from cx_Freeze import setup, Executable

# ADD FILES
files = ['favicon.ico', 'Image/']

# TARGET
target = Executable(
    script="main.py",
    base="Win32GUI",
    icon="favicon.ico"
)

# SETUP CX FREEZE
setup(
    name="串口升级工具",
    version="1.0.0b0",
    description="",
    author="Memory",
    options={'build_exe': {'include_files': files}},
    executables=[target]

)
