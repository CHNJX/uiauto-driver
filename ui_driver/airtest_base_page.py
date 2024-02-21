# @Time     :2024/2/18 12:38
# @Author   :CHNJX
# @File     :command.py
# @Desc     :页面共用
from airtest.core.api import *

from ui_driver.utils.logger import Logger
from airtest.core.api import swipe
from airtest.core.api import device
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import cv2
from skimage.metrics import structural_similarity as compare_ssim
import pytesseract
import numpy as np
import logging
from PIL import Image


class BasePage:
    device_ip = ''
    _device_instance = None  # 用于存储设备连接的单例

    def __init__(self):
        # 当前获取的元素
        self._element = None
        # 当前各种结果
        self._result = None
        # 当前的截图对象
        self.screen = None
        self.logger = self._setup_logger()
        self.device = self._setup_device(self.device_ip)
        self.poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        self.page_dir = os.path.join(os.path.dirname(__file__), '../resources/page/')

    def _setup_logger(self):
        logger = logging.getLogger("airtest")
        logger.setLevel(logging.ERROR)
        return Logger().get_logger()

    @classmethod
    def _setup_device(cls, device_ip):
        if cls._device_instance is None or (device_ip and cls._device_instance.device_ip != device_ip):
            try:
                cls._device_instance = connect_device(f"Android:///{device_ip}")
                cls._device_instance.device_ip = device_ip  # 存储设备IP为了后续比较
            except Exception as e:
                logging.error(f"Failed to connect to device: {device_ip}. Error: {e}")
                raise e
        return cls._device_instance

    def find_image(self, image_path, similarity=0.995):
        """使用图片查找元素"""
        self.logger.info(f"查找图片：{image_path}")
        self._result = exists(Template(image_path, threshold=similarity))
        return self._result

    def is_image_exist(self, image_path, similarity=0.995):
        res = self.find_image(image_path, similarity)
        self._result = res is not None and len(res) != 0
        return self._result

    def click_image(self, image_path):
        """点击图片标识的元素"""
        assert_exists(Template(image_path), f"Element {image_path} not found")
        self.logger.info(f"点击元素：{image_path}")
        touch(Template(image_path))
        return self

    # @handle_exception
    def find_element(self, locator, timeout=10):
        """使用 Poco 定位器查找元素"""
        self.logger.info(f'查找元素 locator:{locator}')
        try:
            self.poco(**locator).wait_for_appearance(timeout)
        except Exception as e:
            self.logger.error(f'查找元素失败,locator:{locator}')
            self.logger.error(e.__str__())
            self.logger.info('开始判断是否有存在黑名单元素')
            raise e
        self._element = self.poco(**locator)
        return self._element

    def click(self):
        """点击元素"""
        self._element.click()
        return self

    def find_and_click(self, locator):
        """使用 Poco 定位器点击元素"""
        self.find_element(locator).click()
        return self

    def input(self, input_text: str):
        self._element.set_text(input_text)
        return self

    def find_and_input(self, locator: str, input_text: str):
        self.find_element(locator).set_text(input_text)
        return self

    def get_ele_text(self):
        """返回元素文本"""
        self._result = self._element.attr('text')
        return self

    def assert_element(self, image_path, msg, similarity=0.995):
        """断言元素存在"""
        assert_exists(Template(image_path, threshold=similarity), msg=msg)

    def click_back(self):
        ...
        return self

    def swipe_vertical(self, direction: str):
        """
        竖屏滑动操作
        :param direction: 滑动方向
        :return:
        """
        display_info = device().display_info
        screen_width = display_info['width']
        screen_height = display_info['height']
        if direction == 'up':
            self.logger.info(f"向上滑动")
            swipe([screen_width / 2, screen_height * 3 / 4], [screen_width / 2, screen_height / 4])
        elif direction == 'down':
            self.logger.info(f"向下滑动")
            swipe([screen_width / 2, screen_height / 4], [screen_width / 2, screen_height * 3 / 4])
        elif direction == 'left':
            self.logger.info(f"向左滑动")
            swipe([screen_width * 3 / 4, screen_height / 2], [screen_width / 4, screen_height / 2])
        elif direction == 'right':
            self.logger.info(f"向右滑动")
            swipe([screen_width / 4, screen_height / 2], [screen_width * 3 / 4, screen_height / 2])
        return self

    def swipe_horizontal(self, direction: str):
        """
        横屏滑动操作
        :param direction: 滑动方向
        :return:
        """
        display_info = device().display_info
        screen_width = display_info['width']
        screen_height = display_info['height']

        # 在横屏模式下，宽度和高度的概念是相反的
        if direction == 'up':  # 在横屏模式下，上滑实际是向左滑
            self.logger.info(f"横屏模式下向上（左）滑动")
            swipe([screen_height / 2, screen_width * 3 / 4], [screen_height / 2, screen_width / 4], duration=1)
        elif direction == 'down':  # 在横屏模式下，下滑实际是向右滑
            self.logger.info(f"横屏模式下向下（右）滑动")
            swipe([screen_height / 2, screen_width / 4], [screen_height / 2, screen_width * 3 / 4], duration=1)
        elif direction == 'left':  # 在横屏模式下，左滑实际是向下滑
            self.logger.info(f"横屏模式下向左（下）滑动")
            swipe([screen_height * 3 / 4, screen_width / 2], [screen_height / 4, screen_width / 2], duration=1)
        elif direction == 'right':  # 在横屏模式下，右滑实际是向上滑
            self.logger.info(f"横屏模式下向右（上）滑动")
            swipe([screen_height / 4, screen_width / 2], [screen_height * 3 / 4, screen_width / 2], duration=1)

        return self

    def swipe_to_target(self, direction: str, targets: tuple[str]):
        """
        滑动到目标位置
        """
        self.logger.info(f'Swiping screen to find targets: {targets}')
        while not self._are_targets_found(targets):
            before_screen = self.get_current_screen()
            self._swipe_screen(direction)
            after_screen = self.get_current_screen()

            if self.compare_screens(before_screen, after_screen):
                self.logger.error('Reached end of screen without finding targets')
                raise Exception('Target elements not found')

    def _are_targets_found(self, targets):
        """
        查看是否存在目标元素
        """
        return any(self.find_image(target) for target in targets)

    def _swipe_screen(self, direction):
        display_info = device().display_info
        width, height = display_info['width'], display_info['height']
        center_x, center_y = width / 2, height / 2

        swipe_start_end = {
            'up': [(center_x, height * 3 / 4), (center_x, height / 4)],
            'down': [(center_x, height / 4), (center_x, height * 3 / 4)],
            # Add other directions if needed
        }
        swipe(*swipe_start_end[direction])

    def get_current_screen(self, image_name=None):
        # 获取当前屏幕的快照
        self.logger.info('进行截图')
        screen_pil = G.DEVICE.snapshot()  # 返回PIL格式的图像
        if screen_pil is None:
            raise ValueError("Failed to capture screen")

        # 保存截图到本地
        if image_name is not None:
            cv2.imwrite(f'resource/screen/{image_name}.jpg', screen_pil)
            self.logger.info(f'截图已保存到 resource/screen/{image_name}')
        # 将PIL图像转换为OpenCV格式
        self.screen = cv2.cvtColor(np.array(screen_pil), cv2.COLOR_RGB2BGR)

        return self.screen

    def compare_screens(self, screen1, screen2, threshold=0.99):
        """比较两张图片流是否一致"""
        # 检查图像是否为空
        if screen1 is None or screen2 is None:
            raise ValueError("One of the input images is empty")

        # 将图像转换为灰度，因为SSIM比较通常在灰度图像上进行
        gray1 = cv2.cvtColor(screen1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(screen2, cv2.COLOR_BGR2GRAY)

        # 计算两个灰度图像之间的SSIM
        ssim_index, _ = compare_ssim(gray1, gray2, full=True)

        # 如果SSIM值高于阈值，则认为屏幕没有显著变化
        return ssim_index >= threshold

    def compare_image(self, page_name, image1: str, image2: str, threshold=0.99):

        image_base_dir = 'resource/'
        if image1.startswith('screen'):
            image_path1 = image_base_dir + 'screen/' + image1[7:]
        else:
            image_path1 = image_base_dir + f'{page_name}/' + image1
        screen1 = cv2.imread(image_path1 + '.jpg')
        if image2.startswith('screen'):
            image_path2 = image_base_dir + 'screen/' + image2[7:]
        else:
            image_path2 = image_base_dir + f'{page_name}/' + image2
        screen2 = cv2.imread(image_path2 + '.jpg')
        self._result = self.compare_screens(screen1, screen2, threshold)
        return self._result

    def back(self):
        keyevent('BACK')
        return self

    def wait(self, second):
        sleep(second)

    def close_device(self):
        self.device.disconnect()

    def into_page_with_diff_lan(self, *args):
        """
        根据不通用语言，点击不同的入口图片
        :param args: 不同语言的图片
        :return: self
        """
        for image in args:
            if self.find_image(image):
                self.click(image)
                break

    def into_page_with_diff_lan_swipe(self, direction, *args):
        """
        根据不通用语言，点击不同的入口图片，需要进行滑动
        :param direction: 方向
        :param args: 不同语言图片
        :return:
        """
        self.swipe_to_target(direction, *args)
        self.into_page_with_diff_lan(*args)

    def get_str_from_img(self, img):
        """
        识别图中文字信息
        :param img: 图片路径
        :return:
        """
        read_img = cv2.imread(img)
        gray = cv2.cvtColor(read_img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 3)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        gray = cv2.medianBlur(gray, 3)
        img_text = pytesseract.image_to_string(gray, lang='eng')
        return img_text

    def snapshot(self, image_name=None):
        """截取当前页面"""
        snapshot(image_name)
        return self

    def ocr(self, region=None):
        # 如果没有指定区域，OCR 整个屏幕
        if region is None:
            screen = self.device.snapshot()  # 获取整个屏幕的截图
            image = Image.fromarray(screen)
        else:
            # 指定区域的 OCR
            x, y, width, height = region
            screen = self.device.snapshot(quality=100, filename=None)  # 获取高质量截图
            image = Image.fromarray(screen)
            image = image.crop((x, y, x + width, y + height))

        # 对截取的图像应用 OCR
        return pytesseract.image_to_string(image)
