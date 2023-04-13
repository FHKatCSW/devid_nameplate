from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QPixmap, QMovie
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QDialog
import logging


class NameplateLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(250, 40)
        self.move(30, 30)
        self.setWordWrap(True)
        font = QFont()
        font.setItalic(True)
        font.setPointSize(12)
        self.setFont(font)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw border
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor("black"), 2))
        painter.drawRoundedRect(self.rect(), 10, 10)

        super().paintEvent(event)

class StatusIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)

        self.setStyleSheet("""
                   StatusIndicator {
                       background-color: #d9d9d9;
                   }
               """)
    def postive(self):
        self.setStyleSheet("background-color: green;")

    def negative(self):
        self.setStyleSheet("background-color: red;")

class LoadingSpinner(QDialog):
    def __init__(self):
        super(LoadingSpinner, self).__init__()

        # Set dialog properties
        self.setWindowTitle('Loading...')
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setModal(True)

        # Set spinner label properties
        self.spinner_label = QLabel()
        self.spinner_label.setAlignment(Qt.AlignCenter)

        # Set spinner movie
        movie = QMovie('/home/admin/devid_nameplate/gui/misc/loading_spinner/giphy.gif')
        self.spinner_label.setMovie(movie)
        movie.start()

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.spinner_label)
        self.setLayout(layout)

        # Set background color
        self.setStyleSheet("background-color: #FFFFFF;")

class NameplateLabelHeader(QLabel):
    def __init__(self, text="",parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setFixedSize(150, 40)
        self.move(15, 15)
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

class CertOutput(QLabel):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setFixedSize(350, 250)
        self.move(15, 15)
        self.setWordWrap(True)
        font = QFont()
        font.setPointSize(6)
        self.setFont(font)

class StatusLabel(QLabel):
    def __init__(self, text="",parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setFixedSize(150, 40)
        self.move(30, 30)
        self.setWordWrap(True)
        font = QFont()
        font.setPointSize(16)
        self.setFont(font)

class NameplateHeader(QLabel):
    def __init__(self, text="",parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setFixedSize(200, 40)
        self.move(30, 30)
        self.setWordWrap(True)
        font = QFont()
        font.setBold(True)
        font.setPointSize(20)
        self.setFont(font)

class QTextEditHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)



class IconWithSize(QLabel):
    def __init__(self, icon_path, width=80, height=40):
        super().__init__()

        # Load the icon from the file path
        pixmap = QPixmap(icon_path)
        icon_size = QSize(width, height)

        scaled_pixmap = pixmap.scaled(icon_size)

        # Set the pixmap of the label
        self.setPixmap(scaled_pixmap)