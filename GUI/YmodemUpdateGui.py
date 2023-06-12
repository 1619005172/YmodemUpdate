import os
import sys
import threading
import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QBasicTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, \
    QHBoxLayout, QVBoxLayout, QTextBrowser, \
    QGridLayout, QMainWindow, QLineEdit, QComboBox, QMessageBox, QLabel

from App.BinFile import BinFile
from App.Update import AppUpdate
from App.SerialPort import SerialPort, get_serial, get_serial_name
from App.Ymodem import Ymodem

serial_bps = ['4800', '9600', '19200', '38400',
              '57600', '74800', '115200', '230400',
              '460800', '576000', '921600', '1152000']


def open_file(self):
    file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(self, "选取文件", os.getcwd(),
                                                                 "bin Files(*.bin);;All Files(*)")
    return file_name


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class SetUi(QMainWindow):
    serial_select = QtCore.pyqtSignal(list)
    serial_err = QtCore.pyqtSignal(str)
    __connectBuf = False  # 串口开启标志
    __analysisUiBuf = True  # 子窗口开启标志

    def __init__(self):
        super().__init__()
        # self.version_buf = None
        self.timer1 = None
        self.pv = 0
        self.update_flag = True
        self.__connectBuf = False
        self.serial_flag = False
        self.widget = QWidget()
        self.__updateThread = threading.Thread(target=self.__appUpdateThread)
        self.__updateThread.setDaemon(True)

        self.update_app = AppUpdate()
        self.crc_bin_file = BinFile()

        # 整体布局
        # 主垂直布局
        self.vbox = QVBoxLayout()
        # 上层水平布局
        self.top_hbox = QHBoxLayout()
        # 中层水平布局
        self.among_hbox = QHBoxLayout()
        # 下层水平布局
        self.down_hbox = QHBoxLayout()
        # # 上层左侧垂直布局
        self.right_top_vbox = QVBoxLayout()
        # 上层网格布局
        self.top_Gbox = QGridLayout()

        # 右侧
        self.selectBootButton = QPushButton("bootloader")
        self.selectAppButton = QPushButton("app")
        self.startButton = QPushButton("开始升级")

        # 文本显示窗口
        self.bottom_TextView = QTextBrowser()  # 底部文本框
        self.bottom_TextView2 = QTextBrowser()  # 底部文本框2
        self.boot_file_line_edit = QLineEdit()  # boot选择文本框
        self.app_file_line_edit = QLineEdit()  # app选择文本框
        self.shifting_line_edit = QLineEdit()  # app偏移量
        self.device_id_addr_line_edit = QLineEdit()  # 设备版本号
        self.device_id_line_edit = QLineEdit()  # 设备版本号

        self.left_label1 = QLabel("串口")
        self.left_label2 = QLabel("波特率")
        # 选择控件
        self.device_select = QComboBox()  # 设备选择框
        self.device_select_baud = QComboBox()  # 串口波特率选择

        # 时钟控件
        self.timer1 = QBasicTimer()  # 添加时钟控件，刷进度条

        # # 进度条
        # self.pgb = QProgressBar()

        self.serialBuf = SerialPort()
        self.initUI()
        self.__runCheckSerial()  # 启动监测线程
        self.initSerial()

    def initUI(self):
        # # 显示任务栏图标
        # if sys.platform == "win32":
        #     import ctypes
        #     ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("6666")

        # 设置窗口的标题
        self.setWindowTitle('串口升级工具  V' + str(self.update_app.version))
        self.resize(800, 500)
        # 设置窗口ICON
        self.setWindowIcon(QIcon(get_resource_path("./image/favicon.ico")))
        self.right_top_vbox.setSpacing(15)
        self.top_hbox.setSpacing(15)
        self.down_hbox.setSpacing(15)
        self.among_hbox.setSpacing(15)

        # self.pgb.move(50, 50)
        # self.pgb.resize(250, 20)
        # # 进度条相关

        self.left_label1.setAlignment(Qt.AlignCenter)
        self.left_label2.setAlignment(Qt.AlignCenter)

        self.bottom_TextView2.document().setMaximumBlockCount(150)

        # self.boot_file_line_edit.setPlaceholderText("选择BootLoader")
        self.app_file_line_edit.setPlaceholderText("选择APP")
        # self.shifting_line_edit.setPlaceholderText("APP偏移量")
        # self.device_id_line_edit.setPlaceholderText("APP版本信息")
        # self.device_id_addr_line_edit.setPlaceholderText("版本信息偏移量")
        # self.device_select.addItem("选择串口")
        # self.device_select_baud.addItem("选择波特率")
        # self.shifting_line_edit.setInputMask("H")
        # self.device_id_addr_line_edit.setInputMask("H")

        self.device_select.width()
        # self.top_Gbox.addWidget(self.boot_file_line_edit, 0, 0)
        self.top_Gbox.addWidget(self.app_file_line_edit, 1, 0)
        # self.top_Gbox.addWidget(self.selectBootButton, 0, 1)
        self.top_Gbox.addWidget(self.selectAppButton, 1, 1)
        self.top_Gbox.addWidget(self.startButton, 2, 1)
        self.among_hbox.addWidget(self.left_label1)
        self.among_hbox.addWidget(self.device_select)
        self.among_hbox.addWidget(self.left_label2)
        self.among_hbox.addWidget(self.device_select_baud)
        # self.among_hbox.addWidget(self.shifting_line_edit)
        # self.among_hbox.addWidget(self.device_id_addr_line_edit)
        # self.among_hbox.addWidget(self.device_id_line_edit)

        self.down_hbox.addWidget(self.bottom_TextView)  # 下层水平布局添加显示窗口
        self.down_hbox.addWidget(self.bottom_TextView2)  # 下层水平布局添加显示窗口2
        # self.device_select.addItems(device_list)
        self.device_select.addItems(get_serial_name())
        self.device_select_baud.addItems(serial_bps)
        self.device_select_baud.setCurrentIndex(6)

        self.vbox.addLayout(self.top_Gbox)  # 上层添加网格布局
        self.vbox.addLayout(self.down_hbox)  # 下层添加水平布局
        self.top_Gbox.addLayout(self.among_hbox, 2, 0)  # 中间层添加水平布局

        # 注册按钮信号
        # self.selectBootButton.clicked.connect(self.buttonMsg)
        self.selectAppButton.clicked.connect(self.buttonMsg)
        self.startButton.clicked.connect(self.buttonMsg)

        # 注册选择窗信号
        self.device_select.activated.connect(self.selectMsg)
        self.device_select_baud.activated.connect(self.selectMsg)
        # 串口选择更新信号
        self.serial_select.connect(self.uiUpdate)
        # 串口异常断开信号
        self.serial_err.connect(self.__serialAbnormal)

        # 文本框信号
        # self.boot_file_line_edit.textChanged.connect(self.lineEditMsg)  # 只要文本框内容改变就发送信号
        self.app_file_line_edit.textChanged.connect(self.lineEditMsg)
        # self.shifting_line_edit.textChanged.connect(self.lineEditMsg)
        # self.device_id_line_edit.textChanged.connect(self.lineEditMsg)
        # self.device_id_addr_line_edit.textChanged.connect(self.lineEditMsg)

        self.widget.setLayout(self.vbox)
        self.setCentralWidget(self.widget)
        # 检测升级
        if self.update_app.GetUpdateMsg():
            a = QMessageBox.question(self, 'update', '发现新的版本V{} \n是否升级?'.format(self.update_app.app_version),
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if a == QMessageBox.Yes:
                self.timer1.start(10, self)
                self.__runAppUpdateThread()

    # 按钮功能选择
    def buttonMsg(self):
        if self.sender() == self.selectBootButton:
            print("选择boot")
            boot_file_path = open_file(self)  # 获取boot文件路径
            self.boot_file_line_edit.setText(boot_file_path)
        elif self.sender() == self.selectAppButton:
            app_file_path = open_file(self)  # 获取app文件路径
            self.app_file_line_edit.setText(app_file_path)
            print("选择app")
        elif self.sender() == self.startButton:
            if self.device_select.currentIndex() == -1:
                QMessageBox.information(self, "错误", "未选择串口")
                return
            if self.crc_bin_file.app_file_path is None:
                QMessageBox.information(self, "错误", "未选择固件")
                return
            if self.serialBuf.port is None:
                print("串口为空")
                QMessageBox.information(self, "提示", "串口为空")
            else:
                if not self.__connectBuf:
                    if self.serialBuf.connect_serial():
                        self.__connectBuf = True
                        print("串口打开成功")
                        self.connectOnOff(False)
                        self.__runTextUpdateThread()
                    else:
                        print("串口打开失败")
                        QMessageBox.information(self, "提示", "串口打开失败")
                else:
                    self.__connectBuf = False
                    self.serial_flag = False
                    self.serialBuf.ser.close()
                    self.connectOnOff(True)
                    # self.uiUpdate(get_serial())
                    # self.initSerial()  # 关闭串口后重新刷新参数
                    print("串口关闭")
            # try:
            #     self.bottom_TextView.append("-----------------------------------------")
            #     self.bottom_TextView.append("开始生成")
            #     if self.crc_bin_file.boot_file_path is not None:
            #         self.bottom_TextView.append("Bootloader:" + str(self.crc_bin_file.boot_file_path))
            #     self.bottom_TextView.append("App:" + str(self.crc_bin_file.app_file_path))
            #     self.bottom_TextView.append("App偏移地址:" + str(hex(self.crc_bin_file.app_addr)))
            #     self.bottom_TextView.append("Bootloader偏移地址:" + str(hex(self.crc_bin_file.boot_addr)))
            #     self.bottom_TextView.append("设备信息偏移地址:" + str(hex(self.crc_bin_file.device_msg_addr)))
            #     self.bottom_TextView.append("固件版本:" + self.crc_bin_file.edition)
            #     self.bottom_TextView.append("设备ID:" + str(self.crc_bin_file.device_id))
            #     if not self.crc_bin_file.CreateBin():
            #         QMessageBox.information(self, "error", "生成错误")
            #         self.bottom_TextView.append("生成错误")
            #     self.bottom_TextView.append("CRC结果:" + str(self.crc_bin_file.CRC_BUF))
            #     self.bottom_TextView.append("生成成功")
            #     self.bottom_TextView.append("-----------------------------------------")
            #     self.bottom_TextView.moveCursor(self.bottom_TextView.textCursor().End)  # 移动显示到底部
            # except Exception as e:
            #     QMessageBox.information(self, "error", "未知错误:" + str(e))

    def selectMsg(self):
        if self.sender() == self.device_select:
            print("串口选择")
            select_id = self.device_select.currentIndex()
            if select_id == -1:
                return
            else:
                self.serialBuf.port = get_serial()[int(select_id)]
        elif self.sender() == self.device_select_baud:
            print("波特率选择")
            select_id = self.device_select_baud.currentIndex()
            if select_id == -1:
                return
            else:
                self.serialBuf.bps = int(select_id)

    def lineEditMsg(self):
        if self.sender() == self.boot_file_line_edit:
            try:
                boot_file_path = self.boot_file_line_edit.text()
                self.crc_bin_file.boot_file_path = boot_file_path
                return
            except Exception as e:
                print("输入错误" + str(e))
                return
        elif self.sender() == self.app_file_line_edit:
            try:
                app_file_path = self.app_file_line_edit.text()
                self.crc_bin_file.app_file_path = app_file_path
                return
            except Exception as e:
                print("输入错误" + str(e))
                return
        elif self.sender() == self.shifting_line_edit:
            try:
                shifting_cache = self.shifting_line_edit.text()
                shifting_cache = int(shifting_cache, 16)
                self.crc_bin_file.app_addr = shifting_cache
                return
            except Exception as e:
                print("输入错误" + str(e))
                return
        elif self.sender() == self.device_id_line_edit:
            try:
                device_id_cache = self.device_id_line_edit.text()
                self.crc_bin_file.edition = device_id_cache
                return
            except Exception as e:
                print("输入错误" + str(e))
                return
        elif self.sender() == self.device_id_addr_line_edit:
            try:
                device_id_addr_cache = self.device_id_addr_line_edit.text()
                device_id_addr_cache = int(device_id_addr_cache, 16)
                self.crc_bin_file.device_msg_addr = device_id_addr_cache
                return
            except Exception as e:
                print("输入错误" + str(e))
                return

    def timerEvent(self, event):
        # print("timer")
        if not self.update_flag:
            QMessageBox.information(self, "update", "升级失败")
            self.timer1.stop()
        if self.pv >= 100:
            self.timer1.stop()
            QMessageBox.information(self, "update", "升级成功，请删除旧版本启动新版本")
            sys.exit()
        else:
            self.pv = self.update_app.schedule_num
            self.bottom_TextView.append(self.update_app.schedule)
            self.bottom_TextView.moveCursor(self.bottom_TextView.textCursor().End)  # 移动显示到底部
        # print(self.update_app.schedule_num)

    # 刷新串口列表
    def uiUpdate(self):
        # 串口开启之后界面不会刷新
        if not self.__connectBuf:
            self.device_select.clear()
            self.device_select.addItems(get_serial_name())
            self.device_select.update()

    # 串口打开/关闭功能刷新
    def connectOnOff(self, o_f):
        self.device_select.setEnabled(o_f)
        self.device_select_baud.setEnabled(o_f)
        if o_f:
            self.startButton.setText("开始升级")
        else:
            self.startButton.setText("停止升级")

    def initSerial(self):
        if self.device_select.currentIndex() != -1:
            self.serialBuf.port = self.device_select.currentText()  # 获取选中端口名称
        if self.device_select_baud.currentIndex() != -1:
            self.serialBuf.bps = self.device_select_baud.currentIndex()  # 获取选中索引
        print("端口:", self.serialBuf.port, "波特率:", self.serialBuf.bps,
              "数据位:", self.serialBuf.byte_size, "校验位:", self.serialBuf.parity,
              "停止位:", self.serialBuf.stop_bits, "流控:", self.serialBuf.flow_control)

    # 读串口线程
    def __textUpdateThread(self):
        while self.__connectBuf:
            if not self.__connectBuf:  # 串口关闭停止线程
                self.serial_flag = False
                return
            try:
                if not self.serial_flag:
                    self.serial_flag = True
                    self.bottom_TextView.append("-----------------------------------------")
                    time.sleep(1)
                    self.bottom_TextView.append("开始升级")
                    if Ymodem(self.crc_bin_file.app_file_path, self.serialBuf.ser,self.bottom_TextView):
                        self.bottom_TextView.append("文件发送成功")
                        self.bottom_TextView.append("升级成功")
                        self.serialBuf.ser.close()
                        self.__connectBuf = False
                        self.serial_flag = False
                        self.connectOnOff(True)
                        print("串口关闭")
                    else:
                        self.bottom_TextView.append("升级失败")
                    self.bottom_TextView.append("-----------------------------------------")
                    self.bottom_TextView2.moveCursor(self.bottom_TextView2.textCursor().End)
                buf = self.serialBuf.ser.readline()
                if buf == b'':
                    continue
                print(buf.decode('GBK'))
                # print(buf.hex())
                # self.serialBuf.ser.write(b'\x43')
                # if buf is not None:
                #     buf_gbk = buf.decode("GBK")
                #     self.bottom_TextView2.append(buf_gbk)
                #     self.bottom_TextView2.moveCursor(self.bottom_TextView2.textCursor().End)  # 移动显示到底部
                # print(buf_gbk)

            except Exception as e:
                self.serial_err.emit(e.args[0])  # 发送异常信号
                print(e.args[0])
                return

    def __runTextUpdateThread(self):
        self.__textThread = threading.Thread(target=self.__textUpdateThread)
        self.__textThread.setDaemon(True)
        self.__textThread.start()

    def __appUpdateThread(self):
        if self.update_app.GetNewApp():
            self.update_flag = True
        else:
            self.update_flag = False

    def __runAppUpdateThread(self):
        self.__updateThread = threading.Thread(target=self.__appUpdateThread)
        self.__updateThread.setDaemon(True)
        self.__updateThread.start()

    # def __runAppUpdateThread(self,args):
    #       self.__updateThread = threading.Thread(target=self.__appUpdateThread,args=args)
    #       self.__updateThread.setDaemon(True)
    #       self.__updateThread.start()

    def __checkSerialThread(self):
        serial_list = get_serial_name()
        while True:
            time.sleep(1)
            if serial_list != get_serial_name():
                if len(serial_list) > len(get_serial_name()):
                    print("串口拔出")
                else:
                    print("串口接入")
                serial_list = get_serial_name()
                print(serial_list)
                self.serial_select.emit(serial_list)

    # 串口异常断开
    def __serialAbnormal(self, args):
        print(args)
        if args.find("拒绝访问"):
            if self.__connectBuf:
                print("串口异常断开")
                QMessageBox.critical(self, "错误", "串口异常关闭！")
                self.__connectBuf = False
                self.connectOnOff(True)
                self.serialBuf.ser.close()
                self.uiUpdate()

    # 刷屏线程
    # def __refreshUiThread(self):
    #     while True:
    #         while self.__queue.empty() is not True:
    #             # if self.__queue.empty() is not True:
    #             buf_gbk = self.__queue.get().decode("GBK")
    #             self.TextView.append(buf_gbk)
    #             self.TextView.moveCursor(self.TextView.textCursor().End)  # 移动显示到底部
    #             print(buf_gbk)

    def __runCheckSerial(self):
        t = threading.Thread(target=self.__checkSerialThread)
        t.setDaemon(True)  # 设置为守护进程
        t.start()
        # t2 = threading.Thread(target=self.__refreshUiThread)
        # t2.setDaemon(True)
        # t2.start()
        print("监测线程启动")
