# coding:utf-8

import os
# from pathlib import Path

from PySide6.QtCore import  (
                                QCoreApplication,
                                QTranslator,
                                Qt
                            )

from PySide6.QtWidgets import  (
                                # QApplication,
                                QSpacerItem,
                                QWidget
                                , QStackedWidget
                                , QVBoxLayout
                                , QHBoxLayout
                                , QGridLayout
                                # , QMainWindow
                            )

from PySide6.QtGui import QIcon

from qfluentwidgets import (
                            NavigationAvatarWidget,
                            NavigationInterface
                            , setTheme
                            , setThemeColor
                            , Theme
                            , FluentIcon
                            , NavigationItemPosition

                        )

from qframelesswindow import (
                                FramelessMainWindow
                                , StandardTitleBar
                            )

from .config import (Language_dict
                    , Preciese_list
                    , Model_names
                    , Device_list
                )

from resource import (rc_Image, rc_qss)
import json

from .version import (
                        __version__

                    )

from .style_sheet import StyleSheet
from .translator import TRANSLATOR
from resource import rc_Translater

from .modelPageNavigationInterface import ModelNavigationInterface
from .serverPageNavigationInterface import ServerNavigationInterface
from .processPageNavigationInterface import ProcessPageNavigationInterface
from .homePageNavigationInterface import HomePageNavigationinterface
from .aboutPageNavigationInterface import AboutPageNavigationInterface
from .fasterGuiIcon import FasterGUIIcon
from .settingPageNavigation import SettingPageNavigationInterface

