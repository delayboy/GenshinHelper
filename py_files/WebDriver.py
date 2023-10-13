from __future__ import annotations  # 使用高级注解器，

from typing import TypeVar, Callable, Dict, Tuple, List
import datetime
import os
import time
import base64
import numpy as np
import cv2
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PyTools.MyAwesomeTool.MyUtil import start_thread, auto_patch_python, build_logger

from PyTools.MyAwesomeTool.PyUseCPlus import MainUI, MyOpenCv, WinManager, MyDllLib, Rect

logger = build_logger(filename="C:/share/log.txt", name=__name__, use_to_debug=True, file_log_debug=False,
                      use_time_rotate=False)


def base64_to_image(base64_string) -> np.ndarray:
    # 要解码的base64字符串

    # 从base64字符串中提取编码的图像数据部分
    image_data = base64_string.split(',')[1]

    # 将base64数据解码为字节数组
    image_bytes = base64.b64decode(image_data)

    # 将字节数组转换为NumPy数组
    image_np = np.frombuffer(image_bytes, np.uint8)

    # 解码为OpenCV图像
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    return image


class MyWebDriver:
    def __init__(self, my_dll: MyDllLib.MyDll):
        edge_execute_path = "/Edge/Application/"
        env_variable_name = "webdriver.edge.driver"
        user = os.getcwd()  # 获取当前工作目录
        # 设置EdgeDriver路径
        driver_path = user + edge_execute_path + "msedgedriver.exe"
        # 使用os.environ来设置环境变量
        os.environ[env_variable_name] = driver_path

        edge_options = webdriver.EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_argument("disable-gpu")
        edge_options.add_argument("start-maximized")
        # edge_options.add_argument("--auto-open-devtools-for-tabs")  # 自动为tab标签打开控制台窗口

        # 禁用密码管理
        edge_prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }
        edge_options.add_experimental_option("prefs", edge_prefs)

        # 更多Chrome选项可以在此处添加

        # 设置用户数据目录
        user_data_dir = user + "/Edge/UserData"
        profile_directory = "Profile 1"
        edge_options.add_argument("user-data-dir=" + user_data_dir)
        edge_options.add_argument("profile-directory=" + profile_directory)
        edge_options.add_argument('--force-device-scale-factor=1')
        # 设置代理（如果需要）
        # proxy = webdriver.Proxy()
        # proxy.http_proxy = "127.0.0.1:8888"
        # proxy.ssl_proxy = "127.0.0.1:8888"
        # edge_options.add_argument("--proxy-server=http://127.0.0.1:8888")

        logger.debug(edge_options)
        # 获取缩放比例

        self.driver = webdriver.Edge(options=edge_options)
        self.driver.set_window_size(1000, 800)
        self.driver.set_window_position(0, 0)
        self.js_lib_str = ""  # MyFileEditor("./JSLib.js").read()

    def close_current_tab_and_switch(self) -> bool:
        if len(self.driver.window_handles) > 1:
            target_locator = self.driver.switch_to
            self.driver.close()
            window_handles = self.driver.window_handles
            for window_handle in window_handles:
                # 切换到对应标签页
                target_locator.window(window_handle)
                break
            return True
        return False

    def get_now_url(self):
        return self.driver.execute_script("return window.location.href")

    def go_url(self):
        self.driver.get(
            "https://cg.163.com/#/mobile")
        time.sleep(2)
        logger.debug("go url")

    def capture_page_with_js(self) -> np.ndarray:
        base64_pic = self.driver.execute_script(self.js_lib_str + "\n\rreturn await saveAllPageAsPicture()")
        img = base64_to_image(base64_pic)
        return img

    def capture_page_with_driver(self) -> np.ndarray:
        # 截图并保存为NumPy数组
        screenshot = self.driver.get_screenshot_as_png()
        screenshot_np = np.frombuffer(screenshot, np.uint8)
        image = cv2.imdecode(screenshot_np, cv2.IMREAD_COLOR)

        return image

    def click_point_with_templates(self, src: np.ndarray, temp: np.ndarray, loc: tuple, percent_x: float = 0.5,
                                   percent_y: float = 0.5,
                                   click: bool = True, button_num: int = 0):
        src_shape = MyOpenCv.get_image_size(src)
        temp_shape = MyOpenCv.get_image_size(temp)
        rec = self.driver.get_window_size()
        w, h = (rec["width"], rec["height"])
        middle_x = (loc[0] + temp_shape[0] * percent_x) / src_shape[0] * w
        middle_y = (loc[1] + temp_shape[1] * percent_y) / src_shape[1] * h
        logger.debug('x:%.2f y:%.2f', middle_x, middle_y)
        # 获取当前窗口大小
        window_width = self.driver.execute_script("return window.innerWidth;")
        window_height = self.driver.execute_script("return window.innerHeight;")
        logger.debug("window_width: %.2f, window_height: %.2f", window_width, window_height)
        actions = ActionChains(self.driver)
        # 进行重置坐标
        actions.reset_actions()
        # 将鼠标移动到指定的坐标位置
        actions.move_by_offset(middle_x, middle_y)

        # 执行点击操作
        actions.click().perform()

    def close(self):
        self.driver.quit()


ManyScriptArranger = TypeVar("ManyScriptArranger")


class ScriptToolBox:
    def __init__(self, main_app: MainUI):
        self.main_app = main_app
        self.cache_img = None
        self.my_dll = main_app.my_dll
        self.driver = MyWebDriver(self.my_dll)
        time.sleep(1)
        self.driver.go_url()
        self.main_manager = WinManager(self.my_dll, "")
        self.manager = WinManager(self.my_dll, "网易云", False)
        self.manager.set_top(not self.main_app.Pause)
        self.last_py_code = auto_patch_python(globals())
        logger.debug("md5:%s", self.last_py_code)
        self.arranger = ManyScriptArranger(self)

        start_thread(self.script_loop, ())
        self.main_app.set_user_key_code_callback(self.key_code_callback)

    def script_loop(self):
        while True:
            if not self.main_app.Pause:
                self.arranger.script_entry_point()
                # try:
                #
                # except Exception as ep:
                #     logger.error("脚本发生致命错误: %s", ep)

            elif self.cache_img is not None:
                # rect = MyOpenCv.get_real_rect_by_percent_rect(self.cache_img, self.main_app.rect)
                # img2 = MyOpenCv.draw_rect(self.cache_img, rect)
                # img2 = MyOpenCv.show_single_match_pic(img, temp, score, loc)
                # self.main_app.show_image(img2, self.main_app.rect.__str__())
                time.sleep(1)

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


def main_loop(app: MainUI):
    ScriptToolBox(app)


if __name__ == '__main__':
    MainUI(main_loop).myloop()

# 现在您可以使用driver进行网页操作
