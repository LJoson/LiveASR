#!/usr/bin/env python3
# Copyright      2024  LJoson.
#


import argparse
import asyncio
import http
import json
import logging
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import sherpa_onnx
import websockets

from typing import Set
from .http_server import HttpServer
from PySide6.QtCore import QThread, Signal
from .util import ServerParameters


def setup_logger(
    log_filename: str,
    log_level: str = "info",
    use_console: bool = True,
) -> None:
    """Setup log level.

    Args:
      log_filename:
        The filename to save the log.
      log_level:
        The log level to use, e.g., "debug", "info", "warning", "error",
        "critical"
      use_console:
        True to also print logs to console.
    """
    now = datetime.now()
    date_time = now.strftime("%Y-%m-%d-%H-%M-%S")
    formatter = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s"
    log_filename = f"{log_filename}-{date_time}.txt"

    Path(log_filename).parent.mkdir(parents=True, exist_ok=True)

    level = logging.ERROR
    if log_level == "debug":
        level = logging.DEBUG
    elif log_level == "info":
        level = logging.INFO
    elif log_level == "warning":
        level = logging.WARNING
    elif log_level == "critical":
        level = logging.CRITICAL

    logging.basicConfig(
        filename=log_filename,
        format=formatter,
        level=level,
        filemode="w",
    )
    if use_console:
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(logging.Formatter(formatter))
        logging.getLogger("").addHandler(console)
def format_timestamps(timestamps: List[float]) -> List[str]:
    return ["{:.3f}".format(t) for t in timestamps]


