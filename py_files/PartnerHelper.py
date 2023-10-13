from __future__ import annotations  # 使用高级注解器，
import os.path
from typing import List, TypeVar, Callable, Generic, Dict, Tuple
import time
import numpy as np

from PyTools.MyAwesomeTool.PyUseCPlus import WinManager, MainUI, MyDllLib, AndroidApp, start_thread, build_logger
from PyTools.MyAwesomeTool.PyUseCPlus import MyOpenCv, Rect, auto_patch_python
from WebDriver import main_loop as cloud_main_loop

logger = build_logger(filename="log.log", name=__name__, use_to_debug=False, file_log_debug=True, use_time_rotate=False)


class Property:
    def __init__(self, name: str, max_skill_time: float, ji_li_weapon: bool):
        self.name = name
        self.max_skill_time = max_skill_time
        self.ji_li_weapon = ji_li_weapon

    def __str__(self):
        return "%s %.2f %d" % (self.name, self.max_skill_time, self.ji_li_weapon)

    @staticmethod
    def get_partner_properties() -> Dict[str, Property]:
        res = {}
        for line in PARTNER_SETTING.split("\n"):
            tuples = line.split("^")
            if len(tuples) > 2:
                proper = Property(tuples[0], float(tuples[1]), tuples[2].__eq__("true"))
                logger.debug(proper.__str__())
                res[proper.name] = proper

        return res


