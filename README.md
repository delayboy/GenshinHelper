# GenshinHelper
提瓦特退坑小助手



## 软件特性

| 功能名称                                        | 触发方式                     |
| ----------------------------------------------- | ---------------------------- |
| 「空荧酒馆」原神地图扩展屏                      | 启动运行自动连接             |
| OCR技能冷却修正，用于适应迟滞止水（公子技能等） | 游戏中按E触发                |
| 那维莱特转圈圈                                  | 游戏中蓄力重击时同时按住ctrl |
| 草神转一圈                                      | 切换到草神长按E              |
| 大月卡武器遗祀玉珑buff计时                      | 那维入队后自动开启           |
| 基于OCR的配队切换                               | 游戏中按F                    |
| 锁定配对（按F不再切换配队）                     | 游戏中按H                    |
| 冷却时间手动归零                                | 游戏中按0                    |



## OpenCV模板图设置

\py_files\templates\partner中设置队友新的名称，要求与配置文件PARTNER_SETTING遍历中的命名一致



## 配置文件

- settings.txt

```python
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

