# 手动指定 OpenCV 路径以避免导入错误，不要修改以下代码部分
import sys
opencv_path = r'C:\Users\wuwuy\AppData\Local\Programs\Python\Python312\Lib\site-packages'
if opencv_path not in sys.path:
    sys.path.append(opencv_path)
import cv2
print(cv2.__version__)

import bpy
import numpy as np
import tempfile
import os

# 参数配置
alpha_threshold = 30
border_thickness = 2  # 描边的宽度

def add_border(image):
    alpha_channel = image[:, :, 3]
    
    # 创建边界掩码
    edges = cv2.Canny(alpha_channel.astype(np.uint8), 100, 200)
    
    # 扩展边界线条到指定宽度
    kernel = np.ones((border_thickness, border_thickness), np.uint8)
    edges_dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # 为边界添加黑色描边
    image_with_border = image.copy()
    image_with_border[edges_dilated > 0] = [0, 0, 0, 255]  # 黑色描边（RGBA）

    return image_with_border

def process_image(image_path):
    # 确保文件扩展名是 .png
    if not image_path.lower().endswith('.png'):
        print(f"文件 {image_path} 不是 PNG 格式，请检查输入图片。")
        return

    # 使用 OpenCV 读取图片
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # 读取包含透明通道的图片

    # 确保图片是RGBA格式
    if image.shape[2] != 4:
        print(f"图片 {image_path} 不是RGBA格式，请检查输入图片。")
        return

    # 提取透明度通道（Alpha通道）
    alpha_channel = image[:, :, 3]

    # 创建一个掩码，用于更新透明度
    alpha_channel[alpha_channel < alpha_threshold] = 0
    alpha_channel[alpha_channel >= alpha_threshold] = 255

    # 更新图片中的Alpha通道
    image[:, :, 3] = alpha_channel

    # 为透明度边界添加黑色描边
    image_with_border = add_border(image)

    # 保存修改后的图片
    if not cv2.imwrite(image_path, image_with_border):
        print(f"保存图片失败: {image_path}")

def main():
    # 临时目录用于存储图像文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 遍历所有纹理图像
        for image in bpy.data.images:
            if image.file_format.lower() == 'png':
                # 保存到临时目录
                temp_path = os.path.join(temp_dir, image.name)

                # 确保文件名有扩展名
                if not temp_path.lower().endswith('.png'):
                    temp_path += '.png'

                # 保存原图像到临时路径
                image.save_render(temp_path)

                # 处理图像
                process_image(temp_path)

                # 重新加载处理后的图像
                new_image = bpy.data.images.load(temp_path)

                # 获取处理后的图像的像素数据
                new_pixels = np.array(new_image.pixels)

                # 更新原图像的像素数据
                image.pixels = new_pixels.tolist()

                print(f"处理完成: {image.name}")

if __name__ == "__main__":
    main()