class PartnerHelper:
    def __init__(self, main_app: MainUI):
        self.main_app = main_app
        self.mainManager = WinManager(self.main_app.my_dll, "")
        self.genShenManager = WinManager(self.main_app.my_dll, "原神")
        self.android_app = AndroidApp(True, ANDROID_DEVICE_NAME)
        self.main_app.set_user_key_code_callback(self.user_key_code)
        self.main_app.set_user_key_code_realtime_callback(self.user_realtime_key_code)

        self.partner_properties = Property.get_partner_properties()
        self.skills_cd = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.now_index = 0
        self.isPartnerShipLocked = False
        self.auto_click = False
        self.ship_names = self.get_default_names()
        self.on_buff = False
        self.fill_cd_flag = False
        self.pre_partner_index = 0
        self.rotation_limit = 0  # 帮助草神正好转一圈
        self.keep_rotation = False

        start_thread(self.record_gui_screen_loop, ())
        start_thread(self.draw_loop, ())
        start_thread(self.skills_cd_loop, ())

    def rotation_loop(self, loop_num=1, delay=0):
        if not self.keep_rotation:
            self.keep_rotation = True
        if delay > 0:
            time.sleep(delay)
        num = 0
        while self.keep_rotation:
            for i in range(10):
                self.genShenManager.simulate_mouse_movement()
                time.sleep(0.01)
            num += 1
            if num >= loop_num:
                break

    def clear_sills_cd(self):
        for i in range(4):
            self.skills_cd[i] = 0

        self.on_buff = False
        self.skills_cd[4] = 5

    def skills_cd_loop(self):
        while True:
            for i in range(len(self.skills_cd)):
                if self.skills_cd[i] > 0:
                    self.skills_cd[i] -= 0.1
            time.sleep(0.1)

    def draw_loop(self):
        fresh_index = 0
        while True:
            if self.auto_click:
                self.isPartnerShipLocked = True
                time.sleep(0.5)
                continue

            now_index = self.select_now_index_match()
            self.now_index = now_index if now_index != -1 else self.now_index
            fresh_index = 0

            if self.fill_cd_flag:
                self.fill_cd_flag = False
                self.fill_now_partner_cd()

            for i in range(4):
                name = self.ship_names[i]
                text_color = (255, 255, 255) if i == self.now_index else (0, 0, 0)
                bk_color = (255, 0, 0) if self.skills_cd[i] > 0 else (0, 255, 0)
                div_str = ">" if self.isPartnerShipLocked else ":"
                y_pos = Y_POS_0 + i * Y_DELTA
                show_text = "%.1f%s%s" % (self.skills_cd[i], div_str, name)
                self.mainManager.draw_text(Rect(0.88, y_pos, 1, y_pos + 0.06), show_text, text_color, bk_color)
                self.buff_cd(name, i, text_color)

            self.pre_partner_index = self.now_index

            # fresh_index += 1
            time.sleep(0.002)

    def buff_cd(self, name: str, index: int, text_color):
        if name.__contains__("那维"):
            bk_color = (0, 255, 0) if self.on_buff else (255, 0, 0)
            show_text = "%.1f%s%s" % (self.skills_cd[4], ":", name)
            if self.pre_partner_index != self.now_index:
                if self.now_index == index:
                    self.skills_cd[4] = 10
                    logger.debug("那维-切换到前台")
                elif self.pre_partner_index == index:
                    self.skills_cd[4] = 105 if self.on_buff else 5
                    logger.debug("那维-切换到后台")

            if self.skills_cd[4] <= 0:  # 如果计时归零时，在前台就取消buff，在后台就上buff
                self.on_buff = (self.now_index != index)
            self.mainManager.draw_text(Rect(0, 0, 0.12, 0.06), show_text, text_color, bk_color)

    def record_gui_screen_loop(self):
        self.android_app.play_screen_record_on_phone(WinManager(self.main_app.my_dll, EXT_SCREEN_WIN_NAME, False))

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

    def user_key_code(self, key_code) -> bool:
        if key_code == MyDllLib.VK_F1 + 3:
            img = self.genShenManager.capture_window(None)
            self.main_app.show_image(img)
        elif key_code == 70:  # F
            self.auto_exchange_partner_ship_with_ocr()
        elif key_code == 69:  # E
            time.sleep(0.2)
            self.fill_cd_flag = True
            self.correct_skill_cd_with_ocr()

        elif key_code == 48:  # 0
            self.clear_sills_cd()
        elif key_code == 86:  # V
            self.genShenManager.simulate_mouse_movement()
        elif key_code == 0x28:  # down
            if self.auto_click:
                self.genShenManager.click_point_with_wnd_percent(0.74, 0.72)
                return True
        elif key_code == MyDllLib.VK_OEM_3:
            self.auto_click = not self.auto_click
        elif key_code == 72:  # H
            self.isPartnerShipLocked = not self.isPartnerShipLocked
        elif 49 <= key_code <= 52:  # 1--4
            self.correct_skill_cd_with_ocr()

        return False

    def get_default_names(self) -> List[str]:
        res = []
        for key in self.partner_properties.keys():
            res.append(key)
            if len(res) >= 4:
                break

        return res

    def fill_now_partner_cd(self):
        now_index_save = self.now_index
        name = self.ship_names[now_index_save]
        logger.debug("记录角色[%s]的CD", name)
        p = self.partner_properties[name]
        if p.ji_li_weapon:
            self.skills_cd[now_index_save] = p.max_skill_time
        elif self.skills_cd[now_index_save] <= 0:
            self.skills_cd[now_index_save] = p.max_skill_time

    def auto_exchange_partner_ship_with_ocr(self):
        if self.genShenManager.hwnd <= 0 or self.isPartnerShipLocked:
            return
        w, h = self.genShenManager.get_rect().get_size()
        if w < 1000:
            logger.debug("Wrong YuanShen Windows Size!")
            return
        img = self.genShenManager.capture_window(None)
        w, h = MyOpenCv.get_image_size(img)
        if w < 1000:
            logger.debug("Wrong bmp Size!")
            return
        for row in range(4):
            partner_name = self.list_member_match(img, row)
            self.ship_names[row] = partner_name

    @staticmethod
    def cut_member_image(screen: np.ndarray, row: int = 0) -> np.ndarray:
        temp_start_h = 0.2038 + row * 0.088565
        img, _ = MyOpenCv.cut_picture_with_percent(screen, Rect(0.85677, temp_start_h, 0.91927, temp_start_h + 0.086))
        img = MyOpenCv.color_to_gray(img)
        img = MyOpenCv.threshold(img, 205, 255)
        return img

    def correct_skill_cd_with_ocr(self):
        now_index_save = self.now_index  # 缓存当前选中角色，防止多线程引起索引变动，放心，截图瞬间NowIndex来不及切换
        if self.skills_cd[now_index_save] > 0:  # 尝试修正当前计时
            cd = self.skill_cd_match()
            if cd >= 1:
                logger.debug("number_ocr_cd:%.2f", cd)
                self.skills_cd[now_index_save] = cd
        time.sleep(0.2)

    def skill_cd_match(self) -> float:
        if self.genShenManager.hwnd <= 0 or self.auto_click:
            return -1
        w, h = self.genShenManager.get_rect().get_size()
        if w < 1000:
            logger.debug("Wrong YuanShen Windows Size!")
            return -1

        rect = self.genShenManager.from_percent_rect_get_real_rect(Rect(0.80260, 0.8815, 0.908, 0.974))
        src_mat = self.genShenManager.capture_window(rect)
        temp_path = "templates/E.png"
        temp_mat = MyOpenCv.cv_imread(temp_path)
        score, point = MyOpenCv.match_single_score_and_pos(src_mat, temp_mat)
        if score > 0.9 and point[0] > 15 and point[1] > 51:
            x, y = (point[0] - 15, point[1] - 51)
            roi_rect = Rect(x, y, x + 50, y + 30)

            num_mat = MyOpenCv.cut_picture(src_mat, roi_rect)
            num_mat = MyOpenCv.color_to_gray(num_mat)
            num_mat = MyOpenCv.threshold(num_mat, 245, 255)
            v = self.number_ocr(num_mat.copy())
            self.main_app.show_image(num_mat, "推断:%.2f" % v)
            return v

        else:
            return -1

    @staticmethod
    def number_ocr(num_mat: np.ndarray):

        match_num_seq = [8, 9, 6, 3, 4, 5, 2, 7, 0, 1]
        max_score = 99
        threshold = 0.77
        round_num = 0
        tuples = (0, 0, 0)
        x_list = []
        num_list = []
        fill_black_rect = Rect(0, 0, 0, 0)
        while max_score >= threshold and round_num < 3:
            round_num += 1
            max_score = 0
            for i in range(10):
                now_num = match_num_seq[i]
                path = "templates/number/%d.png" % now_num
                temp_mat = MyOpenCv.cv_imread(path)
                score, loc = MyOpenCv.match_single_score_and_pos(num_mat, temp_mat)
                # logger.debug("match: (%d):(%.4f)", now_num, score)
                if score >= threshold and score > max_score:
                    max_score = score
                    w, h = MyOpenCv.get_image_size(temp_mat)
                    x, y = loc
                    fill_black_rect = Rect(x, y, x + w, y + h)
                    tuples = (loc[0], loc[1], now_num)

                    break
            if max_score >= threshold:
                num_mat = MyOpenCv.fill_black_to_src(num_mat, fill_black_rect)
                x_list.append(tuples[0])
                num_list.append(tuples[2])
                # logger.debug("get number:(%d)(%.4f)", tuples[2], max_score)

        x_list = np.array(x_list)
        num_list = np.array(num_list)
        index = x_list.argsort()
        num_list = num_list[index]
        k = 0.1
        sum_v = 0.0
        for num in reversed(num_list):
            sum_v += k * num
            k *= 10
        return sum_v

    def list_member_match(self, screen: np.ndarray, row: int = 0) -> str:
        src_mat = self.cut_member_image(screen, row)

        for key in self.partner_properties.keys():
            temp_path = "templates/partner/%s.png" % key
            if not os.path.exists(temp_path):
                continue
            temp_mat = MyOpenCv.cv_imread(temp_path)
            score, loc = MyOpenCv.match_single_score_and_pos(src_mat, temp_mat)
            logger.debug("(row:%d)(path:%s) score:(%.4f)", row, temp_path, score)
            if score > 0.8:
                return key

        # 如果没有匹配成功则保存当前截图分片，进行人工分析
        temp_path = "templates/partner/Unknown-Line-%d.png" % row
        if not os.path.exists(temp_path):
            MyOpenCv.cv_im_write(temp_path, src_mat)

        return self.ship_names[row]  # 找不到则不切换角色

    def select_now_index_match(self):
        if self.genShenManager.hwnd <= 0 or self.auto_click:
            return -1
        w, h = self.genShenManager.get_rect().get_size()
        if w < 1000:
            return -1
        rect = self.genShenManager.from_percent_rect_get_real_rect(Rect(0.90208, 0.2389, 0.91719, 0.5352))
        step = (rect.bottom - rect.top) / 4.0
        # logger.debug(rect.__str__())
        src_mat = self.genShenManager.capture_window(None)
        src_mat, _ = MyOpenCv.cut_picture_with_percent(src_mat, Rect(0.90208, 0.2389, 0.91719, 0.5352))
        src_mat = MyOpenCv.color_to_gray(src_mat)
        src_mat = MyOpenCv.threshold(src_mat, 225, 255)
        temp_path = "templates/select.png"
        temp_mat = MyOpenCv.cv_imread(temp_path)
        score, loc = MyOpenCv.match_single_score_and_pos(src_mat, temp_mat)

        if score < 0.74:
            return -1
        for i in range(4):
            top = i * step
            bottom = top + step
            # log_str = "[%.2f,%d,%d][%.2f,%.2f]" % (score, loc[0], loc[1],top,bottom)
            # logger.debug(log_str)
            if top < loc[1] < bottom:
                # logger.debug("当前选中的角色为:%s %.2f", self.ship_names[i], score)
                self.main_app.show_image(src_mat, "当前选中的角色为:%s" % self.ship_names[i])
                return i

        return -1


