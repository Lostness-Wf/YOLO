import cv2
import numpy as np
import matplotlib.pyplot as plt

def get_vertical_midline_color_values(image):
    # 获取图像的尺寸
    height, width, _ = image.shape

    # 计算中线的 x 坐标
    mid_x = width // 2

    # 获取中线上的颜色值
    color_valuesRGB = []
    for y in range(height):
        color_valuesRGB.append(image[y, mid_x])

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 获取中线上的颜色值
    color_valuesHSV = []
    for y in range(height):
        color_valuesHSV.append(hsv_image[y, mid_x])

    return color_valuesRGB, color_valuesHSV


def plot_color_values(color_valuesRGB, color_valuesHSV, vertical_lines):

    # 分离RGB颜色通道
    color_valuesRGB = np.array(color_valuesRGB)
    b_values = color_valuesRGB[:, 0]
    g_values = color_valuesRGB[:, 1]
    r_values = color_valuesRGB[:, 2]

    # 分离HSV颜色通道
    color_valuesHSV = np.array(color_valuesHSV)
    h_values = color_valuesHSV[:, 0]
    s_values = color_valuesHSV[:, 1]
    v_values = color_valuesHSV[:, 2]

    # 绘制RGB颜色值表
    plt.figure(figsize=(10, 5))
    plt.plot(b_values, label='Blue', color='b')
    plt.plot(g_values, label='Green', color='g')
    plt.plot(r_values, label='Red', color='r')

    # 添加垂直线和标注
    for x in vertical_lines:
        plt.axvline(x=x, color='k', linestyle='--')
        mean_value_rgb = np.mean([b_values[x], g_values[x], r_values[x]])
        plt.text(x - 20, 30,
                f'B: {b_values[x]}\nG: {g_values[x]}\nR: {r_values[x]}',
                color='black', ha='right', va='center', bbox=dict(facecolor='white', alpha=0.8))

    plt.xlabel('Pixel Coordinate')
    plt.ylabel('Color Value')
    plt.title('Color Values Along the Vertical Midline (RGB)')
    plt.legend()
    plt.show()

    # 绘制HSV颜色值表
    plt.figure(figsize=(10, 5))
    plt.plot(h_values, label='Hue', color='r')
    plt.plot(s_values, label='Saturation', color='g')
    plt.plot(v_values, label='Value', color='b')

    # 添加垂直线和标注
    for x in vertical_lines:
        plt.axvline(x=x, color='k', linestyle='--')
        mean_value_hsv = np.mean([h_values[x], s_values[x], v_values[x]])
        plt.text(x - 20, 30,
               f'H: {h_values[x]}\nS: {s_values[x]}\nV: {v_values[x]}',
              color='black', ha='right', va='center', bbox=dict(facecolor='white', alpha=0.8))

    plt.xlabel('Pixel Coordinate')
    plt.ylabel('Color Value')
    plt.title('Color Values Along the Vertical Midline (HSV)')
    plt.legend()
    plt.show()

# 读取图像
image_path = r'/Users/wfcy/Dev/PycharmProj/YOLOTrain/Pic/1.png'
image = cv2.imread(image_path)

# 获取垂直中线上的颜色值
color_valuesRGB, color_valuesHSV = get_vertical_midline_color_values(image)

# 指定垂直线的位置（横坐标）
vertical_lines = [233, 404, 583, 753, 1105]

# 绘制颜色值表格
plot_color_values(color_valuesRGB, color_valuesHSV, vertical_lines)

# def plot_custom_data(custom_data):
#     """绘制自定义数组的折线图"""
#     plt.figure(figsize=(10, 5))
#     plt.plot(custom_data, marker='o', linestyle='-', color='g', label='Data')
#
#     # 自动标记所有数据点（如果数据点较少）
#     if len(custom_data) < 20:
#         for i, value in enumerate(custom_data):
#             plt.text(i, value, f'{value:.1f}', ha='center', va='bottom', color = 'r')
#
#     plt.xlabel("epoch")
#     plt.ylabel("Lose value")
#     plt.title("Lose")
#     plt.grid(True)
#     plt.legend()
#     plt.show()
#
# if __name__ == "__main__":
#
#     # 示例数据，替换换成自己的数据
#     sample_data = [1, 2, 3, 4]
#
#     # 绘制基础折线图
#     plot_custom_data(sample_data)
