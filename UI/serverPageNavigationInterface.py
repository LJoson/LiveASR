# coding:utf-8

from PySide6.QtCore import QCoreApplication,Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
                                QGridLayout
                                , QHBoxLayout
                                ,QVBoxLayout,
                            )

from qfluentwidgets import (
                                SwitchButton
                                , LineEdit
                                , ComboBox
                                , TitleLabel
                                , DoubleSpinBox
                                ,PrimaryPushButton
                                ,FluentIcon
                            )

from .navigationInterface import NavigationBaseInterface
from .paramItemWidget import ParamWidget
from .style_sheet import StyleSheet

class ServerNavigationInterface(NavigationBaseInterface):
    def __tr(self, text):
        return QCoreApplication.translate(self.__class__.__name__, text)

    def __init__(self, parent=None):
        super().__init__(
                            title = self.__tr("服务器参数配置")
                            , subtitle = self.__tr("转写服务及参数配置")
                            , parent = parent
                        )

        self.setupUI()
        # self.SignalAndSlotConnect()
        StyleSheet.TRANSCRIBEPAGEINTERFACE.apply(self.view)

    def setupUI(self):

        self.layout_button_streaming_server = QVBoxLayout()
        # self.button_sreaming_server = PushButton()
        self.button_sreaming_server = PrimaryPushButton(self)

        self.button_sreaming_server.setText(self.__tr("启动转写服务"))
        self.button_sreaming_server.setFixedHeight(65)
        self.button_sreaming_server.setFixedWidth(195)
        font = QFont("Segoe UI", 15)
        font.setBold(True)

        self.button_sreaming_server.setFont(font)

        self.button_sreaming_server.setIcon(FluentIcon.PLAY)
        self.button_sreaming_server.setObjectName("buttonStreamingServer")


        self.layout_button_streaming_server.addWidget(self.button_sreaming_server)
        self.layout_button_streaming_server.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.addLayout(self.layout_button_streaming_server)

        self.titleLabel_Server= TitleLabel(self.__tr("转写服务参数"))
        self.addWidget(self.titleLabel_Server)
        # ------------------------------------------------------------------------------------------------------------------------------------

        GridLayout_Server_param = QGridLayout()
        self.GridLayout_Server_param = GridLayout_Server_param
        GridLayout_Server_param.setContentsMargins(10,0,10,0)
        GridLayout_Server_param.setSpacing(0)

        # ------------------------------------------------------------------------------------------------------------------------------------

        self.LineEdit_Server_ip = LineEdit()
        self.LineEdit_Server_ip.setText("localhost")

        self.Server_param_ip_param_widget = ParamWidget(self.__tr("IP"),
                                                            self.__tr("转写服务IP地址。"),
                                                            self.LineEdit_Server_ip
                                                        )

        self.GridLayout_Server_param.addWidget(self.Server_param_ip_param_widget, 0, 0)
        # ------------------------------------------------------------------------------------------------------------------------------------

        self.LineEdit_Server_port = LineEdit()
        self.LineEdit_Server_port.setText("5000")

        self.Server_param_port_param_widget = ParamWidget(self.__tr("port"),
                                                            self.__tr("转写服务监听的端口号。"),
                                                            self.LineEdit_Server_port
                                                        )

        self.GridLayout_Server_param.addWidget(self.Server_param_port_param_widget, 1, 0)
        # ------------------------------------------------------------------------------------------------------------------------------------

        self.LineEdit_Server_param_nn_pool_size = LineEdit()
        self.LineEdit_Server_param_nn_pool_size.setText("1")
        # self.doubleSpin_Server_param_nn_pool_size.setSuffix("%")

        self.Server_param_nn_pool_size_param_widget = ParamWidget(self.__tr("nn_pool_size"),
                                                            self.__tr("负责神经网络计算和解码的线程池中的线程数。"),
                                                            self.LineEdit_Server_param_nn_pool_size
                                                        )

        self.GridLayout_Server_param.addWidget(self.Server_param_nn_pool_size_param_widget, 2, 0)

        # -------------------------------------------------------------------------------------------------------------------------------------------
        self.LineEdit_Server_param_max_batch_size = LineEdit()
        self.LineEdit_Server_param_max_batch_size.setText("3")

        self.Server_param_max_batch_size_param_widget = ParamWidget(self.__tr("max_wait_ms"),
                                                                        self.__tr("构建一个`batch_size`大小的批次，最大等待时间（以毫秒为单位）"),
                                                                        self.LineEdit_Server_param_max_batch_size
                                                                    )

        self.GridLayout_Server_param.addWidget(self.Server_param_max_batch_size_param_widget, 3, 0)
        # -------------------------------------------------------------------------------------------------------------------------------------------

        self.LineEdit_Server_param_max_wait_ms = LineEdit()
        self.LineEdit_Server_param_max_wait_ms.setText("10")

        self.Server_param_max_wait_ms_param_widget = ParamWidget(self.__tr("max_batch_size"),
                                                                        self.__tr("推理的最大批次大小。"),
                                                                        self.LineEdit_Server_param_max_wait_ms
                                                                    )
        self.GridLayout_Server_param.addWidget(self.Server_param_max_wait_ms_param_widget, 4, 0)

        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.LineEdit_Server_param_max_message_size = LineEdit()
        self.LineEdit_Server_param_max_message_size.setText("1048576")

        self.Server_param_max_message_size_param_widget = ParamWidget(self.__tr("max_message_size"),
                                                                            self.__tr("每个消息的最大大小（以字节为单位）。建议值1048576"),
                                                                            self.LineEdit_Server_param_max_message_size
                                                                        )

        self.GridLayout_Server_param.addWidget(self.Server_param_max_message_size_param_widget, 5, 0)

        # ------------------------------------------------------------------------------------------------------------------------------------------------

        self.LineEdit_Server_param_max_queue_size = LineEdit()
        self.LineEdit_Server_param_max_queue_size.setText("32")

        self.Server_param_max_queue_size_param_widget = ParamWidget(self.__tr("max_queue_size"),
                                                                    self.__tr("每个连接的消息队列中的最大消息数。"),
                                                                    self.LineEdit_Server_param_max_queue_size
                                                                )

        self.GridLayout_Server_param.addWidget(self.Server_param_max_queue_size_param_widget, 6,0)


        # -------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.LineEdit_Server_param_max_active_connections = LineEdit()
        self.LineEdit_Server_param_max_active_connections.setText("200")

        self.Server_param_max_active_connections_param_widget = ParamWidget(self.__tr("max_active_connections"),
                                                                self.__tr("最大活动连接数。一旦活动客户端数量达到此限制，服务器将拒绝接受新连接。"),
                                                                self.LineEdit_Server_param_max_active_connections
                                                            )
        self.GridLayout_Server_param.addWidget(self.Server_param_max_active_connections_param_widget , 7, 0)

        # ----------------------------------------------------------------------------------------------------------------------
        self.addLayout(GridLayout_Server_param)


        # ================================================================================================================================================================
        # self.titleLabel_HuggingFace = TitleLabel(self.__tr("huggingface 参数"))
        # self.addWidget(self.titleLabel_HuggingFace )
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # GridLayout_speakerDiarize_param = QGridLayout()
        # self.GridLayout_speakerDiarize_param = GridLayout_speakerDiarize_param
        # GridLayout_speakerDiarize_param.setContentsMargins(10,10,10,10)
        # self.addLayout(self.GridLayout_speakerDiarize_param)


    # def SignalAndSlotConnect(self):
    #     self.Server_check_switchButton.checkedChanged.connect(self.setServerUILayout)


    # def setServerUILayout(self):
    #     num_widgets_layout = self.GridLayout_Server_param.count()

    #     for i in range(num_widgets_layout):
    #         widget = self.GridLayout_Server_param.itemAt(i).widget()
    #         widget.setEnabled(self.Server_check_switchButton.isChecked())

    def getParam(self):
        param = {}
        # param["use_Server"] = self.Server_check_switchButton.isChecked()
        param["port"] = self.LineEdit_Server_port.text().strip()
        param["nn_pool_size"] = self.LineEdit_Server_param_nn_pool_size.text().strip()
        param["max_batch_size"] = self.LineEdit_Server_param_max_batch_size.text().strip()
        param["max_message_size"] = self.LineEdit_Server_param_max_message_size.text().strip()
        param["max_wait_ms"] = self.LineEdit_Server_param_max_wait_ms.text().strip()
        param["max_queue_size"] = self.LineEdit_Server_param_max_queue_size.text().strip()
        param["max_active_connections"] = self.LineEdit_Server_param_max_active_connections.text().strip()

        return param

    def setParam(self, param:dict):

        # self.Server_check_switchButton.setChecked(param["use_Server"])
        self.LineEdit_Server_port.setText(param["port"] )
        self.LineEdit_Server_param_nn_pool_size.setText(param["nn_pool_size"] )
        self.LineEdit_Server_param_max_batch_size.setText(param["max_batch_size"])
        self.LineEdit_Server_param_max_message_size.setText(param["max_message_size"])
        self.LineEdit_Server_param_max_wait_ms.setText(param["max_wait_ms"])
        self.LineEdit_Server_param_max_queue_size.setText(param["max_queue_size"])
        self.LineEdit_Server_param_max_active_connections.setText(param["max_active_connections"])
