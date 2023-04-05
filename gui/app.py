import json
import sys

from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QFont, QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QLabel, \
    QGridLayout, QDesktopWidget
from PyQt5.QtGui import QIcon

from gui.funs.highlevel import HighlevelIdev, HighlevelLdev
from gui.funs.rest import RestApiClient
from gui.funs.status_led import RestLed

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


class NameplateLabelHeader(QLabel):
    def __init__(self, text="",parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setFixedSize(150, 40)
        self.move(15, 15)
        font = QFont()
        font.setPointSize(20)
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
        self.setFixedSize(150, 40)
        self.move(30, 30)
        self.setWordWrap(True)
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IEEE 802.1 AR GUI')

        # Set style sheet
        self.setStyleSheet('''
            QPushButton {
                background-color: #EFEFEF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 3px;
                color: black;
                font-size: 10pt;
            }
            QTabBar::tab {
                margin-left:2px;
                margin-right:2px;
                margin-top:2px;
                background-color: #EFEFEF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
                color: black;
                font-size: 8pt;
            }
            QTabBar::tab:selected {
                background-color: #adacac;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DDDDDD;
            }
        ''')

        self.results_control_ldev = []
        self.results_control_idev = []
        self.results_idev_cycle = []
        self.results_ldev_cycle = []

        self.color_on = QColor(124,252,0)
        self.color_off = QColor(255,99,71)
        #self.state = False

        # Create tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Get the size of the screen
        screen_size = QDesktopWidget().screenGeometry().size()
        # Set the maximum size of the label to fit on the screen
        max_width = int(screen_size.width() * 1)  # Use 90% of the screen width
        max_height = int(screen_size.height() * 0.9)  # Use 90% of the screen height

        # ------------------
        # Tab for Status
        # ------------------

        self.status_grid = QGridLayout()
        self.status_grid.setSpacing(5)

        # Status for REST API
        self.status_label_rest = StatusLabel("REST API")
        self.status_grid.addWidget(self.status_label_rest, 0, 0)
        rest_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/rest")
        self.status_grid.addWidget(rest_led, 0, 1)

        # Status for HSM
        self.status_label_hsm = StatusLabel("HSM")
        self.status_grid.addWidget(self.status_label_hsm, 1, 0)
        hsm_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/hsm")
        self.status_grid.addWidget(hsm_led, 1, 1)


        # Status for IDevID
        self.status_label_idev = StatusLabel("IDevID")
        self.status_grid.addWidget(self.status_label_idev, 2, 0)
        idev_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/idevid")
        self.status_grid.addWidget(idev_led, 2, 1)

        # Status for LDevID
        self.status_label_ldev = StatusLabel("LDevID")
        self.status_grid.addWidget(self.status_label_ldev, 3, 0)
        ldev_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/ldevid")
        self.status_grid.addWidget(ldev_led, 3, 1)

        self.tab0 = QWidget()
        self.tabs.addTab(self.tab0, 'Status')
        self.tab0.setLayout(self.status_grid)

        close_button = QPushButton('Close Application', self)
        close_button.clicked.connect(self.close)
        self.status_grid.addWidget(close_button)

        # ------------------
        # Control IDevID
        # ------------------

        # Create first tab
        self.control_grid_idev = QGridLayout()
        self.control_grid_idev.setSpacing(5)

        self.result_label_idev = QLabel(self)
        self.result_label_idev.setFixedSize(300,250)
        self.result_label_idev.move(80, 80)
        self.result_label_idev.setWordWrap(True)

        self.control_grid_idev.addWidget(self.result_label_idev, 0, 2, 3, 2)

        # Create buttons for first tab
        self.button_bootstrap_idev = QPushButton('Bootstrap\nIDev')
        self.button_delete_idev = QPushButton('Delete\nIDev')
        self.button_validate_idev = QPushButton('Validate\nIDev')
        self.button_bootstrap_idev.setFixedSize(100,40)
        self.button_delete_idev.setFixedSize(100,40)
        self.button_validate_idev.setFixedSize(100,40)
        self.control_grid_idev.addWidget(self.button_bootstrap_idev, 0, 0)
        self.control_grid_idev.addWidget(self.button_delete_idev, 1, 0)
        self.control_grid_idev.addWidget(self.button_validate_idev, 2, 0)

        # Create LED label and add to grid
        # Button 1
        self.led_provision_idev = StatusIndicator()
        self.control_grid_idev.addWidget(self.led_provision_idev, 0, 1)
        # Button 2
        self.led_delete_idev = StatusIndicator()
        self.control_grid_idev.addWidget(self.led_delete_idev, 1, 1)
        # Button 3
        self.led_validate_idev = StatusIndicator()
        self.control_grid_idev.addWidget(self.led_validate_idev, 2, 1)

        # Connect buttons to API calls and update labels
        self.button_delete_idev.clicked.connect(lambda: self.delete_idev())
        self.button_bootstrap_idev.clicked.connect(lambda: self.provision_idev())
        self.button_validate_idev.clicked.connect(lambda: self.validate_idev())

        self.tab_control_ldev = QWidget()
        self.tabs.addTab(self.tab_control_ldev, 'Control IDevID')
        self.tab_control_ldev.setLayout(self.control_grid_idev)

        # ------------------
        # Control LDevID
        # ------------------

        # Create first tab
        self.control_grid_ldev = QGridLayout()
        self.control_grid_ldev.setSpacing(5)

        self.result_label_ldev = QLabel(self)
        self.result_label_idev.setFixedSize(300,250)
        self.result_label_ldev.move(80, 80)
        self.result_label_ldev.setWordWrap(True)

        self.control_grid_ldev.addWidget(self.result_label_ldev, 0, 2, 3, 2)

        # Create buttons for first tab
        self.button_bootstrap_ldev = QPushButton('Bootstrap\nLDev')
        self.button_delete_ldev = QPushButton('Delete\nLDev')
        self.button_validate_ldev = QPushButton('Validate\nLDev')
        self.button_bootstrap_ldev.setFixedSize(100,40)
        self.button_delete_ldev.setFixedSize(100,40)
        self.button_validate_ldev.setFixedSize(100,40)
        self.control_grid_ldev.addWidget(self.button_bootstrap_ldev, 0, 0)
        self.control_grid_ldev.addWidget(self.button_delete_ldev, 1, 0)
        self.control_grid_ldev.addWidget(self.button_validate_ldev, 2, 0)

        # Create LED label and add to grid
        # Button 1
        self.led_provision_ldev = StatusIndicator()
        self.control_grid_ldev.addWidget(self.led_provision_ldev, 0, 1)
        # Button 2
        self.led_delete_ldev = StatusIndicator()
        self.control_grid_ldev.addWidget(self.led_delete_ldev, 1, 1)
        # Button 3
        self.led_validate_ldev = StatusIndicator()
        self.control_grid_ldev.addWidget(self.led_validate_ldev, 2, 1)

        # Connect buttons to API calls and update labels
        self.button_delete_ldev.clicked.connect(lambda: self.delete_ldev())
        self.button_bootstrap_ldev.clicked.connect(lambda: self.provision_ldev())
        self.button_validate_ldev.clicked.connect(lambda: self.validate_ldev())

        self.tab_control_ldev = QWidget()
        self.tabs.addTab(self.tab_control_ldev, 'Control LDevID')
        self.tab_control_ldev.setLayout(self.control_grid_ldev)

        # ------------------
        # Tab for the IDevID
        # ------------------

        self.control_grid_act_idev = QGridLayout()
        self.control_grid_act_idev.setSpacing(3)

        self.actual_idev_nameplate = NameplateHeader('Nameplate')
        self.control_grid_act_idev.addWidget(self.actual_idev_nameplate, 0, 0)


        self.button_reload_idev = QPushButton()
        icon = QIcon("/home/admin/devid_nameplate/icons/rotate-icon.png")  # Load the icon from a file path
        self.button_reload_idev.setIcon(icon)
        self.button_reload_idev.setIconSize(QSize(32, 32))
        self.button_reload_idev.setFixedSize(40, 40)
        self.control_grid_act_idev.addWidget(self.button_reload_idev, 0, 1)


        self.button_reload_idev.clicked.connect(lambda: self.load_actual_idev())

        # Producer / Organization
        self.actual_idev_producer = NameplateLabel(self)
        self.actual_idev_producer_label = NameplateLabelHeader('Producer:')

        self.control_grid_act_idev.addWidget(self.actual_idev_producer_label, 1, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_producer, 1, 1)

        # Produced
        self.actual_idev_produced = NameplateLabel(self)
        self.actual_idev_produced_label = NameplateLabelHeader("Produced:")

        self.control_grid_act_idev.addWidget(self.actual_idev_produced_label,2, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_produced, 2, 1)

        # Pseudonym
        self.actual_idev_pseudonym = NameplateLabel(self)
        self.actual_idev_pseudonym_label = NameplateLabelHeader('Product:')

        self.control_grid_act_idev.addWidget(self.actual_idev_pseudonym_label,3, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_pseudonym, 3, 1)

        # Serial Number
        self.actual_idev_serial = NameplateLabel(self)
        self.actual_idev_serial_label = NameplateLabelHeader('Serial No.:')

        self.control_grid_act_idev.addWidget(self.actual_idev_serial_label, 4, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_serial, 4, 1)

        # Country
        self.actual_idev_country = NameplateLabel(self)
        self.actual_idev_country_label = NameplateLabelHeader('Country:')

        self.control_grid_act_idev.addWidget(self.actual_idev_country_label, 5, 0)
        self.control_grid_act_idev.addWidget(self.actual_idev_country, 5, 1)

        self.tab_actual_idev = QWidget()
        self.tabs.addTab(self.tab_actual_idev, 'IDevID')
        self.tab_actual_idev.setLayout(self.control_grid_act_idev)

        # ------------------
        # Tab for the LDevID
        # ------------------
        self.control_grid_act_ldev = QGridLayout()
        self.control_grid_act_ldev.setSpacing(5)

        self.result_actual_ldev = QLabel(self)
        self.result_actual_ldev.setFixedSize(350,250)
        self.result_actual_ldev.move(30, 30)
        self.result_actual_ldev.setWordWrap(True)

        self.control_grid_act_ldev.addWidget(self.result_actual_ldev, 0, 1, 1, 1)

        self.button_reload_ldev = QPushButton()
        icon = QIcon("/home/admin/devid_nameplate/icons/rotate-icon.png")  # Load the icon from a file path
        self.button_reload_ldev.setIcon(icon)
        self.button_reload_ldev.setIconSize(QSize(32, 32))
        self.button_reload_ldev.setFixedSize(50, 50)
        self.control_grid_act_ldev.addWidget(self.button_reload_ldev, 0, 0)


        self.button_reload_ldev.clicked.connect(lambda: self.load_actual_ldev())

        self.tab_actual_ldev = QWidget()
        self.tabs.addTab(self.tab_actual_ldev, 'LDevID')
        self.tab_actual_ldev.setLayout(self.control_grid_act_ldev)

    def delete_idev(self):
        idevapi = HighlevelIdev()
        response = idevapi.delete()
        if response['success']:
            self.led_delete_idev.setStyleSheet("background-color: green")
        else:
            self.led_delete_idev.setStyleSheet("background-color: red")
        self.results_control_idev.append(json.dumps(response["message"]))
        self.result_label_idev.setText(json.dumps(self.results_control_idev[-1]))

    def provision_idev(self):
        idevapi = HighlevelIdev()
        response = idevapi.provision()
        if response['success']:
            self.led_provision_idev.setStyleSheet("background-color: green")
        else:
            self.led_provision_idev.setStyleSheet("background-color: red")
        #print(response)
        self.results_control_idev.append(json.dumps(response["message"]))
        self.result_label_idev.setText(json.dumps(self.results_control_idev[-1]))

    def validate_idev(self):
        idevapi = HighlevelIdev()
        response = idevapi.validate()
        print(response)
        if response['success']:
            self.led_validate_idev.setStyleSheet("background-color: green")
        else:
            self.led_validate_idev.setStyleSheet("background-color: red")
        self.results_control_idev.append(json.dumps(response["message"]))
        self.result_label_idev.setText(json.dumps(self.results_control_idev[-1]))

    def delete_ldev(self):
        ldevapi = HighlevelLdev()
        response = ldevapi.delete()
        if response['success']:
            self.led_delete_ldev.setStyleSheet("background-color: green")
        else:
            self.led_delete_ldev.setStyleSheet("background-color: red")
        self.results_control_ldev.append(json.dumps(response["message"]))
        self.result_label_ldev.setText(json.dumps(self.results_control_ldev[-1]))

    def provision_ldev(self):
        ldevapi = HighlevelLdev()
        response = ldevapi.provision()
        if response['success']:
            self.led_provision_ldev.setStyleSheet("background-color: green")
        else:
            self.led_provision_ldev.setStyleSheet("background-color: red")
        #print(response)
        self.results_control_ldev.append(json.dumps(response["message"]))
        self.result_label_ldev.setText(json.dumps(self.results_control_ldev[-1]))

    def validate_ldev(self):
        ldevapi = HighlevelLdev()
        response = ldevapi.validate()
        print(response)
        if response['success']:
            self.led_validate_ldev.setStyleSheet("background-color: green")
        else:
            self.led_validate_ldev.setStyleSheet("background-color: red")
        self.results_control_ldev.append(json.dumps(response["message"]))
        self.result_label_ldev.setText(json.dumps(self.results_control_ldev[-1]))


    def load_actual_idev(self):
        idevapi = HighlevelIdev()
        response = idevapi.provide()
        self.results_idev_cycle.append(json.dumps(response["data"]))
        self.actual_idev_producer.setText(json.dumps(response["data"]["o"]))
        self.actual_idev_serial.setText(json.dumps(response["data"]["serial_number"]))
        self.actual_idev_produced.setText(json.dumps(response["data"]["validFrom"]))
        self.actual_idev_country.setText(json.dumps(response["data"]["c"]))
        self.actual_idev_pseudonym.setText(json.dumps(response["data"]["pseudonym"]))


    def load_actual_ldev(self):
        ldevapi = HighlevelLdev()
        response = ldevapi.provide()
        self.results_ldev_cycle.append(json.dumps(response["data"]["issuer"]))
        self.result_actual_ldev.setText(json.dumps(self.results_ldev_cycle[-1]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())