def main_loop(main_ui: MainUI):
    PartnerHelper(main_ui)


USE_CLOUD = False
Y_POS_0 = 0.24
Y_DELTA = 0.085
ANDROID_DEVICE_NAME = "QWBILZRGSW7XXCV4"
EXT_SCREEN_WIN_NAME = "python黑客工具箱"
PARTNER_SETTING = """
胡桃^16^false^
宵宫^18^false^
雷神^10^false^
草神^6^true^
夜兰^10^false^
神里^10^-false^
甘雨^10^false^
魈^10^false^
钟离^12^false^
辛炎^18^false^
迪奥娜^15^true^
温迪^6^true^
七七^30^false^
刻晴^7^false^
莫娜^12^false^
迪卢克^10^false^
琴^6^false^
砂糖^15^true^
重云^15^false^
女仆^24^false^
心海^20^false^
班尼特^5^false^
皇女^25^false^
那维^12^false^
凝光^12^false^
行秋^21^true^
北斗^8^false^
罗莎^6^false^
万叶^10^false^
香菱^12^false^
雷泽^10^false^
早柚^11^false^
九条^10^false^
芭芭拉^32^false^
"""


def main():
    auto_patch_python(globals(), patch_path="./settings.py")
    if USE_CLOUD:
        MainUI(cloud_main_loop).myloop()
    else:
        MainUI(main_loop).myloop()


if __name__ == '__main__':
    main()
