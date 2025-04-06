# coding:utf-8

from PySide6.QtCore import (QCoreApplication, Qt)
from PySide6.QtGui import QFont

from PySide6.QtWidgets import (
                                QCompleter,
                                QGridLayout,
                                QHBoxLayout,
                                QLabel,
                                QStyle,
                                QVBoxLayout,
                                QSplitter
                            )

from qfluentwidgets import (
                            ComboBox,
                            RadioButton,
                            PushButton,
                            ToolButton,
                            EditableComboBox,
                            LineEdit ,
                            SwitchButton,
                            FluentIcon,
                            PrimaryPushButton,

                        )

from .navigationInterface import NavigationBaseInterface
from .paramItemWidget import ParamWidget
from .style_sheet import StyleSheet

from .config import (
                    Preciese_list
                    , Model_names
                    , Device_list
                )

class ModelNavigationInterface(NavigationBaseInterface):
    def __tr(self, text):
        return QCoreApplication.translate(self.__class__.__name__, text)

    def __init__(self, parent=None):

        super().__init__(
                        title=self.__tr("模型配置")
                        , subtitle=self.__tr('加载本地模型以及参数配置')
                        , parent=parent
                    )

        self.model_names = Model_names
        self.device_list = Device_list
        self.preciese_list = Preciese_list

        self.setObjectName('modelNavigationInterface')
        self.setupUI()

        # StyleSheet.MODELLOAD.apply(self.button_model_loader)

        self.SignalAndSlotConnect()

    def SignalAndSlotConnect(self):
        self.model_local_RadioButton.clicked.connect(self.setModelLocationLayout)
        # self.model_online_RadioButton.clicked.connect(self.setModelLocationLayout)

    def setModelLocationLayout(self):
        num_widgets_layout = self.hBoxLayout_local_model.count()

        for i in range(num_widgets_layout):
            widget = self.hBoxLayout_local_model.itemAt(i).widget()
            widget.setEnabled(self.model_local_RadioButton.isChecked())


    def setupUI(self):
        self.layout_button_model_loader = QVBoxLayout()
        # self.button_model_loader = PushButton()
        self.button_model_loader = PrimaryPushButton(self)

        self.button_model_loader.setText(self.__tr("加载模型"))
        self.button_model_loader.setFixedHeight(65)
        self.button_model_loader.setFixedWidth(195)
        font = QFont("Segoe UI", 15)
        font.setBold(True)

        self.button_model_loader.setFont(font)

        self.button_model_loader.setIcon(FluentIcon.PLAY)
        self.button_model_loader.setObjectName("buttonModelLodar")


        self.layout_button_model_loader.addWidget(self.button_model_loader)
        self.layout_button_model_loader.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.addLayout(self.layout_button_model_loader)


        # ==========================================================================================================

        model_local_RadioButton = RadioButton()
        model_local_RadioButton.setChecked(True)
        model_local_RadioButton.setText(self.__tr("使用本地模型"))
        # model_local_RadioButton.setToolTip(self.__tr("本地模型需使用经过 CTranslate2 转换工具，从 OpenAI 模型格式转换而来的模型"))
        self.model_local_RadioButton = model_local_RadioButton
        self.addWidget(self.model_local_RadioButton)

        # ==========================================================================================================

        self.hBoxLayout_local_model = QHBoxLayout()
        self.addLayout(self.hBoxLayout_local_model)

        # 使用decoder模型时添加相关控件到布局
        self.decoder_model_path = QLabel()
        self.decoder_model_path.setText(self.__tr("decoder模型"))
        self.decoder_model_path.setObjectName("LabelModelPath")
        self.decoder_model_path.setStyleSheet("#LabelModelPath{ background : rgba(0, 128, 0, 120); }")
        self.lineEdit_decoder_model_path = LineEdit()
        self.lineEdit_decoder_model_path.setClearButtonEnabled(True)
        self.toolPushButton_get_decoder_model_path = ToolButton()
        self.toolPushButton_get_decoder_model_path.setIcon(self.style().standardPixmap(QStyle.StandardPixmap.SP_DirOpenIcon))

        self.hBoxLayout_local_model.addWidget(self.decoder_model_path)
        self.hBoxLayout_local_model.addWidget(self.lineEdit_decoder_model_path)
        self.hBoxLayout_local_model.addWidget(self.toolPushButton_get_decoder_model_path)


        # ==========================================================================================================

        self.hBoxLayout_local_model = QHBoxLayout()
        self.addLayout(self.hBoxLayout_local_model)

        # 使用encoder模型时添加相关控件到布局
        self.encoder_model_path = QLabel()
        self.encoder_model_path.setText(self.__tr("encoder 模型"))
        self.encoder_model_path.setObjectName("LabelModelPath")
        self.encoder_model_path.setStyleSheet("#LabelModelPath{ background : rgba(0, 128, 0, 120); }")
        self.lineEdit_encoder_model_path = LineEdit()
        self.lineEdit_encoder_model_path.setClearButtonEnabled(True)
        self.toolPushButton_get_encoder_model_path = ToolButton()
        self.toolPushButton_get_encoder_model_path.setIcon(self.style().standardPixmap(QStyle.StandardPixmap.SP_DirOpenIcon))

        self.hBoxLayout_local_model.addWidget(self.encoder_model_path)
        self.hBoxLayout_local_model.addWidget(self.lineEdit_encoder_model_path)
        self.hBoxLayout_local_model.addWidget(self.toolPushButton_get_encoder_model_path)

        # ==========================================================================================================

        self.hBoxLayout_local_model = QHBoxLayout()
        self.addLayout(self.hBoxLayout_local_model)

        # 使用joiner模型时添加相关控件到布局
        self.joiner_model_path = QLabel()
        self.joiner_model_path.setText(self.__tr("joiner 模型"))
        self.joiner_model_path.setObjectName("LabelModelPath")
        self.joiner_model_path.setStyleSheet("#LabelModelPath{ background : rgba(0, 128, 0, 120); }")
        self.lineEdit_joiner_model_path = LineEdit()
        self.lineEdit_joiner_model_path.setClearButtonEnabled(True)
        self.toolPushButton_get_joiner_model_path = ToolButton()
        self.toolPushButton_get_joiner_model_path.setIcon(self.style().standardPixmap(QStyle.StandardPixmap.SP_DirOpenIcon))

        self.hBoxLayout_local_model.addWidget(self.joiner_model_path)
        self.hBoxLayout_local_model.addWidget(self.lineEdit_joiner_model_path)
        self.hBoxLayout_local_model.addWidget(self.toolPushButton_get_joiner_model_path)

        # ==========================================================================================================

        self.hBoxLayout_local_model = QHBoxLayout()
        self.addLayout(self.hBoxLayout_local_model)

        # 使用 tokens 添加相关控件到布局
        self.tokens_file_path = QLabel()
        self.tokens_file_path.setText(self.__tr("tokens"))
        self.tokens_file_path.setObjectName("LabelModelPath")
        self.tokens_file_path.setStyleSheet("#LabelModelPath{ background : rgba(0, 128, 0, 120); }")
        self.lineEdit_tokens_file_path = LineEdit()
        self.lineEdit_tokens_file_path.setClearButtonEnabled(True)
        self.toolPushButton_get_tokens_file_path = ToolButton()
        self.toolPushButton_get_tokens_file_path.setIcon(self.style().standardPixmap(QStyle.StandardPixmap.SP_DirOpenIcon))

        self.hBoxLayout_local_model.addWidget(self.tokens_file_path)
        self.hBoxLayout_local_model.addWidget(self.lineEdit_tokens_file_path)
        self.hBoxLayout_local_model.addWidget(self.toolPushButton_get_tokens_file_path)

        # ==========================================================================================================
        self.hBoxLayout_local_model = QHBoxLayout()
        self.addLayout(self.hBoxLayout_local_model)

        # 使用 rule_fsts 添加相关控件到布局
        self.rule_fsts_file_path = QLabel()
        self.rule_fsts_file_path.setText(self.__tr("rule_fsts"))
        self.rule_fsts_file_path.setObjectName("LabelModelPath")
        self.rule_fsts_file_path.setStyleSheet("#LabelModelPath{ background : rgba(0, 128, 0, 120); }")
        self.lineEdit_rule_fsts_file_path = LineEdit()
        self.lineEdit_rule_fsts_file_path.setClearButtonEnabled(True)
        self.toolPushButton_get_rule_fsts_file_path = ToolButton()
        self.toolPushButton_get_rule_fsts_file_path.setIcon(self.style().standardPixmap(QStyle.StandardPixmap.SP_DirOpenIcon))

        self.hBoxLayout_local_model.addWidget(self.rule_fsts_file_path)
        self.hBoxLayout_local_model.addWidget(self.lineEdit_rule_fsts_file_path)
        self.hBoxLayout_local_model.addWidget(self.toolPushButton_get_rule_fsts_file_path)
        # ==========================================================================================================
        self.hBoxLayout_local_model = QHBoxLayout()
        self.addLayout(self.hBoxLayout_local_model)

        # 使用 hotwords 添加相关控件到布局
        self.hotwords_file_path = QLabel()
        self.hotwords_file_path.setText(self.__tr("hotwords"))
        self.hotwords_file_path.setObjectName("LabelModelPath")
        self.hotwords_file_path.setStyleSheet("#LabelModelPath{ background : rgba(0, 128, 0, 120); }")
        self.lineEdit_hotwords_file_path = LineEdit()
        self.lineEdit_hotwords_file_path.setClearButtonEnabled(True)
        self.toolPushButton_get_hotwords_file_path = ToolButton()
        self.toolPushButton_get_hotwords_file_path.setIcon(self.style().standardPixmap(QStyle.StandardPixmap.SP_DirOpenIcon))

        self.hBoxLayout_local_model.addWidget(self.hotwords_file_path)
        self.hBoxLayout_local_model.addWidget(self.lineEdit_hotwords_file_path)
        self.hBoxLayout_local_model.addWidget(self.toolPushButton_get_hotwords_file_path)

        # ==========================================================================================================
        # model_online_RadioButton = RadioButton()
        # model_online_RadioButton.setChecked(False)
        # model_online_RadioButton.setText(self.__tr("在线下载模型"))
        # model_online_RadioButton.setToolTip(self.__tr("下载可能会花费很长时间，具体取决于网络状态，请耐心等待"))
        # self.model_online_RadioButton = model_online_RadioButton
        # self.addWidget(model_online_RadioButton)

        # self.hBoxLayout_online_model = QHBoxLayout()
        # self.addLayout(self.hBoxLayout_online_model)

        # # 添加一些控件到布局中

        # # ==========================================================================================================
        # self.label_online_model_name = QLabel()
        # self.label_online_model_name.setText(self.__tr("模型名称"))
        # self.label_online_model_name.setObjectName("LabelOnlineModelName")
        # self.label_online_model_name.setStyleSheet("#LabelOnlineModelName{ background : rgba(0, 128, 0, 120); }")

        # self.combox_online_model = EditableComboBox()
        # # 下拉框设置项目
        # self.combox_online_model.addItems(self.model_names)
        # # 下拉框设置自动完成
        # completer = QCompleter(self.model_names, self)
        # self.combox_online_model.setCompleter(completer)
        # self.combox_online_model.setCurrentIndex(0)
        # self.hBoxLayout_online_model.addWidget(self.label_online_model_name)
        # self.hBoxLayout_online_model.addWidget(self.combox_online_model)

        self.setModelLocationLayout()

        GridLayout_model_param = QGridLayout()
        GridLayout_model_param.setAlignment(Qt.AlignmentFlag.AlignTop)
        GridLayout_model_param.setContentsMargins(0, 0, 0, 0)
        GridLayout_model_param.setSpacing(0)
        self.addLayout(GridLayout_model_param)
        GridLayout_model_param_widgets_list = []

        # ===================================================================================================================================================================================================
        # hotword score of each token for biasing word/phrase. Used only if --hotwords-file is given.
        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        LineEdit_hotwords_score = LineEdit()
        LineEdit_hotwords_score.setText("1.5")
        LineEdit_hotwords_score.setToolTip(self.__tr("专有词汇提升分数(默认为1.5)。"))
        self.LineEdit_hotwords_score = LineEdit_hotwords_score

        self.paramItemWidget_hotwords_score = ParamWidget(self.__tr("专有词汇分数"), self.__tr("指定专有词汇提升分数"), LineEdit_hotwords_score)

        GridLayout_model_param_widgets_list.append(self.paramItemWidget_hotwords_score)

        # ===================================================================================================================================================================================================

        # 设备
        device_combox  = ComboBox()
        device_combox.addItems(self.device_list)
        device_combox.setCurrentIndex(1)
        self.device_combox = device_combox

        self.paramItemWidget_device = ParamWidget(self.__tr("处理设备"), self.__tr("选择运行语音识别的设备。"), device_combox)
        GridLayout_model_param_widgets_list.append(self.paramItemWidget_device)

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        LineEdit_device_index = LineEdit()
        LineEdit_device_index.setText("0")
        LineEdit_device_index.setToolTip(self.__tr("要使用的GPU设备ID。"))
        self.LineEdit_device_index = LineEdit_device_index

        self.paramItemWidget_device_index = ParamWidget(self.__tr("GPU 设备号"), self.__tr("要使用的GPU设备ID。"), LineEdit_device_index)

        GridLayout_model_param_widgets_list.append(self.paramItemWidget_device_index)

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # 采样率
        preciese_combox  = EditableComboBox()
        preciese_combox.addItems(self.preciese_list)
        preciese_combox.setCurrentIndex(5)
        preciese_combox.setCompleter(QCompleter(self.preciese_list))
        preciese_combox.setToolTip(self.__tr("采样率"))
        self.preciese_combox = preciese_combox

        self.paramItemWidget_preciese = ParamWidget(self.__tr("采样率"), self.__tr("用于训练模型的训练数据的采样率。"), preciese_combox)

        GridLayout_model_param_widgets_list.append(self.paramItemWidget_preciese)

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        LineEdit_cpu_threads = LineEdit()
        LineEdit_cpu_threads.setText("4")
        LineEdit_cpu_threads.setToolTip(self.__tr("在CPU上运行时使用的线程数(默认为4)。非零值会覆盖"))
        self.LineEdit_cpu_threads = LineEdit_cpu_threads

        self.paramItemWidget_cpu_threads = ParamWidget(self.__tr("线程数（CPU）"), self.__tr("在CPU上运行时使用的线程数(默认为4)。非零值会覆盖"), LineEdit_cpu_threads)

        GridLayout_model_param_widgets_list.append(self.paramItemWidget_cpu_threads)

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        LineEdit_num_workers = LineEdit()
        LineEdit_num_workers.setText("2")
        LineEdit_num_workers.setToolTip(self.__tr("具有多个工作线程可以在运行模型时实现真正的并行性。\n这可以以增加内存使用为代价提高整体吞吐量。"))
        self.LineEdit_num_workers = LineEdit_num_workers

        self.paramItemWidget_num_workers = ParamWidget(self.__tr("并发数"), self.__tr("具有多个工作线程可以在运行模型时实现真正的并行性。\n这可以以增加内存使用为代价提高整体吞吐量。"), LineEdit_num_workers)

        GridLayout_model_param_widgets_list.append(self.paramItemWidget_num_workers)

        # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # button_download_root = PushButton()
        # button_download_root.setText(self.__tr("下载缓存目录"))

        # self.LineEdit_download_root = LineEdit()
        # self.LineEdit_download_root.setToolTip(self.__tr("模型下载保存的目录。如果未修改,\n则模型将保存在标准Hugging Face缓存目录中。"))

        # self.LineEdit_download_root = self.LineEdit_download_root
        # self.button_download_root = button_download_root

        # self.paramItemWidget_download_root = ParamWidget(self.__tr("下载缓存目录"), self.__tr("模型下载保存的目录。如果未修改,\n则模型将保存在标准Hugging Face缓存目录中。"), self.button_download_root)
        # self.paramItemWidget_download_root.addwidget(self.LineEdit_download_root)

        # GridLayout_model_param_widgets_list.append(self.paramItemWidget_download_root)

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        self.switchButton_use_endpoint = SwitchButton()
        self.switchButton_use_endpoint.setChecked(False)
        self.switchButton_use_endpoint.setOnText(self.__tr("启用"))
        self.switchButton_use_endpoint.setOffText(self.__tr("不启用"))
        self.paramItemWidget_use_endpoint = ParamWidget(self.__tr("是否启用端点检测"), self.__tr("如果为 True 启用端点检测,如果为 False 禁用端点检测。"), self.switchButton_use_endpoint)

        GridLayout_model_param_widgets_list.append(self.paramItemWidget_use_endpoint)

        # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        for i,item in enumerate(GridLayout_model_param_widgets_list):
            GridLayout_model_param.addWidget(item, i,0)


    def setParam(self, param:dict):
        self.model_local_RadioButton.setChecked(param["localModel"])
        # self.model_online_RadioButton.setChecked(param["onlineModel"])

        self.setModelLocationLayout()

        self.lineEdit_decoder_model_path.setText(param["decoder_model"])
        self.lineEdit_encoder_model_path.setText(param["encoder_model"])
        self.lineEdit_joiner_model_path.setText(param["joiner_model"])
        self.lineEdit_tokens_file_path.setText(param["token_file"])
        self.lineEdit_rule_fsts_file_path.setText(param["rule_fsts_file"])
        self.lineEdit_hotwords_file_path.setText(param["hotwords_file"])
        self.LineEdit_hotwords_score.setText(param["hotwords_score"])

        # self.combox_online_model.setCurrentIndex(param["modelName"])

        self.device_combox.setCurrentIndex(param["device"])
        self.LineEdit_device_index.setText(param["deviceIndex"])
        # self.preciese_combox.setCurrentIndex(param["preciese"])
        self.LineEdit_cpu_threads.setText(param["thread_num"])
        self.LineEdit_num_workers.setText(param["num_worker"])
        # self.LineEdit_download_root.setText(param["download_root"])
        self.switchButton_use_endpoint.setChecked(param["use_endpoint"] )

    def getParam(self):
        param = {}
        param["localModel"] = self.model_local_RadioButton.isChecked()
        param["decoder_model"] = self.lineEdit_decoder_model_path.text()
        param["encoder_model"] = self.lineEdit_encoder_model_path.text()
        param["joiner_model"] = self.lineEdit_joiner_model_path.text()
        param["token_file"] = self.lineEdit_tokens_file_path.text()
        param["rule_fsts_file"] = self.lineEdit_rule_fsts_file_path.text()
        param["hotwords_file"] = self.lineEdit_hotwords_file_path.text()
        param["hotwords_score"] = self.LineEdit_hotwords_score.text().strip()
        self.LineEdit_hotwords_score.setText(param["hotwords_score"])
        # param["onlineModel"] = self.model_online_RadioButton.isChecked()
        # param["model_path"] = self.lineEdit_model_path.text()
        # param["modelName"] = self.combox_online_model.currentIndex()
        param["device"] = self.device_combox.currentIndex()
        param["deviceIndex"] = self.LineEdit_device_index.text().strip()
        param["preciese"] = self.preciese_combox.currentIndex()
        param["thread_num"] = self.LineEdit_cpu_threads.text().strip()
        param["num_worker"] = self.LineEdit_num_workers.text().strip()
        # param["download_root"] = self.LineEdit_download_root.text().strip()
        param["use_endpoint"] = self.switchButton_use_endpoint.isChecked()

        return param

