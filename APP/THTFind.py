import cv2
import numpy as np

"""
预处理阶段使用高斯模糊消除高频噪声
Canny边缘检测结合形态学闭合操作确保电阻轮廓完整
轮廓筛选使用面积和长宽比双重条件排除干扰
最后通过中值滤波和二次形态学操作优化遮罩质量
"""

""" 调整：
高斯模糊核大小
Canny边缘检测阈值
形态学操作的迭代次数
轮廓面积阈值和长宽比参数
"""

# 读取图片
img = cv2.imread(r"/Users/wfcy/Dev/PycharmProj/YOLOTrain/APP/Picture/555.png")
cv2.imshow('Original', img)
cv2.waitKey(0)

# 转换为灰度图
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow('Gray', gray)
cv2.waitKey(0)

# 高斯模糊去噪
blur = cv2.GaussianBlur(gray, (5,5), 0)
cv2.imshow('Blur', blur)
cv2.waitKey(0)

# Canny边缘检测
edges = cv2.Canny(blur, 50, 150)
cv2.imshow('Edges', edges)
cv2.waitKey(0)

# 形态学操作闭合边缘
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=3)
cv2.imshow('Closed Edges', closed)
cv2.waitKey(0)

# 查找轮廓
contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 筛选轮廓（根据面积和长宽比）
mask = np.zeros_like(gray)
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > 1000:  # 根据实际调整面积阈值
        x,y,w,h = cv2.boundingRect(cnt)
        aspect_ratio = w/h
        if 0.5 < aspect_ratio < 2.5:  # 排除明显非矩形轮廓
            cv2.drawContours(mask, [cnt], -1, 255, -1)

cv2.imshow('Mask', mask)
cv2.waitKey(0)

# 优化遮罩
mask = cv2.medianBlur(mask, 5)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

# 最终结果
result = cv2.bitwise_and(img, img, mask=mask)
cv2.imshow('Result', result)
cv2.waitKey(0)
cv2.destroyAllWindows()
