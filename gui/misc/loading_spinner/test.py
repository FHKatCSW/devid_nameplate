from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget, QPushButton, QDesktopWidget
from PyQt5.QtGui import QMovie
import sys
import requests  # Import the requests library for REST calls
import time

class LoadingSpinner(QLabel):
    def __init__(self):
        super(LoadingSpinner, self).__init__()

        # Set label properties
        self.setFixedSize(200, 200)
        self.setAlignment(Qt.AlignCenter)

        # Set spinner movie
        movie = QMovie('/home/admin/devid_nameplate/gui/misc/loading_spinner/giphy.gif')
        self.setMovie(movie)
        movie.start()

class RestThread(QThread):
    rest_response = pyqtSignal()  # Signal to indicate REST call is complete

    def run(self):
        # Simulate REST call with a delay
        response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
        print(response.json())
        time.sleep(3)

        # Emit the signal once the REST call is complete
        self.rest_response.emit()

class MyMainWindow(QMainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()

        # Set window properties
        self.setWindowTitle('My Application')
        self.setGeometry(100, 100, 800, 600)

        # Create central widget
        central_widget = QTabWidget()
        self.setCentralWidget(central_widget)

        # Create tabs
        tab1 = QWidget()
        tab2 = QWidget()
        central_widget.addTab(tab1, 'Tab 1')
        central_widget.addTab(tab2, 'Tab 2')

        # Create loading spinner
        self.loading_spinner = LoadingSpinner()

        # Create REST thread
        self.rest_thread = RestThread()
        self.rest_thread.rest_response.connect(self.on_rest_complete)

        # Create button
        button = QPushButton('Trigger REST Call')
        button.clicked.connect(self.on_button_clicked)
        self.statusBar().addWidget(button)

    def on_button_clicked(self):
        # Show loading spinner in full screen when button is clicked
        self.loading_spinner.show()
        self.loading_spinner.setWindowState(self.loading_spinner.windowState() | QtCore.Qt.WindowFullScreen)  # Set the window to be fullscreen
        self.loading_spinner.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove the title bar and border

        # Start REST call in a separate QThread
        self.rest_thread.start()

    def on_rest_complete(self):
        # Hide loading spinner when REST call is complete
        self.loading_spinner.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MyMainWindow()
    window.setWindowState(window.windowState() | QtCore.Qt.WindowFullScreen)  # Set the window to be fullscreen
    window.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # Remove the title bar and border

    window.show()

    sys.exit(app.exec_())
