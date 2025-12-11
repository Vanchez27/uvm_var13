import os
import subprocess
import sys


def build():
    try:
        import PyInstaller
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # onefile: один exe файл
    # noconsole: без консольного окна (для GUI)
    # hidden-import: явно указывает PyInstaller'у захватить ваши модули
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", "UVM_Tool",
        "--hidden-import", "assembler_stage1",
        "--hidden-import", "interpreter",
        "uvm_gui.py"
    ]

    subprocess.call(cmd)

if __name__ == "__main__":
    build()