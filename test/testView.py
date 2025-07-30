import sys
from PyQt5.QtWidgets import QApplication
from view.view import View

def main():
    app = QApplication(sys.argv)
    window = View()
    window.show()
    #window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()