# class aa(QWidget):
#     def __init__(self, parent: QWidget | None = ..., f: Qt.WindowType = ...) -> None:
#         super().__init__(parent, f)
# =======================================================================================
# UI
# =======================================================================================
class UIMainWin(FramelessMainWindow):
    """V"""

    # def tr(self, text):
    #     return QCoreApplication.translate(self.__class__.__name__, text)

    def readConfigJson(self, config_file_path: str = ""):
        self.default_theme = "light"
        self.model_param = {}
        self.setting = {}
        self.demucs = {}
        self.Transcription_param = {}
        self.output_whisperX_param = {}
        self.Server_param = {}

        if not config_file_path:
            return

        self.use_auth_token_speaker_diarition= ""
        with open(os.path.abspath(config_file_path),"r", encoding="utf8") as fp:
            json_data = json.load(fp)

            try:
                self.default_theme = json_data["theme"]
            except:
                self.default_theme = "light"

            try:
                self.model_param = json_data["model_param"]
            except:
                self.model_param = {}

            try:
                self.setting = json_data["setting"]
            except:
                self.setting = {}

            try:
                self.Server_param = json_data["Server_param"]
            except:
                self.Server_param = {}


    def setConfig(self):
        setTheme(Theme.DARK if self.default_theme == "dark" else Theme.LIGHT, save=True, lazy=True)
        # setThemeColor("#aaff009f")

        try:
            if self.model_param != {} and hasattr(self, 'page_model'):
                self.page_model.setParam(self.model_param)
        except Exception as e:
            print(f"设置模型参数失败: {str(e)}")

        try:
            if self.setting != {} and hasattr(self, 'page_setting'):
                self.page_setting.setParam(self.setting)
        except Exception as e:
            print(f"设置页面参数失败: {str(e)}")

        try:
            if self.Server_param != {} and hasattr(self, 'page_Server'):
                self.page_Server.setParam(self.Server_param)
        except Exception as e:
            print(f"设置服务器参数失败: {str(e)}")

    def __init__(self, parent=None, f=None) -> None:
        super().__init__()

        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.model_path = ""
        self.model_names = Model_names

        # 模型支持的计算设备
        self.device_list = Device_list
        # 模型支持的计算精度
        self.preciese_list = Preciese_list
        # 语言支持
        self.LANGUAGES_DICT = Language_dict

        self.SherpaOnnxModel = None

        # 读配置文件
        self.readConfigJson(r"./GUIConfig.json")

        # UI设置
        self.setupUI()
        self.initWin()

        # 设置配置
        self.setConfig()



    def initWin(self):

        self.setObjectName("FramlessMainWin")
        # setTheme(Theme.LIGHT)
        StyleSheet.MAIN_WINDOWS.apply(self)

        # self.resize(800, 500)
        self.setGeometry(100, 100, 1250, 915)

        # TODO: 添加标题栏
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.setAttribute(Qt.WA_StyledBackground)


        self.setWindowIcon(QIcon(":/resource/Image/microphone.png"))


    def setupUI(self):

        # =====================================================================================
        # 创建窗体中心控件
        self.mainWindowsWidget = QWidget(self)
        self.mainWindowsWidget.setObjectName("mainWidget")

        # 创建窗体主布局
        self.mainLayout = QGridLayout()

        # 将主布局添加到窗体中心控件
        self.mainWindowsWidget.setLayout(self.mainLayout)

        # 导航布局
        self.vBoxLayout = QVBoxLayout()

        # 将导航布局添加到主布局
        self.mainLayout.addLayout(self.vBoxLayout,0,0)

        # 设置窗体中心控件
        self.setCentralWidget(self.mainWindowsWidget)

        # TODO: 创建一个空对象 用于改善布局顶部
        self.spacer_main = QSpacerItem(0,25)
        self.vBoxLayout.addItem(self.spacer_main)

        # 设置显示图层到最后避免遮挡窗体按钮
        self.mainWindowsWidget.lower()
        self.lower()

        # 创建布局用于放置导航枢和分页
        self.mainHBoxLayout = QHBoxLayout()
        self.vBoxLayout.addLayout(self.mainHBoxLayout)

        # 创建窗体导航枢 和 stacke 控件
        self.pivot = NavigationInterface(self, showMenuButton=True, showReturnButton=True)
        self.pivot.setObjectName("pivot")
        self.pivot.setExpandWidth(300)
        # self.pivot.panel.returnButton.setEnabled(True)

        self.stackedWidget = QStackedWidget(self)

        self.mainHBoxLayout.addWidget(self.pivot)
        self.mainHBoxLayout.addWidget(self.stackedWidget)

        self.pages = []

        # 添加子界面
        self.page_home = HomePageNavigationinterface(self)
        self.addSubInterface(self.page_home, "pageHome", self.tr("Home"), icon=FluentIcon.HOME)
        self.pages.append(self.page_home)

        self.page_model = ModelNavigationInterface(self)
        self.addSubInterface(self.page_model, "pageModelParameter", self.tr("模型参数"), icon=FluentIcon.BOOK_SHELF)
        self.pages.append(self.page_model)

        self.page_Server = ServerNavigationInterface(self)
        self.addSubInterface(self.page_Server, "pageServerParameter", self.tr("转写服务参数"), icon=FasterGUIIcon.Server_PAGE)
        self.pages.append(self.page_Server)

        self.page_process = ProcessPageNavigationInterface(self)
        self.addSubInterface(self.page_process, "pageProcess", self.tr("执行转写"), icon=FasterGUIIcon.HEAD_PHONE)
        self.pages.append(self.page_process)

        self.page_About = AboutPageNavigationInterface(self)
        self.addSubInterface(self.page_About, "pageAbout", self.tr("关于"), icon=FluentIcon.INFO)
        self.pages.append(self.page_About)

        # =============================================================================================================================

        self.navigationAvatarWidget = NavigationAvatarWidget('', ':/resource/Image/killua.png')
        self.pivot.addWidget(
                            routeKey='avatar',
                            widget=self.navigationAvatarWidget,
                            onClick=lambda: self.stackedWidget.setCurrentWidget(self.page_About),
                            position=NavigationItemPosition.BOTTOM
                        )

        self.page_setting = SettingPageNavigationInterface(self)
        self.addSubInterface(
            self.page_setting, "pageSetting", self.tr('设置'), FluentIcon.SETTING, NavigationItemPosition.BOTTOM)
        self.pages.append(self.page_setting)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.page_home)
        # self.pivot.setCurrentItem(self.page_process.objectName())

        # 设置默认 RouteKey 防止返回键功能异常
        self.pivot.panel.history.setDefaultRouteKey(self.stackedWidget, self.page_home.objectName())


    def addSubInterface(self, layout: QWidget, objectName, text: str, icon:QIcon=None,position=NavigationItemPosition.TOP ):
        layout.setObjectName(objectName)
        self.stackedWidget.addWidget(layout)
        item = self.pivot.addItem(
            routeKey=objectName
            ,text=text
            # 由于修复下面的 bug ，此处需要手动重新设置 setCurrentWidget 来保证换页功能正常
            ,onClick=lambda: self.stackedWidget.setCurrentWidget(layout)
            ,icon=icon
            ,position=position
        )

        # item.clicked.connect(lambda: self.pivot.panel.history.push(self.stackedWidget , objectName))

    def onCurrentIndexChanged(self, index):
        if not index :
            index = self.stackedWidget.currentIndex()
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        self.pivot.panel.history.push(self.stackedWidget , widget.objectName())
