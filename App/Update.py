import os

import requests

UPDATE_VERSION_URL = "http://update.xuebuwan.cn:8899/new/update/version"
UPDATE_APP_URL = "http://update.xuebuwan.cn:8899/new/update/app"


class AppUpdate:
    version = "1.0.0_beta"
    schedule = None
    schedule_num = 0
    app_version = None

    def GetUpdateMsg(self):
        try:
            resp = requests.get(UPDATE_VERSION_URL)
            if resp.status_code != 200:
                print("服务器链接失败")
                return False
            version_buf = str(resp.text)
            if int(version_buf[0]) > int(self.version[0]):
                print("app有更新 版本V{}".format(resp.text))
                self.app_version = resp.text
                return True
            if int(version_buf[2]) > int(self.version[2]):
                print("app有更新 版本V{}".format(resp.text))
                self.app_version = resp.text
                return True
            if int(version_buf[4]) > int(self.version[4]):
                print("app有更新 版本V{}".format(resp.text))
                self.app_version = resp.text
                return True
            print("无更新版本")
            return False
        except Exception as e:
            print("网络错误" + str(e))
            return False

    def GetNewApp(self):
        size = 0  # 初始化已下载大小
        chunk_size = 1024  # 每次下载的数据大小
        try:
            resp = requests.get(UPDATE_APP_URL, stream=True)
            resp.encoding = 'UTF-8'
            content_size = int(resp.headers['content-length'])  # 下载文件总大小
            if resp.status_code == 200:
                print('开始下载,文件大小:{size:.2f} MB'.format(
                    size=content_size / chunk_size / 1024))  # 开始下载，显示下载文件大小
                with open('./BIN升级校验助手 V{}.exe'.format(self.app_version), 'wb') as file:  # 显示进度条
                    for data in resp.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        size += len(data)
                        self.schedule_num = float(size / content_size * 100)
                        self.schedule = ('\r' + '[下载进度]:%s%.2f%%' % (
                            '>' * int(size * 50 / content_size), float(size / content_size * 100)))
                        print(self.schedule, end=' ')
                return True
            else:
                print('服务器连接失败')
                return False
        except Exception as e:
            print('网络错误' + str(e))
            return False


if __name__ == '__main__':
    AppUpdate().GetUpdateMsg()
