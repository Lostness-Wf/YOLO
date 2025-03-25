import warnings
from ultralytics import YOLO

# 忽略警告
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    # 加载模型
    model = YOLO('ultralytics/cfg/models/11/yolo11.yaml')
    model.load('yolo11n.pt')  # 加载预训练权重

    # 训练模型
    model.train(
        data=r'D:\python\yolov11\dianzu\five\data.yaml',  # 数据集配置文件
        cache=False,  # 是否缓存数据集
        imgsz=640,  # 输入图像大小
        epochs=200,  # 训练轮数
        batch=16,  # 批量大小
        close_mosaic=10,  # 最后 10 个 epoch 关闭 Mosaic 数据增强
        workers=8,  # 数据加载的线程数
        patience=0,  # 早停的耐心值（0 表示禁用早停）
        device='0',  # 使用 GPU 设备
        optimizer='Adam',  # 优化器
        single_cls=False,  # 是否单类别训练
        # 数据增强配置
        hsv_s=0.7,  # 饱和度增强幅度
        hsv_v=0.4,  # 亮度增强幅度
        degrees=45.0,  # 随机旋转角度范围
        translate=0.1,  # 随机平移幅度
        scale=0.5,  # 随机缩放幅度
        shear=0.0,  # 随机剪切幅度
        perspective=0.0,  # 透视变换幅度
        flipud=0.0,  # 上下翻转概率
        fliplr=0.5,  # 左右翻转概率
        mosaic=1.0,  # Mosaic 数据增强概率
        mixup=0.0,  # MixUp 数据增强概率
        copy_paste=0.0,  # Copy-Paste 数据增强概率
    )