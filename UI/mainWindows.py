# coding:utf-8

import json
import sys
import os
import time
# from typing import override
import re
import datetime

from PySide6.QtWidgets import QFileDialog,QTextEdit

from PySide6.QtGui import QTextCursor,QColor, QTextCharFormat
from PySide6.QtCore import (
                            QCoreApplication,
                            QObject
                            , Qt
                            , Signal,
                            QTimer
                        )

from qfluentwidgets import (
                            StateToolTip
                            , InfoBar
                            , InfoBarPosition
                            , InfoBarIcon
                            , MessageBox
                            , FluentIcon
                            , isDarkTheme
                        )


from .config import (
                    Task_list
                    , STR_BOOL
                    , CAPTURE_PARA
                )

from .modelLoad import LoadModelWorker
from .streaming_server import StreamingServerWorker

from .transcribe import (

                        CaptureAudioWorker
                    )

from .fasterGuiIcon import FasterGUIIcon
from .UI_MainWindows import UIMainWin


from .config import ENCODING_DICT

from .util import (
                    outputWithDateTime,
                    HMSToSeconds,
                    MSToSeconds,
                    ServerParameters
                )



import opencc


# =======================================================================================
# SignalStore
# =======================================================================================
class RedirectOutputSignalStore(QObject):
    outputSignal = Signal(str)
    def flush( self ):
        pass
    def fileno( self ):
        return -1
    def write( self, text ):
        if ( not self.signalsBlocked() ):
            self.outputSignal.emit(str(text))


