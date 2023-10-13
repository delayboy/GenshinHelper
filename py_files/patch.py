import time

from WebDriver import *


class ManyScriptArranger:

    def __init__(self, box: ScriptToolBox):
        self.temp_file_path = os.path.dirname(os.path.abspath("./templates")) + "/cloud_templates/"  # 获取临时文件夹在电脑上的绝对路径
        self.taskTotalReward = 0
        self.taskErrorReward = 0
        self.taskSuccess: Dict[int] = {}
        self.box = box
        self.taskId = 0
        self.pre_action_info = {}

    def get_pre_action_info(self, key: str):
        if self.pre_action_info.__contains__(key):
            return self.pre_action_info[key]
        return None

    def set_task_success(self):
        if not self.taskSuccess.__contains__(self.taskId):
            self.taskSuccess[self.taskId] = 1

    def task_is_100_over(self):
        return self.taskSuccess.__contains__(self.taskId) and self.taskSuccess[self.taskId] > 1

    def capture_screen(self) -> np.ndarray:
        return self.box.manager.capture_window_with_other_manager(self.box.main_manager)

    def _match_sub_pos_and_do(self, temp_path: str, src_mat: np.ndarray, percent_rect: Rect, threshold: float = 0.85,
                              sleep_time: int = 1,
                              is_final: bool = True,
                              reward: int = -1,
                              call_back: Callable[[np.ndarray, Tuple[float, float], str], None] = None,
                              action_alias_name: str = None) -> bool:
        if call_back is None:
            call_back = self.default_action_route
        if action_alias_name is None:
            action_alias_name = temp_path

        temp = MyOpenCv.cv_imread(self.temp_file_path + temp_path, cv2.IMREAD_UNCHANGED)
        src_sub_mat, rect = MyOpenCv.cut_picture_with_percent(src_mat, percent_rect)
        score, loc = MyOpenCv.match_single_score_and_pos(src_sub_mat, temp)
        loc = (loc[0] + int(rect.left), loc[1] + int(rect.top))
        logger.debug(rect.__str__())
        img = MyOpenCv.draw_rect(src_mat, rect)
        img = MyOpenCv.show_single_match_pic(img, temp, score, loc)
        now = datetime.datetime.now()
        large_than = '>' if score > threshold else '<'
        log_text = "[%s]--%d,%d--[%.2f %s %.2f]--%d--%s" % (
            now, self.taskTotalReward, self.taskErrorReward, score, large_than, threshold, self.taskId,
            action_alias_name)
        logger.debug(log_text)
        self.box.cache_img = img
        self.box.main_app.show_image(img, log_text)
        if score > threshold:
            # self.vmManager.clickPointWithTemplates(temp, loc, 0.5, 0.5)
            call_back(temp, loc, action_alias_name)
            time.sleep(sleep_time)
            if reward < 0:
                self.taskErrorReward += reward
            else:
                self.taskTotalReward += reward
            self.default_final_exit(is_final)
            return True
        return False

    def _match_pos_and_do(self, temp_path: str, src_mat: np.ndarray, threshold: float = 0.85, sleep_time: int = 1,
                          is_final: bool = True,
                          reward: int = -1,
                          call_back: Callable[[np.ndarray, Tuple[float, float], str], None] = None,
                          action_alias_name: str = None) -> bool:

        return self._match_sub_pos_and_do(temp_path, src_mat, Rect(0, 0, 1, 1), threshold, sleep_time, is_final, reward,
                                          call_back, action_alias_name)

    def jump_walk_front_in_game(self, use_left=False):
        self.box.manager.send_key_code(True, 87)  # w
        self.box.manager.send_key_code(True, 0x20)  # space
        if use_left:
            self.box.manager.send_key_code(True, 65)
        time.sleep(1)
        if use_left:
            self.box.manager.send_key_code(False, 65)
        self.box.manager.send_key_code(False, 87)
        self.box.manager.send_key_code(False, 0x20)
        time.sleep(1)

    @staticmethod
    def default_final_exit(is_final: bool = True):
        if is_final:
            raise KeyboardInterrupt("一旦匹配成功就推出了")

    def jump_to_next_task(self, normal_exit: bool = False):
        if self.taskSuccess.__contains__(self.taskId):
            if self.taskSuccess[self.taskId] <= 1:
                logger.info(f'任务{self.taskId}成功完成')
                self.taskSuccess[self.taskId] = 100
        else:
            logger.info(f'-------任务{self.taskId}执行失败-------')

        if not normal_exit:
            while self.box.driver.close_current_tab_and_switch():
                pass

            img = self.capture_screen()
            if not self._match_pos_and_do("原神.png", img, 0.8, 2, False, 0, action_alias_name="什么都不干"):
                self.box.driver.go_url()
                logger.debug("未找到原神视图重新回到主页")
                time.sleep(2)

        self.taskId += 1
        self.taskErrorReward = 0
        self.taskTotalReward = 0

    def script_entry_point(self):
        try:
            # self.loop_only_one_script()
            self.do_mi_you_she_task()
            self.do_yuan_shen_task()
            self.do_tie_dao_task()
            self.do_idle_task()
        except KeyboardInterrupt:
            pass

    @staticmethod
    def get_key_code(key_str: str):
        return key_str.encode("gbk")[0]

    def key_code_callback(self, key_code: int):
        if key_code == MyDllLib.VK_F1 + 2:
            img = self.capture_screen()
            MyOpenCv.cv_im_write('整机截图.png', img)
        if self.get_key_code('0') <= key_code <= self.get_key_code('9'):
            self.taskId = key_code - self.get_key_code('0')
            logger.debug("jump to taskID:%d", self.taskId)

    def do_idle_task(self):
        now = datetime.datetime.now()  # now += datetime.timedelta(seconds=1)
        if 2 <= now.hour <= 5:  # 凌晨2:00到5:00之间停止所有任务
            self.taskSuccess = {}
            self.taskErrorReward = -100
            return True

        if self.taskErrorReward < -20:
            self.box.driver.close()
            time.sleep(1)
            self.box.driver = MyWebDriver(self.box.my_dll)
            time.sleep(1)
            self.box.driver.go_url()
            time.sleep(1)
            self.box.manager = WinManager(self.box.my_dll, "网易云", False)
            if self.box.manager.hwnd != 0:
                self.taskErrorReward = 0
                logger.info(f'重启网易云游戏')
            else:
                logger.error(f'致命错误：网易云游戏无法重启')
                exit(-1)

        img = self.capture_screen()
        self._match_sub_pos_and_do("close.png", img, Rect(0.8, 0, 1, 1), 0.9)

        if self._match_pos_and_do("原神.png", img, 0.8, 5, False, 0, action_alias_name="什么都不干"):
            if self.taskTotalReward < 65530:
                self.taskTotalReward += 1
        else:
            if len(self.box.driver.driver.window_handles) <= 1:
                self.box.manager.click_point_with_wnd_percent(0.5, 0.5, click=False)
                self.box.my_dll.scroll_mouse(-120)
            self.taskErrorReward -= 1
            time.sleep(1)

        # 在每天的7:00-18:00之间，每隔2小时重新做一遍任务。
        if 7 <= now.hour <= 18 and (self.taskTotalReward > 60 * 24):  # or self.taskErrorReward < -20
            self.taskTotalReward = 0
            self.taskErrorReward = 0
            self.taskId = 1

    # 某人的脚本收尾函数，包括自动寻找启动图标，自动点击固定点，异常累加与异常退出
    def default_action_simple_click_or_scroll_mouse(self):
        # 滚动寻找启动图标
        if len(self.box.driver.driver.window_handles) <= 1:
            self.box.manager.click_point_with_wnd_percent(0.5, 0.5, click=False)
            self.box.my_dll.scroll_mouse(-120)
        else:  # 自动点击固定位置
            self.box.manager.click_point_with_wnd_percent(0.42, 0.42)

        self.taskErrorReward -= 1
        time.sleep(2)
        self.default_final_exit()

    def do_mi_you_she_task(self):
        if not (self.taskId == 1):
            return False

        # if self.task_is_100_over():
        #     self.jump_to_next_task()
        #     return False

        if self.taskErrorReward < -50 or self.taskTotalReward > 100:
            self.jump_to_next_task()
            return False

        img = self.capture_screen()
        self._match_pos_and_do("各种绿色按钮.png", img, 0.92)
        self._match_pos_and_do("各种绿色按钮2.png", img, 0.92)
        self._match_sub_pos_and_do("close.png", img, Rect(0.8, 0, 1, 1), 0.9)

        self._match_pos_and_do("米友社各种蓝色按钮.png", img, 0.9)
        self._match_pos_and_do("签到福利.png", img, reward=2, sleep_time=2)
        self._match_pos_and_do("米游社.png", img, reward=2, sleep_time=2)

        self._match_pos_and_do("福利.png", img, 0.92, reward=20)

        self._match_pos_and_do("云手机.png", img)

        self.default_action_simple_click_or_scroll_mouse()

    def do_tie_dao_task(self):
        if not (5 <= self.taskId <= 7):
            return False

        if self.taskErrorReward < -100 or self.taskTotalReward > 100:
            constrain = (5 <= self.taskId + 1 <= 7)
            self.jump_to_next_task(constrain)
            return False

        img = self.capture_screen()

        self._match_pos_and_do("各种绿色按钮.png", img, 0.92)
        self._match_pos_and_do("各种绿色按钮2.png", img, 0.92)
        self._match_sub_pos_and_do("close.png", img, Rect(0.8, 0, 1, 1), 0.9)

        self.铁道派遣任务5(img)
        self.铁道每日任务奖励领取6(img)
        self.铁道纪行奖励领取7(img)
        self._match_pos_and_do("铁道.png", img, 0.8, action_alias_name="原神启动")
        self.default_action_simple_click_or_scroll_mouse()

    def 铁道派遣任务5(self, img: np.ndarray):
        if not 5 == self.taskId:
            return False

        self._match_pos_and_do("铁道白色再次派遣按钮.png", img, 0.85)
        self._match_pos_and_do("铁道黄色派遣领取按钮.png", img, 0.85)
        self._match_sub_pos_and_do("铁道左上角手机图标.png", img, Rect(0.00, 0.18, 0.10, 0.32), 0.83)
        self._match_pos_and_do("铁道委托图标.png", img, 0.85)
        self._match_pos_and_do("铁道派遣中按钮.png", img, 0.85, reward=20, action_alias_name="标记本次任务已完成")

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

    def 铁道纪行奖励领取7(self, img: np.ndarray):
        if not 7 == self.taskId:
            return False
        self._match_pos_and_do("铁道纪行一键领取黄色按钮.png", img, 0.85)
        self._match_pos_and_do("铁道左上角纪行图标.png", img, 0.85, reward=20, action_alias_name="左上角纪行图标.png")
        self._match_sub_pos_and_do("铁道右上角纪行图标.png", img, Rect(0.6, 0.2, 0.86, 0.32), 0.9)
        self._match_pos_and_do("铁道左上角每日实训图标.png", img, 0.85, action_alias_name="铁道各种叉号退出")

    def loop_only_one_script(self):
        img = self.capture_screen()

        self._match_pos_and_do("各种绿色按钮.png", img, 0.92)
        self._match_pos_and_do("各种绿色按钮2.png", img, 0.92)
        self._match_sub_pos_and_do("close.png", img, Rect(0.8, 0, 1, 1), 0.9)
        self._match_sub_pos_and_do("派蒙.png", img, Rect(0.02, 0.18, 0.10, 0.32), action_alias_name="砍树")

        self._match_pos_and_do("原神.png", img, 0.8, action_alias_name="原神启动")
        self._match_sub_pos_and_do("原神开始界面的退出按钮.png", img, Rect(0.90, 0.78, 0.96, 0.86))

        self.default_action_simple_click_or_scroll_mouse()

    def do_yuan_shen_task(self):
        if not (2 <= self.taskId <= 4):
            return False

        if self.taskErrorReward < -100 or self.taskTotalReward > 100:
            constrain = (2 <= self.taskId + 1 <= 4)
            self.jump_to_next_task(constrain)
            return False

        img = self.capture_screen()

        self._match_pos_and_do("各种绿色按钮.png", img, 0.92)
        self._match_pos_and_do("各种绿色按钮2.png", img, 0.92)
        self._match_sub_pos_and_do("close.png", img, Rect(0.8, 0, 1, 1), 0.9)

        self.获取尘歌壶每日货币原神任务2(img)
        self.进行探索派遣原神任务3(img)
        self.原神纪行领取任务4(img)

        self._match_pos_and_do("原神.png", img, 0.8, action_alias_name="原神启动")
        self._match_sub_pos_and_do("原神开始界面的退出按钮.png", img, Rect(0.90, 0.78, 0.96, 0.86))

        self.default_action_simple_click_or_scroll_mouse()

    def 获取尘歌壶每日货币原神任务2(self, img: np.ndarray):
        if not (2 == self.taskId):
            return False

        self._match_sub_pos_and_do("尘歌壶钱币.png", img, Rect(0.38, 0.66, 0.52, 0.74), 0.88, reward=50)
        self._match_sub_pos_and_do("尘歌壶币池.png", img, Rect(0.34, 0.68, 0.56, 0.90), 0.88, reward=50)
        self._match_pos_and_do("信任等阶对话气泡.png", img, 0.9)
        self._match_pos_and_do("阿圆对话气泡.png", img, 0.9)
        self._match_sub_pos_and_do("尘歌壶UI.png", img, Rect(0.58, 0.18, 0.82, 0.32), 0.85)
        self._match_sub_pos_and_do("黄黑键传送.png", img, Rect(0.68, 0.76, 0.92, 0.9), 0.85)
        self._match_sub_pos_and_do("宅邸对话框弹出图标.png", img, Rect(0.56, 0.52, 0.8, 0.66), 0.85)
        self._match_sub_pos_and_do("宅邸地图图标.png", img, Rect(0.44, 0.50, 0.58, 0.62), 0.85)
        self._match_sub_pos_and_do("原神地图尘哥壶三个字.png", img, Rect(0.68, 0.76, 0.82, 0.88), 0.85)
        self._match_sub_pos_and_do("原神地图两个字.png", img, Rect(0.66, 0.18, 0.84, 0.30), 0.85,
                                   action_alias_name="鼠标向上滑动")
        self._match_sub_pos_and_do("罗盘.png", img, Rect(0.88, 0.78, 0.98, 0.90), 0.92)
        self._match_sub_pos_and_do("派蒙.png", img, Rect(0.02, 0.18, 0.10, 0.32), action_alias_name="打开小地图")
        self._match_sub_pos_and_do("原神地图右上角退出按钮.png", img, Rect(0.92, 0.16, 1, 0.30), 0.85)

    def 进行探索派遣原神任务3(self, img: np.ndarray):
        if not (3 == self.taskId):
            return False
        self._match_pos_and_do("左上角角色选择.png", img)
        self._match_sub_pos_and_do("20小时派遣.png", img, Rect(0.80, 0.64, 0.98, 0.80), 0.98)
        self._match_pos_and_do("探索派遣选择角色.png", img)
        self._match_pos_and_do("探索派遣领取.png", img)

        self._match_sub_pos_and_do("探索派遣对话气泡.png", img, Rect(0.60, 0.42, 0.76, 0.64), 0.85)
        self._match_pos_and_do("凯瑟琳对话气泡.png", img, 0.88, reward=10)
        self._match_pos_and_do("传送锚点对话气泡.png", img, 0.85)
        self._match_sub_pos_and_do("黄黑键传送.png", img, Rect(0.68, 0.76, 0.92, 0.9), 0.85)
        self._match_sub_pos_and_do("原神大地图的传送锚点图标.png", img, Rect(0.46, 0.46, 0.54, 0.62), 0.92)
        self._match_pos_and_do("原神蒙德两个字.png", img, 0.85)
        self._match_sub_pos_and_do("原神地图两个字.png", img, Rect(0.66, 0.18, 0.84, 0.30), 0.85, sleep_time=2,
                                   action_alias_name="鼠标向下滑动")
        self._match_sub_pos_and_do("大地图右下角的尘歌壶图标.png", img, Rect(0.88, 0.76, 1, 0.88), 0.85)
        self._match_pos_and_do("尘歌壶UI.png", img, 0.85, action_alias_name="打开小地图")
        self._match_pos_and_do("再见对话气泡.png", img, 0.85)
        self._match_sub_pos_and_do("原神圆形的叉号按钮.png", img, Rect(0.68, 0.18, 1, 0.38), 0.85)
        self._match_pos_and_do("猫尾酒馆对话气泡.png", img, 0.9, action_alias_name="斜跑跳")
        self._match_sub_pos_and_do("派蒙.png", img, Rect(0.02, 0.18, 0.10, 0.32), reward=-2, action_alias_name="跳跑")

    def 原神纪行领取任务4(self, img: np.ndarray):
        if not (4 == self.taskId):
            return False
        self._match_pos_and_do("纪行一键领取.png", img, 0.85)
        self._match_pos_and_do("再见对话气泡.png", img, 0.85)
        # 因为纪行图标是纯白色的，如果不好匹配之后可以对img做一下阈值提取   img2 = cv2.threshold(img, 245, 255, cv2.THRESH_BINARY)
        self._match_sub_pos_and_do("右上角纪行图标.png", img, Rect(0.54, 0.20, 0.80, 0.28), 0.93)
        self._match_pos_and_do("左上角纪行图标.png", img, 0.85, reward=20)
        self._match_sub_pos_and_do("原神圆形的叉号按钮.png", img, Rect(0.68, 0.18, 1, 0.38), 0.85)

    def default_action_route(self, temp: np.ndarray, loc: tuple, action_alias_name: str):
        now_action_info = {}
        if action_alias_name.__eq__("福利.png"):
            self.box.manager.click_point_with_templates(temp, loc)
            self.set_task_success()
        elif action_alias_name.__eq__("云手机.png") or action_alias_name.__eq__("原神启动"):
            self.box.manager.click_point_with_templates(temp, loc, percent_y=2)
        elif action_alias_name.__eq__("原神开始界面的退出按钮.png"):
            self.box.manager.click_point_with_wnd_percent(0.42, 0.42)
        elif action_alias_name.__eq__("尘歌壶钱币.png") or action_alias_name.__eq__("尘歌壶币池.png"):
            self.box.manager.click_point_with_wnd_percent(0.44, 0.8)
            time.sleep(1)
            self.box.manager.click_point_with_wnd_percent(0.92, 0.72)
            time.sleep(1)
            self.box.manager.click_point_with_wnd_percent(0.18, 0.22)
            self.set_task_success()
        elif action_alias_name.__eq__("尘歌壶UI.png"):
            self.box.manager.click_point_with_wnd_percent(0.2, 0.72)
        elif action_alias_name.__eq__("打开小地图"):
            self.box.manager.click_point_with_wnd_percent(0.12, 0.28)
            # self.box.manager.click_point_with_templates(temp, loc, percent_x=3, percent_y=3)
        elif action_alias_name.__eq__("鼠标向上滑动"):
            self.box.manager.click_point_with_templates(temp, loc, 1, 7, click=False)
            time.sleep(1)
            self.box.manager.drag_mouse(0, -30)
        elif action_alias_name.__eq__("鼠标向下滑动"):
            self.box.manager.click_point_with_templates(temp, loc, 1, 7, click=False)
            time.sleep(1)
            self.box.manager.drag_mouse(0, 30)
        elif action_alias_name.__eq__("什么都不干"):
            pass
        elif action_alias_name.__eq__("跳跑"):
            self.jump_walk_front_in_game(False)
        elif action_alias_name.__eq__("斜跑跳"):
            self.jump_walk_front_in_game(True)
        elif action_alias_name.__eq__("假装点击"):
            self.box.manager.click_point_with_templates(temp, loc, click=False)
        elif action_alias_name.__eq__("探索派遣选择角色.png"):
            self.box.manager.click_point_with_wnd_percent(0.92, 0.74)
            time.sleep(2)
            self.box.manager.click_point_with_templates(temp, loc)
        elif action_alias_name.__eq__("左上角角色选择.png"):
            percent_y = self.get_pre_action_info("percent_y")
            percent_y = 1.5 if percent_y is None else percent_y + 0.5
            self.box.manager.click_point_with_templates(temp, loc, percent_y=percent_y)
            now_action_info["percent_y"] = percent_y
        elif action_alias_name.__eq__("左上角纪行图标.png"):
            self.box.manager.click_point_with_wnd_percent(0.06, 0.42)
            self.set_task_success()
        elif action_alias_name.__eq__("凯瑟琳对话气泡.png"):
            self.box.manager.click_point_with_templates(temp, loc)
            self.set_task_success()
        elif action_alias_name.__eq__("标记本次任务已完成"):
            self.set_task_success()
        elif action_alias_name.__eq__("铁道各种叉号退出"):
            self.box.manager.click_point_with_wnd_percent(0.96, 0.22)
        elif action_alias_name.__eq__("砍树"):
            time.sleep(5)
            self.box.manager.click_point_with_wnd_percent(0.32, 0.82)
            time.sleep(5)
            self.box.manager.click_point_with_templates(temp, loc)
            time.sleep(2)
            self.box.manager.click_point_with_wnd_percent(0.04, 0.84)
            time.sleep(2)
            self.box.manager.click_point_with_wnd_percent(0.6, 0.72)
            time.sleep(2)

        else:
            self.box.manager.click_point_with_templates(temp, loc)

        self.pre_action_info = now_action_info
