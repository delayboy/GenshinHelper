# GenshinHelper
提瓦特退坑小助手：基于OCR的原神技能冷却计时插件，额外支持快速跳过游戏剧情、云游戏挂机领月卡、砍树、尘哥壶领取硬币、探索派遣、米友社签到等功能。内封那维莱特&纳西妲转圈圈脚本，【遗祀玉珑】buff计时辅助。支持录制任意Windows后台窗口将画面传输的手机，从而实现Android扩展屏（此功能主要用于配合「空荧酒馆」原神地图工具一起使用）

本工具力求帮原友们打造轻松的原神“就业”体验，高效深渊、手残补强、光速资源采集&地图探索，可基于本人现有的patch脚本定制更多自动化模块，轻松解绑您与原神签署的”月卡合同“，解放上班族们宝贵的时间，感受**每日光速下线，想退坑就退坑，不想退坑创造条件也能退坑**的游戏体验。



## 软件特性

| 功能名称                                                     | 触发方式                                            |
| ------------------------------------------------------------ | --------------------------------------------------- |
| 云挂机领月卡-砍树-尘哥壶领取硬币-探索派遣-米友社奖励-星琼铁道签到派遣 | 设置USE_CLOUD = True进入程序后按F4启动脚本          |
| 「空荧酒馆」原神地图扩展屏                                   | 启动运行自动连接                                    |
| OCR技能冷却修正，用于适应迟滞止水（公子技能等）              | 游戏中按E触发                                       |
| 那维莱特转圈圈                                               | 游戏中蓄力重击时同时按住ctrl                        |
| 草神转一圈                                                   | 切换到草神长按E                                     |
| 大月卡武器遗祀玉珑buff计时                                   | 那维入队后自动开启                                  |
| 基于OCR的配队切换                                            | 游戏中按F                                           |
| 锁定配对（按F不再切换配队）                                  | 游戏中按H                                           |
| 冷却时间手动归零                                             | 游戏中按0                                           |
| 快速过剧情                                                   | 在游戏中按左上角的`或~键，然后按住↓键即可快速过剧情 |




## OpenCV模板图设置

\py_files\templates\partner中设置队友新的名称，要求与配置文件PARTNER_SETTING遍历中的命名一致

\py_files\templates\cloud_templates 设置云挂机脚本相关模板图

## 配置文件

- settings.txt

```python
# 是否以云挂机模式启动程序（将启动云挂机而非冷却计时助手）
USE_CLOUD = False
# 技能显示y轴起始坐标（相对于屏幕的百分比）
Y_POS_0 = 0.24
# 技能显示y轴间隔坐标（相对于屏幕的百分比）
Y_DELTA = 0.085
# Android手机adb devices名称
ANDROID_DEVICE_NAME = "QWBILZRGSW7XXXX"
# 后台录屏的窗口名称
EXT_SCREEN_WIN_NAME = "「空荧酒馆」原神地图"
# 设置角色和技能冷却
PARTNER_SETTING = """
胡桃^16^false^
宵宫^18^false^
"""
```



## 工具文件

- create_pyd_file.py： 批量将python编译为pyd文件
- setup_example.py：pyd文件编译模板，已弃用
- PartnerHelper.py：小助手核心代码
- pyd_main.py：pyd编译入口文件
- adb.exe：手机调试工具
- 基于TCP的android扩展屏.apk：扩展屏上位机
- patch.py：网易云游戏挂机脚本编排
- WebDriver.py：云挂机脚本核心入口



## 如何开启云砍树

在patch.py中添加修改下代码，则脚本姿态将切换为刷树模型（刷树需要装备刷树小道具【王树瑞佑】，并且将角色放置到目标树林即可），挂机1个小时可获取300+树木：

- 修改前

```python
def script_entry_point(self):
    try:
        # self.loop_only_one_script()
        self.do_mi_you_she_task()
        self.do_yuan_shen_task()
        self.do_tie_dao_task()
        self.do_idle_task()
    except KeyboardInterrupt:
        pass
```

- 修改后

```python
def script_entry_point(self):
    try:
       	self.loop_only_one_script()
    except KeyboardInterrupt:
        pass
```



## Requirements

参见pyd_main.py的hidden_imports()函数：

```python
def hidden_imports():
    from PIL import Image, ImageTk  # pillow型图片支持库
    import tkinter as tk  # 窗口控件支持库
    import base64
    from typing import List, TypeVar, Callable, Generic, Dict, Tuple, Sequence
    import ctypes
    import numpy as np
    import threading
    import time
    import os
    import cv2
    import datetime
    import ctypes
    import time

    import numpy.ctypeslib as npct
    import numpy as np
    from typing import Callable, Any
    import win32gui
    import subprocess
    import threading
    from abc import abstractmethod
    import logging
    import os
    import datetime
    from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
    import hashlib

    import socket
    import time
    from typing import Dict, List, Callable, TypeVar
    import threading
    import ctypes
    import numpy as np
    import PyTools.MyAwesomeTool.MyDll as MyDllLib
    import PyTools.MyAwesomeTool.MyUtil
    import PyTools.MyAwesomeTool.MyTcpHelper
    import PyTools.MyAwesomeTool.PyUseCPlus
    import PyTools.MyAwesomeTool.MyProcessHelper
    import PyTools.MyAwesomeTool.MyLinkHelper
```

