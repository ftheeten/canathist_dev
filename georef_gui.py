from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout , QFileDialog, QButtonGroup, QRadioButton, QLineEdit, QLabel, QCheckBox, QMessageBox, QComboBox, QSizePolicy
from PySide6.QtCore import Qt

app=None
window=None
layout=None

def start():
    global app
    global window
    global layout
    try:
        app = QApplication([])
        window = QWidget()
        window.setMinimumWidth(700)
        layout = QVBoxLayout()
    
        window.setLayout(layout)
        window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        window.show()           
        app.exec()
    except:    
        traceback.print_exception(*sys.exc_info())    
    
if __name__ == '__main__':
    start()