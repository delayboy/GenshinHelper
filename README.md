# GenshinHelper

提瓦特退坑小助手：基于OCR的原神技能冷却计时插件，额外支持快速跳过游戏剧情、云游戏挂机领月卡、砍树、尘哥壶领取硬币、探索派遣、米友社签到等功能。内封那维莱特&纳西妲转圈圈脚本，【遗祀玉珑】buff计时辅助。支持录制任意Windows后台窗口将画面传输的手机，从而实现Android扩展屏（此功能主要用于配合「空荧酒馆」原神地图工具一起使用），同时在不安装任何python环境的情况下您也可以对本工具的代码逻辑进行修改，详见章节[不安装任何python环境如何修改源码](#不安装任何python环境如何修改源码)



本工具力求帮原友们打造轻松的原神“就业”体验，高效深渊、手残补强、光速资源采集&地图探索，可基于本人现有的patch脚本定制更多自动化模块，轻松解绑您与原神签署的”月卡合同“，解放上班族们宝贵的时间，感受**每日光速下线不加班，想退坑就退坑，不想退坑创造条件也能退坑**的游戏体验。



## 重要提示

使用**本工具一定要以无边框窗口模式运行原神！！！！！**。

如何开启无边框窗口：

在原神启动器文件夹下找到Genshin Impact Game文件夹，打开后找到YuanShen.exe在桌面创建快捷方式，右击快捷方式，在快捷方式目标属性中追加 `-popupwindow`参数，即可以无边框窗口方式启动原神。

```shell
"启动器安装目录\Genshin Impact Game\YuanShen.exe" -popupwindow
```



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



## DLL提示无法定位程序输入点CreateDX...

说明电脑法使用最新的DX11截图技术，解决办法是将文件夹里的`MyDll-Without-DX11.dll` 重命名为 `MyDll.dll`替换现有的 `MyDll.dll`文件即可正常运行




## OpenCV模板图设置

\py_files\templates\partner中设置队友新的名称，要求与配置文件PARTNER_SETTING遍历中的命名一致

\py_files\templates\cloud_templates 设置云挂机脚本相关模板图

## 配置文件

- settings.py

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

## 不安装任何python环境如何修改源码

本工具支持使用patch技术在不安装python环境的情况下做源码微调，技能冷却相关代码，可以通过 settings.py来重写 PartnerHelper.py中的基本内容，然后双击 pyd_main.exe运行即可。注意**使用这种写法您将无法调用额外的任何第三方库，所用的库文件必须包含在hidden_imports之中**，参见章节[Requirements](#Requirements)

云挂机脚本则可通过patch.py脚本来重写源程序的部分行为。

需要注意的是，**重写内容过多可能导致源程序发生各种逻辑错误，不建议用于开发复杂功能**。

## 如何使用插件定义自己的鼠标宏

可参考那维莱特&草神转圈圈鼠标宏的编写方法，可参考开源代码 `PartnerHelper.py` 中的转圈圈代码：

```shell
  def user_realtime_key_code(self, pk: MyDllLib.HookPackage) -> bool:
        if not pk.keyEventType:
            if pk.wParam == 0x0201:  # WM_LBUTTONDOWN
                if self.main_app.on_ctrl:
                    start_thread(self.rotation_loop, (9999, 0))

            elif pk.wParam == 0x0202:  # WM_LBUTTONUP
                self.keep_rotation = False
            return False

        if pk.code == 69:  # E
            name = self.ship_names[self.now_index]
            if pk.wParam == MyDllLib.WM_KEYDOWN:

                if name.__contains__("草神") and not self.keep_rotation:  # 只触发一次
                    start_thread(self.rotation_loop, (2, 0.2))

            else:
                self.keep_rotation = False

        if pk.code == 162:  # ctrl
            if pk.wParam == MyDllLib.WM_KEYDOWN:
                if self.main_app.left_button_down:
                    start_thread(self.rotation_loop, (9999, 0))
            else:
                self.keep_rotation = False

        return False
```



## 如何使用云游戏挂机功能

将Edge.zip浏览器压缩包，解压到py_files文件夹里，设置配置文件 `settings.py` 如下：

```python
# 是否以云挂机模式启动程序（将启动云挂机而非冷却计时助手）
USE_CLOUD = True
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

双击pyd_main.exe启动即可启动挂机脚本

## 如何切换云砍树

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

## 如何编排自己的自动化云脚本（可扩展神经网络模型）

参照本人开源的`patch.py`脚本编写一个小任务：

```python
    def 铁道每日任务奖励领取6(self, img: np.ndarray):
        if not 6 == self.taskId:
            return False

        self._match_pos_and_do("铁道每日任务黄色领取按钮.png", img, 0.85)
        self._match_pos_and_do("铁道每日任务黄色小礼盒.png", img, 0.85)
        self._match_pos_and_do("铁道派遣中按钮.png", img, 0.85, action_alias_name="铁道各种叉号退出")
        self._match_pos_and_do("铁道委托图标.png", img, 0.85, action_alias_name="铁道各种叉号退出")
        self._match_sub_pos_and_do("右上角每日任务图标.png", img, Rect(0.6, 0.2, 0.86, 0.32), 0.85)
        self._match_pos_and_do("铁道左上角每日实训图标.png", img, 0.85, reward=20,
                               action_alias_name="标记本次任务已完成")
```

如果想自己编排更复杂的任务，需要充分理解 `class ManyScriptArranger` 类的编写逻辑，该类的唯一入口函数为 `script_entry_point`其他成员方法均为辅助，定义该入口即可进行脚本的循环运行：

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

获取更多上下文数据，如webdriver窗口信息等，可参考 `WebDriver.py`的源代码，使用python动态patch技术加载脚本：

```python
 def key_code_callback(self, key_code: int) -> bool:
        self.arranger.key_code_callback(key_code)
        if key_code == MyDllLib.VK_F1 + 3:
            new_md5 = auto_patch_python(None)
            if not new_md5.__eq__(self.last_py_code):
                self.last_py_code = auto_patch_python(globals())
                self.arranger = ManyScriptArranger(self)
            else:
                logger.debug("md5: (%s,%s)", new_md5, self.last_py_code)
            self.main_app.change_pause_mode()
            self.manager.set_foreground_window()
            self.manager.set_top(not self.main_app.Pause)
            self.main_app.set_top(self.main_app.Pause)
        return False
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



[不安装任何python环境如何修改源码]: 
[#不安装任何python环境如何修改源码]: 
