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
```
        # if message['text'] != '':
        # if self.asr != message['text'] and message['text'] != '' and self.asr.startswith(message['text']):
        #     self.asr = message['text']
        #     # self.full_text  = message['text']
        #     # self.page_process.processResultText.append(f"{self.current_role}: {self.asr}\n")
        # elif message['text'] == '' and self.asr != '':
        #     import cn2an
        #     self.asr = cn2an.transform(self.asr, method="cn2an")
        #     full_message = f"{self.current_role}: {self.asr}\n"
        #     # self.page_process.processResultText.append(full_message)
        #     if self.current_role == '管制员':
        #         self.runway_status = {'21': None, '03': None}  # 重置跑道状态
        #         self.last_controller_message = self.asr  # 更新管制员消息
        #     if self.current_role == 'A1飞行员':
        #         self.last_a1_message = self.asr  # 更新A1飞行员的最后指令
        #     if self.current_role == 'D1飞行员':
        #         self.last_d1_message = self.asr  # 更新A1飞行员的最后指令
        #     self.check_warnings()
        #     self.get_warnings()
        #     # 切换角色，确保在管制员和飞行员之间交替
        #     self.role_index = (self.role_index + 1) % len(self.roles)
        #     self.current_role = self.roles[self.role_index]
        #     self.asr = ''  # 重置当前发言
        #     self.warnings = [] # 重置告警列表
```