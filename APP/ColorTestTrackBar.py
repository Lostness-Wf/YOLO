import cv2
import numpy as np


def create_trackbars(window_name):
    cv2.createTrackbar('Lower H', window_name, 0, 180, lambda x: None)
    cv2.createTrackbar('Lower S', window_name, 0, 255, lambda x: None)
    cv2.createTrackbar('Lower V', window_name, 0, 255, lambda x: None)
    cv2.createTrackbar('Upper H', window_name, 180, 180, lambda x: None)
    cv2.createTrackbar('Upper S', window_name, 255, 255, lambda x: None)
    cv2.createTrackbar('Upper V', window_name, 255, 255, lambda x: None)


def get_trackbar_values(window_name):
    l_h = cv2.getTrackbarPos('Lower H', window_name)
    l_s = cv2.getTrackbarPos('Lower S', window_name)
    l_v = cv2.getTrackbarPos('Lower V', window_name)
    u_h = cv2.getTrackbarPos('Upper H', window_name)
    u_s = cv2.getTrackbarPos('Upper S', window_name)
    u_v = cv2.getTrackbarPos('Upper V', window_name)
    return (l_h, l_s, l_v), (u_h, u_s, u_v)


def color_adjustment(img_path):
    # 读取图像
    img = cv2.imread(img_path)
    if img is None:
        print("错误：无法读取图像")
        return

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # 创建窗口
    cv2.namedWindow('HSV Adjuster')
    cv2.namedWindow('Mask Preview')

    # 创建滑动条
    create_trackbars('HSV Adjuster')

    while True:
        # 获取当前滑动条值
        lower, upper = get_trackbar_values('HSV Adjuster')

        # 创建掩膜
        lower = np.array(lower)
        upper = np.array(upper)
        mask = cv2.inRange(hsv, lower, upper)

        # 显示结果
        cv2.imshow('Mask Preview', mask)

        # 按键处理
        key = cv2.waitKey(1)
        if key == 27:  # ESC退出
            break

    cv2.destroyAllWindows()
    print(f"最终HSV范围：\nLower: {lower}\nUpper: {upper}")


# 使用示例
input_image = r"/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/Picture/3.jpg"
color_adjustment(input_image)