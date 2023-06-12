import os


class BinFile:
    app_file_path = None
    device_msg_addr = 0xf810  # 设备信息存储地址
    edition = "v1.0.0"  # 设备版本
    device_id = 0  # 设备ID
    CRC_BUF = 0


# 获取文件名
def GetFileName(file_path):
    try:
        dirt_0, suffix = os.path.splitext(file_path)  # 提取文件后缀
        file_name = os.path.split(dirt_0)[1]  # 提取文件名
        return file_name, suffix
    except Exception as e:
        print(e)
        return False


def GetFileData(file_path):
    try:
        f_app = open(file_path, "rb")
        if f_app is None:
            return False
        while True:
            chunk = f_app.read(128)
            if not chunk:
                break
            yield chunk
    except Exception as e:
        print(e)
        return False


def GetFileDataAll(file_path):
    try:
        f_app = open(file_path, "rb")
        if f_app is None:
            return False
        app_data = f_app.read()
        return app_data
    except Exception as e:
        print(e)
        return False


def GetFileSize(file_path):
    try:
        file_seize = os.path.getsize(file_path)
        return file_seize
    except Exception as e:
        print(e)
        return False


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径


if __name__ == '__main__':
    data = GetFileData("./Slide_Rheostat.bin")
    for chunk in data:
        print(chunk)
