# coding:utf-8

from PySide6.QtCore import QEasingCurve, QObject, Qt
from .navigationInterface import NavigationBaseInterface

from .homePageItemLabel import ItemLabel
from qfluentwidgets import FlowLayout

from resource import rc_Image


class HomePageNavigationinterface(NavigationBaseInterface):
    def parent(self) -> QObject:
        return super().parent()

    def __init__(self, parent=None):
        # self.parent = parent
        super().__init__(title=self.tr("Home"), subtitle=self.tr("sherpa 为主要后端的 ASR 软件"), parent=parent)
        self.setupUI()

    def setupUI(self):
        # self.toolBar.deleteLater()
        # self.vBoxLayout.removeWidget(self.toolBar)
        # self.toolBar = None

        self.toolBar.modelStatusLabel.setVisible(False)
        self.toolBar.buttonLayout.removeWidget( self.toolBar.modelStatusLabel)

        self.hBoxLayout = FlowLayout(needAni=True)
        self.hBoxLayout.setContentsMargins(30,30,30,30)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hBoxLayout.setAnimation(250, QEasingCurve.OutQuad)
        self.addLayout(self.hBoxLayout)

        self.itemLabel_sherpa_asr = ItemLabel(
                                                    self,
                                                    self.tr("LiveASR"),
                                                    self.tr("自动人声识别")
                                                )

        self.itemLabel_sherpa_asr.setModelButton(self.tr("模型设置"))
        self.itemLabel_sherpa_asr.setServerButton(self.tr("服务设置"))
        self.itemLabel_sherpa_asr.setMainButton(self.tr("进入"))


        self.hBoxLayout.addWidget(self.itemLabel_sherpa_asr)#, 3, alignment=Qt.AlignmentFlag.AlignLeft)


