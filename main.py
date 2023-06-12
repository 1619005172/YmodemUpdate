import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from GUI.YmodemUpdateGui import SetUi

if __name__ == '__main__':
    # 据说可以自适应屏幕分辨率
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    # 创建QT对象
    app = QApplication(sys.argv)
    test = SetUi()
    test.show()
    # 退出程序
    sys.exit(app.exec_())
