from PyQt5 import QtWidgets as qtw
from presenter.main_presenter import MainPresenter


class MainWindow(qtw.QWidget):
    """Main window entry point using MVP architecture"""
    
    def __init__(self):    
        super().__init__()
        # Create the presenter which handles all the logic
        self.presenter = MainPresenter()
    
