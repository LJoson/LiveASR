# coding:utf-8

# from threading import Thread
from concurrent import futures
import os
from typing import List
import time
import codecs
import torch
import numpy as np
import json
import hashlib

import asyncio
import sys

try:
    import sounddevice as sd
except ImportError:
    print("Please install sounddevice first. You can use")
    print()
    print("  pip install sounddevice")
    print()
    print("to install it")
    sys.exit(-1)

try:
    import websockets
except ImportError:
    print("please run:")
    print("")
    print("  pip install websockets")
    print("")
    print("before you run this script")
    print("")
    sys.exit(-1)


from PySide6.QtCore import (QThread, Signal)

from .config import (
                    Language_dict
                    , SUBTITLE_FORMAT
                    , Language_without_space
                )

from .util import (
                    secondsToHMS,
                    ServerParameters
                )
# from .modelLoad import ( modelParamDict
# )
from .config import ENCODING_DICT, Task_list



class CaptureAudioWorker(QThread):
    # Signal_process_over = Signal(np.ndarray)
    message_received = Signal(str)

    def __init__(
            self,
            # rate: int ,
            # channels :int,
            # dType : int,
            transcribeParam: ServerParameters,
            parent=None
    ):
        super().__init__(parent=parent)
        self.isRunning = False
        # self.rate = rate
        self.channels = 1
        # self.dType = dType
        # self.is_running = False
        self.server_port = transcribeParam["port"]
        self.server_addr = transcribeParam["host"]
        self.sample_rate: int = 16000
        self.last_message = ""

    async def inputstream_generator(self):
        """Generator that yields blocks of input data as NumPy arrays.

        See https://python-sounddevice.readthedocs.io/en/0.4.6/examples.html#creating-an-asyncio-generator-for-audio-blocks
        """
        q_in = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))

        devices = sd.query_devices()
        print(devices)
        default_input_device_idx = sd.default.device[0]
        print(f'Use default device: {devices[default_input_device_idx]["name"]}')
        print()
        print("Started! Please speak")

        stream = sd.InputStream(
            callback=callback,
            channels=self.channels,
            dtype="float32",
            samplerate=self.sample_rate,
            blocksize=int(0.05 * 16000),  # 0.05 seconds
        )
        with stream:
            while True:
                indata, status = await q_in.get()
                yield indata, status


    # async def receive_results(self,socket: websockets.WebSocketServerProtocol):
        # last_message = ""
        # async for message in socket:
        #     if message != "Done!":
        #         if last_message != message:
        #             last_message = message

        #             # if last_message:
        #                 # 将JSON字符串转换为Python字典
        #             message_dict = json.loads(last_message)
        #                 # print(message_dict)

        #                 # 访问字典中的中文字段
        #             result_text = message_dict["text"]
        #                 # 打印中文
        #             print(result_text)
        #             # result_text = message_dict.get("text", "")
        #             self.message_received.emit(result_text)
        #     else:
        #         last_message = json.loads(last_message)
        #         self.message_received.emit(last_message)
        #         break
        #     return last_message

    async def receive_results(self,socket: websockets.WebSocketServerProtocol):
        last_message = {""}
        async for message in socket:
            if not self.isRunning:
                break
            if message != "Done!":
                if last_message != message:
                    last_message = message
                    if last_message:
                        try:
                            # 确保消息是有效的JSON
                            json.loads(last_message)
                            # 使用QMetaObject.invokeMethod确保在主线程中发送信号
                            self.message_received.emit(last_message)
                        except json.JSONDecodeError:
                            print("Invalid JSON message received")
            else:
                try:
                    last_message = json.loads(last_message)
                    return last_message
                except json.JSONDecodeError:
                    print("Invalid JSON message received")
                    return None

    async def start_input(self):
        try:
            async with websockets.connect(
                f"ws://{self.server_addr}:{self.server_port}"
            ) as websocket:
                receive_task = asyncio.create_task(self.receive_results(websocket))
                try:
                    async for indata, status in self.inputstream_generator():
                        if not self.isRunning:
                            break
                        if status:
                            print(status)
                        indata = indata.reshape(-1)
                        indata = np.ascontiguousarray(indata)
                        await websocket.send(indata.tobytes())
                except Exception as e:
                    print(f"Error in audio input: {str(e)}")
                finally:
                    await receive_task
        except Exception as e:
            print(f"Connection error: {str(e)}")

    def run(self):
        self.isRunning = True
        try:
            # 确保创建临时目录
            temp_path = os.path.abspath(r"./temp")
            if not os.path.exists(temp_path):
                try:
                    os.makedirs(temp_path)
                except Exception as e:
                    print(f"Error creating temp directory: {str(e)}")

            asyncio.run(self.start_input())
        except Exception as e:
            print(f"Error in run: {str(e)}")
        finally:
            self.isRunning = False

    def stop(self):
        self.isRunning = False
        try:
            self.quit()
        except Exception as e:
            print(f"Error in stop: {str(e)}")

    def check_message(self):
        if self.last_message and not self.message_received.is_empty():
            self.emit_warning("消息不完整")
            # self.timer.stop()

    def emit_warning(self, warning_message):
        print(warning_message)

