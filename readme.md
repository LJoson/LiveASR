# LiveASR

----

简介：本项目是基于 sherpa-onnx 搭建的一个实时语音识别系统。

### 系统安装步骤

```shell
# 首先安装必要的python库
cd ./LiveASR
pip3 install -r requirements.txt
```

### 系统运行步骤

在安装完必要的库之后，就可以运行了，主要的运行文件是 LiveASRGUI.py，运行该文件即可启动系统。

```shell
python3 LiveASRGUI.py
```


### 实现原理

1. 通信

   项目中的通信主要使用的是 Websocket 模块实现

2. 异步编程

   项目中的异步编程主要使用的是 asyncio 模块实现，其中主要的异步任务包括：

   - 语音识别任务：使用 sherpa-onnx 模块进行语音识别，并将识别结果动态刷新

### 致谢与引用

本项目在开发过程中参考和使用了以下开源项目和技术，在此表示诚挚的感谢：

#### 核心语音识别引擎
- [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) - 基于 ONNX 的语音识别工具包，提供了高效的语音识别功能
- [Whisper](https://github.com/openai/whisper) - OpenAI 开发的开源语音识别模型，为语音识别技术提供了重要参考

#### 中文语音识别相关
- [FunASR](https://github.com/modelscope/FunASR) - 阿里巴巴达摩院开源的中文语音识别工具包
- [PPASR](https://github.com/yeyupiaoling/PPASR) - 基于 PaddlePaddle 的中文语音识别项目
- [RapidASR](https://github.com/RapidAI/RapidASR) - 快速语音识别框架

#### 语音识别 GUI 工具
- [faster-whisper-GUI](https://github.com/CheshireCC/faster-whisper-GUI) - Faster Whisper 的图形界面实现
- [Whisper-WebUI](https://github.com/jhj0517/Whisper-WebUI) - Whisper 的 Web 界面实现
- [WhisperGUI](https://github.com/ADT109119/WhisperGUI) - Whisper 的桌面应用界面
- [asr-gui](https://github.com/farhadcuber/asr-gui) - 语音识别图形界面工具

#### 其他相关项目
- [CapsWriter-Offline](https://github.com/HaujetZhao/CapsWriter-Offline) - 离线语音输入工具
- [buzz](https://github.com/chidiwilliams/buzz) - 语音转文字工具
- [Const-me/Whisper](https://github.com/Const-me/Whisper) - Whisper 的 C++ 实现

#### 技术参考
- [51CTO 文章](https://www.51cto.com/article/778871.html) - 关于语音识别技术的技术文章
- [IDC 帮助文档](https://www.idc.net/help/414963/) - 语音识别相关技术文档

### 许可证

本项目遵循 GNU 通用公共许可证（GPL）。详情请参阅 [LICENSE](LICENSE) 文件。

https://github.com/k2-fsa/sherpa-onnx
https://www.51cto.com/article/778871.html

https://github.com/openai/whisper

https://github.com/RapidAI/RapidASR?tab=readme-ov-file

https://github.com/modelscope/FunASR

https://github.com/Const-me/Whisper

https://github.com/farhadcuber/asr-gui

https://github.com/yeyupiaoling/PPASR

https://github.com/HaujetZhao/CapsWriter-Offline?tab=readme-ov-file

https://github.com/CheshireCC/faster-whisper-GUI

https://github.com/SYSTRAN/faster-whisper

https://github.com/Pikurrot/whisper-gui?tab=readme-ov-file

https://github.com/jhj0517/Whisper-WebUI

https://github.com/ADT109119/WhisperGUI

https://www.idc.net/help/414963/

https://github.com/chidiwilliams/buzz