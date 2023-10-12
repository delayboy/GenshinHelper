from __future__ import annotations  # 使用高级注解器，
from PartnerHelper import MainUI, main_loop


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


if __name__ == '__main__':
    MainUI(main_loop).myloop()
