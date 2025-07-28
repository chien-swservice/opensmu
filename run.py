import sys
from PyQt5.QtWidgets import QApplication
from application_logic import ApplicationLogic

def main():
    app = QApplication(sys.argv)
    window = ApplicationLogic()
    window.main_view.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()