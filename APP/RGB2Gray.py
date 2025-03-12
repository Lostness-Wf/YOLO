from PIL import Image


def convert_to_grayscale(input_path, output_path):
    """
    将图片转换为灰度图
    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    """
    try:
        # 打开图片文件
        with Image.open(input_path) as img:
            # 转换为灰度模式（'L'模式表示灰度）
            grayscale_img = img.convert('L')

            # 保存灰度图
            grayscale_img.save(output_path)
            print(f"灰度图已保存至：{output_path}")

            # 可选：显示图片
            grayscale_img.show()

    except Exception as e:
        print(f"处理失败：{str(e)}")


# 使用示例
if __name__ == "__main__":
    input_image = "/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/Picture/1.jpg"  # 输入图片路径
    output_image = "/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/2.jpg"  # 输出图片路径
    convert_to_grayscale(input_image, output_image)