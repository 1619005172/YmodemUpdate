import serial
import serial.tools.list_ports
from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE, STOPBITS_ONE, \
    STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO


def get_serial():
    __plist = list(serial.tools.list_ports.comports())
    __ports = [p.name for p in __plist]
    return __ports


def get_serial_name():
    data = []
    __plist = list(serial.tools.list_ports.comports())
    __ports = [p.name + " " + p.description for p in __plist]
    for __i in __ports:
        data.append(str(__i))
    return data


class SerialPort:
    def __init__(self):
        self.__serial_list = get_serial()
        self.ser = serial.Serial()  # 串口设备

        self.port = None  # 端口选择
        self.bps = 6  # 波特率选择
        self.byte_size = 3  # 数据位选择
        self.parity = 0  # 校验位选择
        self.stop_bits = 0  # 停止位选择
        self.flow_control = 0  # 流控选择

    # 连接串口
    def connect_serial(self):
        # 校验位
        serial_parity = [PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE]
        serial_stopbits = [STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO]
        serial_bps = [4800, 9600, 19200, 38400,
                      57600, 74800, 115200, 230400,
                      460800, 576000, 921600, 1152000]
        serial_bytesize = [5, 6, 7, 8]
        timeout = None  # 超时时间
        xonxoff = False  # 软件流控
        rtscts = False  # 硬件流控（RTS/CTS）
        dsrdtr = None  # 硬件流控（DSR/DTR）
        if self.flow_control != 0:
            xonxoff = True
        # 填充串口参数
        self.ser.port = self.port
        self.ser.timeout = 0.01
        self.ser.baudrate = serial_bps[self.bps]
        self.ser.bytesize = serial_bytesize[self.byte_size]
        self.ser.parity = serial_parity[self.parity]
        self.ser.stopbits = serial_stopbits[self.stop_bits]
        self.ser.xonxoff = xonxoff

        # 打开串口
        print(self.ser)
        print("端口:", self.port, "波特率:", serial_bps[self.bps],
              "数据位:", serial_bytesize[self.byte_size], "校验位:", serial_parity[self.parity],
              "停止位:", serial_stopbits[self.stop_bits], "流控:", xonxoff)
        try:
            self.ser.open()
            return True
        except:
            return False


if __name__ == '__main__':
    list_buf = get_serial_name()
    # for i in list_buf:
    #     print(i)
    print(list_buf)
    print(get_serial())
