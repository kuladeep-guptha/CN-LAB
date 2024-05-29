import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QSplitter, QTextEdit

class SplitterExample(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Splitter Example")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget and a layout for the central widget
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)

        # Create a splitter to split the window
        splitter = QSplitter(Qt.Horizontal)

        # Add the splitter to the central layout
        central_layout.addWidget(splitter)

        # Create two text editors for the left and right panes
        left_text_edit = QTextEdit()
        right_text_edit = QTextEdit()

        # Add the text editors to the splitter
        splitter.addWidget(left_text_edit)
        splitter.addWidget(right_text_edit)

        # Create a button to trigger the split
        split_button = QPushButton("Split Window")
        split_button.clicked.connect(self.splitWindow)

        # Add the button to the central layout
        central_layout.addWidget(split_button)

        # Set the central widget
        self.setCentralWidget(central_widget)

    def splitWindow(self):
        # Add a new text editor to the splitter
        new_text_edit = QTextEdit()
        self.centralWidget().layout().itemAt(0).widget().addWidget(new_text_edit)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SplitterExample()
    window.show()
    sys.exit(app.exec_())
