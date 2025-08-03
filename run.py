import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    # The presenter already shows the view, so we don't need to call show() again
    # window.presenter.get_view().show()  # This would be redundant
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()