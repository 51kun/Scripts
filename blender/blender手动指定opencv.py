import sys
#找到 OpenCV 的安装路径：pip show opencv-python
opencv_path = r'C:\Users\wuwuy\AppData\Local\Programs\Python\Python312\Lib\site-packages'
if opencv_path not in sys.path:
    sys.path.append(opencv_path)