class StreamingServerWorker(QThread):
    started_server_signal = Signal(bool)

    def __init__(
        self,
        recognizer: sherpa_onnx.OnlineRecognizer,
        serverParam: ServerParameters,
        parent = None,

    ):
        """
        Args:
          recognizer:
            An instance of online recognizer.
          nn_pool_size:
            Number of threads for the thread pool that is responsible for
            neural network computation and decoding.
          max_wait_ms:
            Max wait time in milliseconds in order to build a batch of
            `batch_size`.
          max_batch_size:
            Max batch size for inference.
          max_message_size:
            Max size in bytes per message.
          max_queue_size:
            Max number of messages in the queue for each connection.
          max_active_connections:
            Max number of active connections. Once number of active client
            equals to this limit, the server refuses to accept new connections.
          beam_search_params:
            Dictionary containing all the parameters for beam search.
          online_endpoint_config:
            Config for endpointing.
          doc_root:
            Path to the directory where files like index.html for the HTTP
            server locate.
          certificate:
            Optional. If not None, it will use secure websocket.
            You can use ./web/generate-certificate.py to generate
            it (the default generated filename is `cert.pem`).
        """
        super().__init__(parent=parent)
        self.isRunning = False
        self.recognizer = recognizer
        self.port = serverParam["port"]

        self.certificate = ""
        self.http_server = HttpServer("./web")

        self.nn_pool_size = serverParam["nn_pool_size"]
        self.nn_pool = ThreadPoolExecutor(
            max_workers=serverParam["nn_pool_size"],
            thread_name_prefix="nn",
        )

        self.stream_queue = asyncio.Queue()

        self.max_wait_ms = serverParam["max_wait_ms"]
        self.max_batch_size = serverParam["max_batch_size"]
        self.max_message_size = serverParam["max_message_size"]
        self.max_queue_size = serverParam["max_queue_size"]
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.max_active_connections = serverParam["max_active_connections"]

        self.current_active_connections = 0

        self.sample_rate = int(recognizer.config.feat_config.sampling_rate)

    async def stream_consumer_task(self):
        """This function extracts streams from the queue, batches them up, sends
        them to the neural network model for computation and decoding.
        """
        while self.isRunning:
            if self.stream_queue.empty():
                await asyncio.sleep(self.max_wait_ms / 1000)
                continue

            batch = []
            try:
                while len(batch) < self.max_batch_size:
                    item = self.stream_queue.get_nowait()

                    assert self.recognizer.is_ready(item[0])

                    batch.append(item)
            except asyncio.QueueEmpty:
                pass
            stream_list = [b[0] for b in batch]
            future_list = [b[1] for b in batch]

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                self.nn_pool,
                self.recognizer.decode_streams,
                stream_list,
            )

            for f in future_list:
                self.stream_queue.task_done()
                f.set_result(None)
            if not self.isRunning:
                break
    async def compute_and_decode(
        self,
        stream: sherpa_onnx.OnlineStream,
    ) -> None:
        """Put the stream into the queue and wait it to be processed by the
        consumer task.

        Args:
          stream:
            The stream to be processed. Note: It is changed in-place.
        """
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        await self.stream_queue.put((stream, future))
        await future

    async def process_request(
        self,
        path: str,
        request_headers: websockets.Headers,
    ) -> Optional[Tuple[http.HTTPStatus, websockets.Headers, bytes]]:
        if "sec-websocket-key" not in request_headers:
            # This is a normal HTTP request
            if path == "/":
                path = "/index.html"

            if path in ("/upload.html", "/offline_record.html"):
                response = r"""
<!doctype html><html><head>
<title>Speech recognition with next-gen Kaldi</title><body>
<h2>Only /streaming_record.html is available for the streaming server.<h2>
<br/>
<br/>
Go back to <a href="/streaming_record.html">/streaming_record.html</a>
</body></head></html>
"""
                found = True
                mime_type = "text/html"
            else:
                found, response, mime_type = self.http_server.process_request(path)

            if isinstance(response, str):
                response = response.encode("utf-8")

            if not found:
                status = http.HTTPStatus.NOT_FOUND
            else:
                status = http.HTTPStatus.OK
            header = {"Content-Type": mime_type}
            return status, header, response

        if self.current_active_connections < self.max_active_connections:
            self.current_active_connections += 1
            return None

        # Refuse new connections
        status = http.HTTPStatus.SERVICE_UNAVAILABLE  # 503
        header = {"Hint": "The server is overloaded. Please retry later."}
        response = b"The server is busy. Please retry later."

        return status, header, response

    async def start_server(self,):
        tasks = []

        for i in range(self.nn_pool_size):
            tasks.append(asyncio.create_task(self.stream_consumer_task()))

        if self.certificate:
            logging.info(f"Using certificate: {self.certificate}")
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(self.certificate)
        else:
            ssl_context = None
            logging.info("No certificate provided")
        try:
            async with websockets.serve(
                self.handle_connection,
                host="",
                port=self.port,
                max_size=self.max_message_size,
                max_queue=self.max_queue_size,
                process_request=self.process_request,
                ssl=ssl_context,
            ):
                ip_list = ["localhost"]
                if ssl_context:
                    ip_list += ["0.0.0.0", "127.0.0.1"]
                    ip_list.append(socket.gethostbyname(socket.gethostname()))
                proto = "http://" if ssl_context is None else "https://"
                s = "Please visit one of the following addresses:\n\n"
                for p in ip_list:
                    s += "  " + proto + p + f":{self.port}" "\n"

                if not ssl_context:
                    s += "\nSince you are not providing a certificate, you cannot "
                    s += "use your microphone from within the browser using "
                    s += "public IP addresses. Only localhost can be used."
                    s += "You also cannot use 0.0.0.0 or 127.0.0.1"

                logging.info(s)
                print("启动中....")
                self.started_server_signal.emit(True)
                await asyncio.Future()  # run forever
                while self.isRunning:  # 持续检查 isRunning 标志
                    await asyncio.sleep(1)  # 短暂的休眠，避免密集循环
        finally:
            self.started_server_signal.emit(False)
            self.isRunning = False

        await asyncio.gather(*tasks)  # not reachable

    async def handle_connection(
        self,
        socket: websockets.WebSocketServerProtocol,
    ):
        """Receive audio samples from the client, process it, and send
        decoding result back to the client.

        Args:
          socket:
            The socket for communicating with the client.
        """
        if len(self.clients) < self.max_active_connections:
            self.clients.add(socket)
        try:
            await self.handle_connection_impl(socket)
        except websockets.exceptions.ConnectionClosedError:
            logging.info(f"{socket.remote_address} disconnected")
        finally:
            # Decrement so that it can accept new connections
            self.current_active_connections -= 1
            self.clients.remove(socket)

            logging.info(
                f"Disconnected: {socket.remote_address}. "
                f"Number of connections: {self.current_active_connections}/{self.max_active_connections}"  # noqa
            )

    async def handle_connection_impl(
        self,
        socket: websockets.WebSocketServerProtocol,
    ):
        """Receive audio samples from the client, process it, and send
        decoding result back to the client.

        Args:
          socket:
            The socket for communicating with the client.
        """
        logging.info(
            f"Connected: {socket.remote_address}. "
            f"Number of connections: {self.current_active_connections}/{self.max_active_connections}"  # noqa
        )

        stream = self.recognizer.create_stream()
        segment = 0
         # 创建一个集合来存储所有连接的客户端
        clients = set()
        clients.add(socket)
        while True:
            samples = await self.recv_audio_samples(socket)
            if samples is None:
                break

            # TODO(fangjun): At present, we assume the sampling rate
            # of the received audio samples equal to --sample-rate
            stream.accept_waveform(sample_rate=self.sample_rate, waveform=samples)

            while self.recognizer.is_ready(stream):
                await self.compute_and_decode(stream)
                result = self.recognizer.get_result(stream)

                message = {
                    "text": result,
                    "segment": segment,
                }
                if self.recognizer.is_endpoint(stream):
                    self.recognizer.reset(stream)
                    segment += 1
                # 广播消息给所有连接的客户端
                await self.broadcast(message)
                # await socket.send(json.dumps(message))


        tail_padding = np.zeros(int(self.sample_rate * 0.3)).astype(np.float32)
        stream.accept_waveform(sample_rate=self.sample_rate, waveform=tail_padding)
        stream.input_finished()
        while self.recognizer.is_ready(stream):
            await self.compute_and_decode(stream)

        result = self.recognizer.get_result(stream)

        message = {
            "text": result,
            "segment": segment,
        }
        # 广播消息给所有连接的客户端
        await self.broadcast(message)
        # await socket.send(json.dumps(message))

    async def broadcast(self, message: str):
        for client in self.clients:
            try:
                await client.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                # 如果客户端已经断开连接，则从列表中移除
                self.clients.remove(client)

    async def recv_audio_samples(
        self,
        socket: websockets.WebSocketServerProtocol,
    ) -> Optional[np.ndarray]:
        """Receive a tensor from the client.

        Each message contains either a bytes buffer containing audio samples
        in 16 kHz or contains "Done" meaning the end of utterance.

        Args:
          socket:
            The socket for communicating with the client.
        Returns:
          Return a 1-D np.float32 tensor containing the audio samples or
          return None.
        """
        message = await socket.recv()
        if message == "Done":
            return None

        return np.frombuffer(message, dtype=np.float32)



    def run(self):
        self.isRunning = True
        log_filename = "log/log-streaming-server"
        setup_logger(log_filename)
        # 启动WebSocket服务
        asyncio.run(self.start_server())

    def stop(self):
        self.isRunning = False