# =======================================================================================
# mainWindows function control class
# =======================================================================================
class MainWindows(UIMainWin):
    """C"""

    # def writeLog(self, text:str):
    #     def go(text:str):
    #         self.log.write(text)
    #     t1 = Thread(target=go, args=(text))
    #     t1.start()

    def __tr(self, text):
        return QCoreApplication.translate(self.__class__.__name__, text)

    log = open(r"./liveasrgui.log" ,"a" ,encoding="utf8", buffering=1)

    def __init__(self):
        # 调用父类初始化
        super().__init__()

        # 重定向输出
        self.redirectErrOutpur = RedirectOutputSignalStore()
        self.redirectErrOutpur.outputSignal.connect(lambda text: self.log.write(text))
        sys.stderr = self.redirectErrOutpur
        sys.stdout = self.redirectErrOutpur

        self.outputWithDateTime = outputWithDateTime

        # 初始化变量
        self.transcribe_thread = None
        self.audio_capture_transcribe_thread = None
        self.loadModelWorker = None
        self.ws_service_thread = None
        self.stateTool = None

        self.tableModel_list = {}
        self.current_result = None
        self.modelRootDir = r"./models"

        # 初始化ASR相关变量
        self.asr = ""  # 用于存储当前识别到的文本
        self.last_displayed_role = None  # 用于跟踪上一次显示的角色
        self.warnings = []
        self.last_displayed_text = ''  # 用于跟踪上一次显示的文本
        self.current_message = ''  # 当前正在显示的消息
        self.full_message = ''  # 完整的消息

        # 连接信号和槽
        self.singleAndSlotProcess()

        if self.page_setting.switchButton_autoLoadModel.isChecked():
            self.onModelLoadClicked()

        self.textOfParentClass()

    def textOfParentClass(self) -> None:
        # to fixed bug of translator
        self.text_home = self.__tr("Home")
        self.text_modelParam = self.__tr("模型参数")
        self.text_server = self.__tr("服务器参数")
        self.text_process = self.__tr("执行转写")
        self.text_setting = self.__tr('设置')



    # ==============================================================================================================
    # 重定向输出到文本框
    # ==============================================================================================================
    def setTextAndMoveCursorToProcessBrowser(self, text:str):
        self.page_process.processResultText.moveCursor(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.MoveAnchor)
        self.page_process.processResultText.insertPlainText(text)

    # ==============================================================================================================
    # 输出重定向，但目前不再进行错误信息重定向，错误信息始终输出到 log 文件
    # ==============================================================================================================
    def redirectOutput(self, target : callable):
        # 重定向输出
        sys.stdout = RedirectOutputSignalStore()
        sys.stdout.outputSignal.connect(target)

    # ==============================================================================================================

    def onModelLoadClicked(self):
        try:
            if hasattr(self, 'SherpaOnnxModel'):
                del self.SherpaOnnxModel
            self.SherpaOnnxModel = None
            self.outputWithDateTime("LoadModel")

            model_param = self.getParam_model()
            for key, value in model_param.items():
                print(f"    -{key}: {value}")

            decoder_model_size_or_path = model_param["decoder_model_size_or_path"]
            encoder_model_size_or_path = model_param["encoder_model_size_or_path"]
            joiner_model_size_or_path = model_param["joiner_model_size_or_path"]
            token_file_size_or_path = model_param["token_file_size_or_path"]
            hotwords_file_path = model_param["hotwords_file_path"]

            if decoder_model_size_or_path == "":
                self.raiseErrorInfoBar(
                                title=self.__tr('加载错误'),
                                content=self.__tr("请检查模型路径，以及模型是否有效，token文件是否存在。"),
                            )
                return

            if os.path.isfile(decoder_model_size_or_path) and os.path.isfile(encoder_model_size_or_path) and os.path.isfile(joiner_model_size_or_path) and os.path.isfile(token_file_size_or_path):
                content = self.__tr("加载本地模型")
            else:
                content = self.__tr("请检查模型文件是否存在")

            infoBar = InfoBar(
                                icon=InfoBarIcon.INFORMATION,
                                title='',
                                content=content,
                                isClosable=False,
                                orient=Qt.Orientation.Vertical,    # vertical layout
                                position=InfoBarPosition.TOP,
                                duration=2000,
                                parent=self
                            )

            infoBar.show()

            param_for_model_load = {
                                    "decoder_model_size_or_path":model_param["decoder_model_size_or_path"],
                                    "encoder_model_size_or_path":model_param["encoder_model_size_or_path"],
                                    "joiner_model_size_or_path":model_param["joiner_model_size_or_path"],
                                    "token_file_size_or_path":model_param["token_file_size_or_path"],
                                    "rule_fsts_file_path":model_param["rule_fsts_file_path"],
                                    "hotwords_file_path":model_param["hotwords_file_path"],
                                    "hotwords_score":model_param["hotwords_score"],
                                    "device":model_param["device"],
                                    "device_index":model_param["device_index"],
                                    "sample_rate":model_param["sample_rate"],
                                    "cpu_threads":model_param["cpu_threads"],
                                    "num_workers":model_param["num_workers"],
                                    "use_endpoint": model_param["use_endpoint"],
                                }

            if hasattr(self, 'loadModelWorker') and self.loadModelWorker is not None:
                self.loadModelWorker.stop()
                self.loadModelWorker.wait()
                self.loadModelWorker = None

            self.loadModelWorker = LoadModelWorker(param_for_model_load, parent=self)
            self.loadModelWorker.setStatusSignal.connect(self.loadModelResult)
            self.loadModelWorker.setStatusSignal.connect(self.setModelStatusLabelTextForAll)
            self.setStateTool(self.__tr("加载模型"), self.__tr("模型加载中，请稍候"), False)
            self.loadModelWorker.start()
        except Exception as e:
            print(f"加载模型时出错: {str(e)}")
            self.raiseErrorInfoBar(
                title=self.__tr("错误"),
                content=self.__tr("加载模型时出错，请检查日志文件。")
            )

    def getParam_model(self) -> dict:
        """
        获取模型参数
        """

        if self.page_model.model_local_RadioButton.isChecked():
            decoder_model_size_or_path = self.page_model.lineEdit_decoder_model_path.text()
            encoder_model_size_or_path = self.page_model.lineEdit_encoder_model_path.text()
            joiner_model_size_or_path = self.page_model.lineEdit_joiner_model_path.text()
            token_file_size_or_path = self.page_model.lineEdit_tokens_file_path.text()
            hotwords_file_path = self.page_model.lineEdit_hotwords_file_path.text()
            rule_fsts_file_path = self.page_model.lineEdit_rule_fsts_file_path.text()
        else:
            pass

        hotwords_score: float = float(self.page_model.LineEdit_hotwords_score.text().replace(" ", ""))
        device: str = self.page_model.device_combox.currentText()
        device_index:str = self.page_model.LineEdit_device_index.text().replace(" ", "")
        device_index = [int(index) for index in device_index.split(",")]
        if len(device_index) == 1:
            device_index = device_index[0]

        compute_type: str = self.page_model.preciese_combox.currentText()
        sample_rate: int = int(self.page_model.preciese_combox.currentText().replace(" ", ""))
        cpu_threads: int = int(self.page_model.LineEdit_cpu_threads.text().replace(" ", ""))
        num_workers: int = int(self.page_model.LineEdit_num_workers.text().replace(" ", ""))
        use_endpoint: bool = self.page_model.switchButton_use_endpoint.isChecked()


        model_dict : dict = {
                    "decoder_model_size_or_path" : decoder_model_size_or_path,
                    "encoder_model_size_or_path" : encoder_model_size_or_path,
                    "joiner_model_size_or_path" : joiner_model_size_or_path,
                    "token_file_size_or_path" : token_file_size_or_path,
                    "rule_fsts_file_path" : rule_fsts_file_path,
                    "hotwords_file_path" : hotwords_file_path,
                    "hotwords_score" : hotwords_score,
                    "device" : device,
                    "device_index" : device_index,
                    "sample_rate" : sample_rate,
                    "cpu_threads" : cpu_threads,
                    "num_workers" : num_workers,
                    "use_endpoint": use_endpoint,

        }

        return model_dict

    def onButtonProcessClicked(self):

        if self.page_process.audio_capture_RadioButton.isChecked():
            self.audioCaptureProcess()

    def audioCaptureProcess(self):

        if  self.audio_capture_transcribe_thread is None:

            self.redirectOutput(self.setTextAndMoveCursorToProcessBrowser)
            self.page_process.processResultText.setText("")
            print("AudioCapture")
            transcribe_params :dict = self.getStreamingServerParam()
            for key, value in transcribe_params.items():
                print(f"    -{key}: {value}")

            if self.SherpaOnnxModel is None:
                print(self.__tr("模型未加载！进程退出"))
                self.audioCaptureOver(None)
                return

            # rate_channel_dType = self.page_process.combox_capture.currentIndex()
            # rate_channel_dType : dict = CAPTURE_PARA[rate_channel_dType]
            # rate = rate_channel_dType["rate"]
            # channels = rate_channel_dType["channel"]
            # dType = rate_channel_dType["dType"]

            self.audio_capture_transcribe_thread = CaptureAudioWorker(transcribeParam=transcribe_params,

                                                                    #   rate = rate
                                                                    #   ,channels = channels
                                                                    #   ,dType = dType,
                                                                      parent = self
                                                        )
            self.audio_capture_transcribe_thread.start()
            self.page_process.button_process.setText(self.__tr("  取消  "))
            self.page_process.button_process.setIcon(":/resource/Image/Cancel_red.svg")
            #self.audio_capture_transcribe_thread.message_received.disconnect()
            self.audio_capture_transcribe_thread.message_received.connect(self.displayMessage)


        else:
            self.audioCaptureOver()
            self.resetButton_process()


    def displayMessage(self, message):
        try:
            message = json.loads(message)
            import cn2an
            message['text'] = cn2an.transform(message['text'], method="cn2an")
            self.asr = f"{message['text']}\n"

            if self.asr != self.full_message and message['text'] != '':
                self.current_message = ''
                self.full_message = self.asr
                # 直接更新文本显示
                self.update_text_browser(self.full_message)

            elif message['text'] == '' and self.full_message != '':
                self.check_warnings()
                self.get_warnings()
                self.asr = ''  # 重置当前发言
                self.warnings = [] # 重置告警列表
                self.last_displayed_text = ''
                self.full_message = ''
        except Exception as e:
            print(f"处理消息时出错: {str(e)}")

    def update_text_browser(self, text):
        # 这个方法用于更新文本显示区域
        try:
            cursor = self.page_process.processResultText.textCursor()
            cursor.movePosition(QTextCursor.End)
            print("TEXT:", text)
            print("text[len(self.last_displayed_text):]:", text[len(self.last_displayed_text):])
            cursor.insertText(text[len(self.last_displayed_text):])  # 只插入新文本
            self.page_process.processResultText.ensureCursorVisible()
            self.last_displayed_text = text  # 更新最后显示的文本
            print('last_displayed_text:', self.last_displayed_text)
        except Exception as e:
            print(f"更新文本显示时出错: {str(e)}")


    def check_warnings(self):
        # 检查告警条件
        pass

    def warning_exists(self, warning_type):
        # 检查特定类型的警告是否已经存在
        return any(warning_type in warning for warning in self.warnings)

    def get_warnings(self):
        # 根据告警级别设置颜色
        for warning in self.warnings:
            color = "black"
            if "一级告警" in warning:
                color = "blue"
            elif "二级告警" in warning:
                color = "orange"
            elif "三级告警" in warning:
                color = "red"
            # 设置富文本格式
            full_warning_message = f"<span style='color: {color};'>{warning}</span><br>\n"
            self.page_process.processResultText.append(full_warning_message)
        return self.warnings


    def resetButton_process(self):
        self.page_process.button_process.setEnabled(True)
        self.page_process.button_process.setText(self.__tr("开始"))
        self.page_process.button_process.setIcon(FasterGUIIcon.PROCESS)


    def audioCaptureOver(self):
        self.audio_capture_transcribe_thread.stop()
        while(self.audio_capture_transcribe_thread.isRunning):
            time.sleep(0.1)
        self.audio_capture_transcribe_thread = None
        self.asr = ""  # 用于存储当前识别到的文本
        self.last_displayed_role = None  # 用于跟踪上一次显示的角色
        self.warnings = []


    #     elif self.audio_capture_transcribe_thread is not None and self.audio_capture_transcribe_thread.isRunning:
    #         # 此处由于输出被重定向只能手动写log文件
    #         dateTime_ = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    #         self.log.write(f"\n=========={dateTime_}==========\n")
    #         self.log.write(f"==========Cancel==========\n")

    #         messageBoxW = MessageBox(
    #                                     self.__tr("取消")
    #                                     , self.__tr("是否取消操作？")
    #                                     , self
    #                                 )

    #         if messageBoxW.exec():
    #             self.page_process.button_process.setEnabled(False)
    #             self.cancelTrancribe()
    #             sys.stdout = self.redirectErrOutpur
    #             self.setStateTool(text=self.__tr("已取消"), status=True)


    def simplifiedAndTraditionalChineseConvert(self, segments, language):
        # 設置轉換器
                    if language == "Auto" or language == "zhs":
                        print(f"convert to Simplified Chinese")
                        print(f"len:{len(segments)}")
                        cc = opencc.OpenCC('t2s')
                    elif language == "zht":
                        print(f"convert to Traditional Chinese")
                        print(f"len:{len(segments)}")
                        cc = opencc.OpenCC('s2t')


    def onButtonStreamingServerClicked(self):

        server_params = self.getStreamingServerParam()
        for key, value in server_params.items():
            print(f"    -{key}: {value}")

        if self.SherpaOnnxModel is None:
            print(self.__tr("模型未加载！进程退出"))

            return

        # 启动WebSocket服务的线程
        self.ws_service_thread = StreamingServerWorker(recognizer=self.SherpaOnnxModel, serverParam=server_params,parent = self)
        self.ws_service_thread.started_server_signal.connect(self.onWebSocketServiceStartedResulted)
        self.setStateTool(self.__tr("启动服务中"), self.__tr("服务启动中，请稍候"), True)
        self.ws_service_thread.start()

    def getStreamingServerParam(self) -> dict:
        """
        get param of server
        """

        host :str= self.page_Server.LineEdit_Server_ip.text().replace(" ", "")
        port :int = int(self.page_Server.LineEdit_Server_port.text().replace(" ", ""))
        nn_pool_size: int = int(self.page_Server.LineEdit_Server_param_nn_pool_size.text().replace(" ", ""))
        max_wait_ms: float = float(self.page_Server.LineEdit_Server_param_max_wait_ms.text().replace(" ", ""))
        max_batch_size: int = int(self.page_Server.LineEdit_Server_param_max_batch_size.text().replace(" ", ""))
        max_message_size: int = int(self.page_Server.LineEdit_Server_param_max_message_size.text().replace(" ", ""))
        max_queue_size: int = int(self.page_Server.LineEdit_Server_param_max_queue_size.text().replace(" ", ""))
        max_active_connections: int = int(self.page_Server.LineEdit_Server_param_max_active_connections.text().replace(" ", ""))


        server_param : dict = {
                    "host" : host,
                    "port" : port,
                    "nn_pool_size" : nn_pool_size,
                    "max_wait_ms" : max_wait_ms,
                    "max_batch_size" : max_batch_size,
                    "max_message_size" : max_message_size,
                    "max_queue_size" : max_queue_size,
                    "max_active_connections" : max_active_connections,

        }


        return server_param


    def setStateTool(self, title:str="", text:str="", status:bool=False):

        if self.stateTool is None:
            self.stateTool = StateToolTip(title, text , self)
            self.stateTool.show()

        else:
            self.stateTool.setContent(text)

        width = self.width()
        self.stateTool.move(width-self.stateTool.width()-30, 45)
        self.stateTool.setState(status)

        if  status:
            self.stateTool = None

    def loadModelResult(self, state:bool):
        try:
            if state:
                self.SherpaOnnxModel = self.loadModelWorker.model
                if self.SherpaOnnxModel is not None:
                    self.setStateTool(text=self.__tr("加载完成"), status=True)
                    self.raiseSuccessInfoBar(
                        title=self.__tr('加载结束'),
                        content=self.__tr("模型加载成功")
                    )
                else:
                    self.setStateTool(text=self.__tr("加载失败"), status=True)
                    self.raiseErrorInfoBar(
                        title=self.__tr("错误"),
                        content=self.__tr("模型加载失败，请检查日志文件。")
                    )
            else:
                self.setStateTool(text=self.__tr("加载失败"), status=True)
                self.raiseErrorInfoBar(
                    title=self.__tr("错误"),
                    content=self.__tr("加载失败，退出并检查 liveasrgui.log 文件可能会获取错误信息。")
                )
        except Exception as e:
            print(f"处理模型加载结果时出错: {str(e)}")
            self.setStateTool(text=self.__tr("加载失败"), status=True)
            self.raiseErrorInfoBar(
                title=self.__tr("错误"),
                content=self.__tr("处理模型加载结果时出错，请检查日志文件。")
            )

    def setModelStatusLabelTextForAll(self, status:bool):

        for page in self.pages:
            try:
                page.setModelStatusLabelText(status)
            except Exception as e:
                pass

    def onWebSocketServiceStartedResulted(self,server_state:bool):
        if server_state and self.stateTool:
            self.raiseSuccessInfoBar(
                                title=self.__tr('服务启动完毕'),
                                content=self.__tr("服务启动完成"))
        try:
            if self.ws_service_thread and self.ws_service_thread.isRunning:
                 self.page_Server.button_sreaming_server.setEnabled(False)  # 禁用按钮
        except Exception:
            pass
        # while(self.ws_service_thread and self.ws_service_thread.isRunning()):
        #     time.sleep(0.3)
        print("WebSocket服务启动完成")

    def getLocalDecoderModelPath(self):
        """
        get path of local model
        """
        options = QFileDialog.Options()
        decoder_model_path  ,_ = QFileDialog.getOpenFileName(self, "选择 ONNX 模型", "", "ONNX Files(*.onnx)", options=options)

        if decoder_model_path:
            self.page_model.lineEdit_decoder_model_path.setText(decoder_model_path)
            self.decoder_model_path = decoder_model_path
            self.modelRootDir = os.path.abspath(os.path.join(decoder_model_path, os.pardir))

    def getLocalEncoderModelPath(self):
        """
        get path of local model
        """

        # encoder_model_path = QFileDialog.getExistingDirectory(self, self.__tr("选择模型文件所在的文件夹"), self.modelRootDir)
        options = QFileDialog.Options()
        encoder_model_path ,_ = QFileDialog.getOpenFileName(self, "选择 ONNX 模型", "", "ONNX Files(*.onnx)", options=options)

        if encoder_model_path:
            self.page_model.lineEdit_encoder_model_path.setText(encoder_model_path)
            self.encoder_model_path = encoder_model_path


    def getLocalJoinerModelPath(self):
        """
        get path of local model
        """
        options = QFileDialog.Options()
        joiner_model_path ,_ = QFileDialog.getOpenFileName(self, "选择 ONNX 模型", "", "ONNX Files(*.onnx)", options=options)

        if joiner_model_path:
            self.page_model.lineEdit_joiner_model_path.setText(joiner_model_path)
            self.joiner_model_path = joiner_model_path


    def getLocalTokenFilePath(self):
        """
        get path of local token file
        """
        # 打开文件选择对话框
        options = QFileDialog.Options()
        token_file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "",
                                                  "Text Files (*.txt)", options=options)
        # token_file_path = QFileDialog.getOpenFileName(self, self.__tr("选择token文件"), self.modelRootDir)

        if token_file_path:
            self.page_model.lineEdit_tokens_file_path.setText(token_file_path)
            self.token_file_path = token_file_path

    def getLocalHotwordsFilePath(self):
        """
        get path of local hotwords file
        """
        # 打开文件选择对话框
        options = QFileDialog.Options()
        hotwords_file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "",
                                                  "Text Files (*.txt)", options=options)

        if hotwords_file_path:
            self.page_model.lineEdit_hotwords_file_path.setText(hotwords_file_path)
            self.hotwords_file_path = hotwords_file_path

    def getLocalrule_fsts_file_Path(self):
        """
        get path of local rule_fsts_file_path
        """
        # 打开文件选择对话框
        options = QFileDialog.Options()
        rule_fsts_file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "",
                                                  "Fst Files (*.fst)", options=options)

        if rule_fsts_file_path:
            self.page_model.lineEdit_rule_fsts_file_path.setText(rule_fsts_file_path)
            self.rule_fsts_file_path = rule_fsts_file_path

    def raiseErrorInfoBar(self, title:str, content:str):
        InfoBar.error(
                        title=title
                        , content=content
                        , isClosable=True
                        , duration=-1
                        , orient=Qt.Orientation.Horizontal
                        , position=InfoBarPosition.TOP
                        # , position='Custom',   # NOTE: use custom info bar manager
                        , parent=self
                    )


    def raiseSuccessInfoBar(self, title:str, content:str):
        InfoBar.success(
                        title=title
                        , content=content
                        , isClosable=True
                        , duration=5000
                        , position=InfoBarPosition.TOP
                        , parent=self
                    )

    # def unloadWhisperModel(self):
    #     """
    #     从内存中卸载模型
    #     """
    #     # 转写正在进行时将会直接退出
    #     if self.SherpaOnnxModel is None:
    #         self.raiseErrorInfoBar(self.__tr("卸载模型失败"), self.__tr("未加载模型"))
    #         return

    #     self.outputWithDateTime("Unload Whisper Model")

    #     if self.transcribe_thread is not None and self.transcribe_thread.isRunning():
    #         # self.transcribe_thread.terminate()
    #         self.raiseErrorInfoBar(self.__tr("模型正在使用"), self.__tr("语音识别正在运行"))
    #         return

    #     if self.current_result is not None and self.page_transcribes.LineEdit_temperature.text().strip() != "0" :

    #         print(f"Temperature: {self.page_transcribes.LineEdit_temperature.text().strip()} and transcript has already been run")
    #         print("Temperature fallback configuration may take effect, that may take crash when unload model from memory!")
    #         messB = MessageBox(self.__tr("警告"), self.__tr("温度不为 \"0\" 且已运行过转写，\n温度回退配置可能会生效，\n从内存中卸载模型可能导致软件崩溃！"),self)
    #         messB.yesButton.setText(self.__tr("继续"))
    #         messB.cancelButton.setText(self.__tr("取消"))
    #         if not messB.exec_():
    #             print("canceled")
    #             return

    #     try:
    #         # self.SherpaOnnxModel.model.to(torch.device("cpu"))
    #         del self.SherpaOnnxModel
    #         self.SherpaOnnxModel = None

    #         del self.loadModelWorker.model
    #         self.loadModelWorker.model = None

    #         self.loadModelWorker = None

    #         self.setModelStatusLabelTextForAll(False)
    #         self.raiseSuccessInfoBar(self.__tr("卸载模型成功"), self.__tr("卸载模型成功"))
    #         print("unload model succeed")

    #     except Exception as e:
    #         print("unload model failed")
    #         print(str(e))
    #         self.raiseErrorInfoBar(self.__tr("卸载模型失败"), self.__tr("卸载模型失败，请在转写之前禁用温度回退配置"))

    #     # 清理缓存



    def singleAndSlotProcess(self):
        """
        process single connect and others
        """
        # TODO: there is too much function be writen in this file,
        # and they are not all must be here,
        # some of them could be in their own class-code file

        try:
            self.page_model.toolPushButton_get_decoder_model_path.clicked.connect(self.getLocalDecoderModelPath)
            self.page_model.toolPushButton_get_encoder_model_path.clicked.connect(self.getLocalEncoderModelPath)
            self.page_model.toolPushButton_get_joiner_model_path.clicked.connect(self.getLocalJoinerModelPath)
            self.page_model.toolPushButton_get_tokens_file_path.clicked.connect(self.getLocalTokenFilePath)
            self.page_model.toolPushButton_get_hotwords_file_path.clicked.connect(self.getLocalHotwordsFilePath)
            self.page_model.toolPushButton_get_rule_fsts_file_path.clicked.connect(self.getLocalrule_fsts_file_Path)

            self.page_model.button_model_loader.clicked.connect(self.onModelLoadClicked)
        except Exception as e:
            print(f"连接模型页面信号失败: {str(e)}")

        try:
            self.page_Server.button_sreaming_server.clicked.connect(self.onButtonStreamingServerClicked)
        except Exception as e:
            print(f"连接服务器页面信号失败: {str(e)}")

        try:
            self.page_process.button_process.clicked.connect(self.onButtonProcessClicked)
            self.page_process.processResultText.textChanged.connect(lambda: self.page_process.processResultText.moveCursor(QTextCursor.MoveOperation.End, mode=QTextCursor.MoveMode.MoveAnchor))
        except Exception as e:
            print(f"连接处理页面信号失败: {str(e)}")

        try:
            self.page_home.itemLabel_sherpa_asr.mainButton.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.page_process))
            self.page_home.itemLabel_sherpa_asr.modelButton.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.page_model))
            self.page_home.itemLabel_sherpa_asr.serverButton.clicked.connect(lambda:self.stackedWidget.setCurrentWidget(self.page_Server))
        except Exception as e:
            print(f"连接主页信号失败: {str(e)}")

    def backupConfigFile(self):
        config_file_path,_ = QFileDialog.getSaveFileName(
                                                            self,
                                                            self.__tr("选择保存位置"),
                                                            r"./",
                                                            "json file(*.json)"
                                                        )
        if not config_file_path:
            return

        self.saveConfig(config_file_path)

        # shutil.copy(config_file_path, config_file_path+".bak")
        self.raiseInfoBar(self.__tr("备份配置文件成功"), self.__tr("配置文件已备份到:\n") + config_file_path)

    def loadBackupConfigFile(self):

        config_file_name, _ = QFileDialog.getOpenFileName(
                                                            self,
                                                            self.__tr("选择配置文件"),
                                                            r"./",
                                                            "json file(*.json)"
                                                        )

        if not config_file_name:
            return

        try:
            self.readConfigJson(config_file_path=config_file_name)
            self.setConfig()
            self.raiseSuccessInfoBar(self.__tr("加载配置文件成功"), self.__tr("配置文件已加载:\n") + config_file_name)

        except Exception as e:
            self.raiseErrorInfoBar(self.__tr("加载配置文件失败"), self.__tr("配置文件加载失败:\n") + str(e))
            print(str(e))



    def raiseInfoBar(self, title:str, content:str ):
        InfoBar.info(
                title=title
                , content=content
                , isClosable=False
                , duration=2000
                , position=InfoBarPosition.TOP_RIGHT
                , parent=self
            )

    def closeEvent(self, event) -> None:
        """
        点击窗口关闭按钮时的事件响应
        """
        messageBoxW = MessageBox(self.__tr('退出'), self.__tr("是否要退出程序？"), self)
        if messageBoxW.exec():
            outputWithDateTime("Exit")

            # 停止所有正在运行的线程
            if self.audio_capture_transcribe_thread is not None:
                self.audio_capture_transcribe_thread.stop()
                self.audio_capture_transcribe_thread.wait()

            if self.ws_service_thread is not None and self.ws_service_thread.isRunning:
                self.ws_service_thread.requestInterruption()
                self.ws_service_thread.stop()
                self.ws_service_thread.wait()

            if self.loadModelWorker is not None:
                self.loadModelWorker.stop()
                self.loadModelWorker.wait()

            if self.page_setting.switchButton_saveConfig.isChecked():
                self.saveConfig(config_file_name=r'./GUIConfig.json')

            if self.page_setting.switchButton_autoClearTempFiles.isChecked():
                try:
                    temp_dir = os.path.abspath(r"./temp")
                    # 检查临时目录是否存在，如果不存在则创建
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                        print("created temp directory")

                    temp_list = os.listdir(temp_dir)
                    if len(temp_list) > 0:
                        temp_cmd = temp_dir + "\\" + "*.srt"
                        os.system(f"del {temp_cmd}")
                        print("cleared temp files")
                    else:
                        print("no temp files to clear")
                except Exception as e:
                    print(str(e))

            # 退还系统错误输出和标准输出
            sys.stderr = sys.__stderr__
            sys.stdout = sys.__stdout__

            # 关闭日志文件 结束全部流
            self.log.close()

            if hasattr(self, 'SherpaOnnxModel'):
                del self.SherpaOnnxModel

            # 接受退出事件，程序正常退出
            event.accept()
        else:
            event.ignore()

    def saveConfig(self, config_file_name: str = ""):

        if config_file_name == "":
            return

        outputWithDateTime("SaveConfigFile")
        model_param = self.page_model.getParam()
        setting_param = self.page_setting.getParam()
        server_param = self.page_Server.getParam()

        config_json = {
                        "theme":"dark" if isDarkTheme() else "light",
                        "model_param" : model_param,
                        "server_param": server_param,
                        "setting":setting_param,

                    }

        with open(os.path.abspath(config_file_name),'w',encoding='utf8')as fp:
            json.dump(
                        config_json,
                        fp,
                        ensure_ascii=False,
                        indent=4
                    )

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.stateTool is not None:
            width_tool = self.stateTool.width()
            width = self.width()
            self.stateTool.move(width-width_tool-30, 45)
        return
