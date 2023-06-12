from time import sleep

import crcmod

# from App.Agreement import UpdateStart, UpdateMode
from App.BinFile import GetFileName, GetFileData, GetFileSize, GetFileDataAll

SOH = b'\x01'
STX = b'\x02'
EOT = b'\x04'
ACK = b'\x06'
NAK = b'\x15'
CAN = b'\x18'
CC = b'C'


# 触发包
def YmodemTigger():
    trigger = "rb -E\r"
    trigger = trigger.encode('UTF-8')
    return trigger


# 握手包
def YmodemStart(file_name, file_size):
    row_buf = file_name + "\0" + file_size + "\0"
    print(row_buf)
    row_buf = row_buf + "\0" * (128 - len(row_buf))
    buf = bytes(row_buf, 'UTF-8')
    crc16 = YmodemCrcCount(buf)
    crc16_h = crc16 >> 8
    crc16_l = crc16 & 0xff
    crc16_h = crc16_h.to_bytes(1, 'big').hex()
    crc16_l = crc16_l.to_bytes(1, 'big').hex()
    hex_buf = SOH.hex() + b'\x00'.hex() + b'\xff'.hex() + buf.hex() + crc16_h + crc16_l
    print(hex_buf)
    hex_buf = bytes.fromhex(hex_buf)
    print(hex_buf)
    return hex_buf


# 数据包
def YmodemData(file_data, num):
    num = num % 256  # 计算包序号
    negation_num = ~num & 0xff  # 计算包号反码
    row_data = file_data.hex() + "1a" * (128 - len(file_data))
    crc16 = YmodemCrcCount(bytes.fromhex(row_data))
    crc16_h = crc16 >> 8
    crc16_l = crc16 & 0xff
    crc16_h = crc16_h.to_bytes(1, 'big').hex()
    crc16_l = crc16_l.to_bytes(1, 'big').hex()
    row_data = SOH.hex() + num.to_bytes(1, 'big').hex() \
               + negation_num.to_bytes(1, 'big').hex() + row_data \
               + crc16_h + crc16_l
    row_data = bytes.fromhex(row_data)
    print(row_data)
    print(len(row_data))
    return row_data


# 取消发送包
def YmodemCancellation():
    data = b'\x18\x18\x18\x18\x18\x08\x08\x08\x08\x08'
    return data


# 结束包
def YmodemEnd():
    return EOT


# 客户端结束
def YmodemClientEnd():
    return b'\x18\x18\x18\x18\x18'


# 计算CRC
def YmodemCrcCount(file_data):
    crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)  # Xmodem
    if file_data is None:
        return None
    buf = crc16(file_data)  # 计算crc
    return buf


def Ymodem(file_path, serial,textview):
    shake_flag = 0
    file_name, file_suffix = GetFileName(file_path)
    if file_name is False or file_suffix is False:
        return False
    file_data = GetFileData(file_path)
    file_size = GetFileSize(file_path)
    file_data_all = GetFileDataAll(file_path)
    if file_data is False or file_size is False or file_data_all is False:
        return False
    file_crc16 = YmodemCrcCount(file_data_all)
    data_num = 1
    can_buf = 0
    flag = False
    while True:
        try:
            buf = serial.readline()
            if flag is False:
                # serial.write(UpdateStart(file_crc16))  # 私有协议部分，可根据需求自行修改
                # sleep(0.5)
                # buf = serial.readline()
                # if buf == b'':
                #     continue
                # if not UpdateMode(buf.decode("GBK")):
                #     continue
                serial.write(YmodemTigger())  # Ymodem触发
                flag = True
                continue
            if buf == b'':
                continue
            if buf == CC:  # 接收到C字符，开始握手
                can_buf = 0
                if shake_flag == 0:  # 首次接收开始握手，握手一次后再次接收视为客户端错误数据，直接跳过
                    textview.append("发送文件信息")
                    name = file_name + file_suffix
                    print(name)
                    serial.write(YmodemStart(file_name + file_suffix, str(file_size)))
                    textview.append("文件信息发送成功")
                continue
            if buf == ACK or buf == b'\x06\x43':
                can_buf = 0
                for chunk in file_data:
                    serial.write(YmodemData(chunk, data_num))
                    while True:
                        buf = serial.readline()
                        if buf == b'':
                            continue
                        if buf == ACK:
                            data_num += 1
                            break
                        if buf == NAK:
                            serial.write(YmodemData(chunk, data_num))
                            continue
                        if buf == CAN:
                            serial.write(YmodemCancellation())
                            textview.append("客户端取消接收")
                            return False
                if buf == b'\x06\x43':
                    serial.write(YmodemStart("\0", "\0"))
                    return True
                serial.write(YmodemEnd())  # 文件发送结束
                continue
            if buf == NAK:
                if flag is False:
                    serial.write(YmodemTigger())
                    flag = True
                    continue
                serial.write(YmodemEnd())
                continue
            if buf == YmodemCancellation():
                return True
            if buf == CAN:
                can_buf += 1
                if can_buf >= 5:
                    serial.write(YmodemCancellation())
                    return True  # 发送完成
                continue
        except Exception as e:
            print(e)
            return False


if __name__ == '__main__':
    YmodemStart("test.bin", "12345")
    YmodemData(b'\x12\x13', 2)
