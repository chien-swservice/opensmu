"""Visual launcher for the View — run directly to test the UI manually.

Not a pytest test. Run with: python test/test_view.py
"""
import sys

try:
    from PyQt5.QtWidgets import QApplication
    from view.view import View
    HAS_QT = True
except ImportError:
    HAS_QT = False


def main():
    if not HAS_QT:
        print("PyQt5 is not installed. Install it with: pip install PyQt5")
        return
    app = QApplication(sys.argv)
    window = View()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
