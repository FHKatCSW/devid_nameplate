import json
import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QLabel, \
    QGridLayout, QDesktopWidget

from gui.funs.highlevel import HighlevelIdev, HighlevelLdev
from gui.funs.rest import RestApiClient
from gui.funs.status_led import RestLed


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
            QLabel {
                background-color: #EFEFEF;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 3px;
                margin: 3px;
                color: black;
                font-size: 16pt;
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
        self.status_label_rest = QLabel("REST API")
        self.status_label_rest.setFixedHeight(50)
        self.status_label_rest.setFixedWidth(200)
        self.status_grid.addWidget(self.status_label_rest, 0, 0)
        rest_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/rest")
        self.status_grid.addWidget(rest_led, 0, 1)

        # Status for HSM
        self.status_label_hsm = QLabel("HSM")
        self.status_label_hsm.setFixedHeight(50)
        self.status_grid.addWidget(self.status_label_hsm, 1, 0)
        hsm_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/hsm")
        self.status_grid.addWidget(hsm_led, 1, 1)


        # Status for IDevID
        self.status_label_idev = QLabel("IDevID")
        self.status_label_idev.setFixedHeight(50)
        self.status_grid.addWidget(self.status_label_idev, 2, 0)
        idev_led = RestLed(url="http://0.0.0.0:5000/v1", endpoint="/mgmt/status/idevid")
        self.status_grid.addWidget(idev_led, 2, 1)

        # Status for LDevID
        self.status_label_ldev = QLabel("LDevID")
        self.status_label_ldev.setFixedHeight(50)
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
        self.result_label_idev.move(80, 80)
        self.result_label_idev.setWordWrap(True)

        self.control_grid_idev.addWidget(self.result_label_idev, 0, 2, 3, 2)

        # Create buttons for first tab
        self.button_delete_idev = QPushButton('Delete LDev')
        self.button_provision_idev = QPushButton('Provision LDev')
        self.button_validate_idev = QPushButton('Validate LDev')
        self.control_grid_idev.addWidget(self.button_delete_idev, 0, 0)
        self.control_grid_idev.addWidget(self.button_provision_idev, 1, 0)
        self.control_grid_idev.addWidget(self.button_validate_idev, 2, 0)

        # Create LED label and add to grid
        # Button 1
        self.led_delete_idev = QLabel()
        self.led_delete_idev.setFixedSize(20, 20)
        self.control_grid_idev.addWidget(self.led_delete_idev, 0, 1)
        # Button 2
        self.led_provision_idev = QLabel()
        self.led_provision_idev.setFixedSize(20, 20)
        self.control_grid_idev.addWidget(self.led_provision_idev, 1, 1)
        # Button 3
        self.led_validate_idev = QLabel()
        self.led_validate_idev.setFixedSize(20, 20)
        self.control_grid_idev.addWidget(self.led_validate_idev, 2, 1)

        # Connect buttons to API calls and update labels
        self.button_delete_idev.clicked.connect(lambda: self.delete_idev())
        self.button_provision_idev.clicked.connect(lambda: self.provision_idev())
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
        self.result_label_ldev.move(80, 80)
        self.result_label_ldev.setWordWrap(True)

        self.control_grid_ldev.addWidget(self.result_label_ldev, 0, 2, 3, 2)

        # Create buttons for first tab
        self.button_delete_ldev = QPushButton('Delete LDev')
        self.button_provision_ldev = QPushButton('Provision LDev')
        self.button_validate_ldev = QPushButton('Validate LDev')
        self.control_grid_ldev.addWidget(self.button_delete_ldev, 0, 0)
        self.control_grid_ldev.addWidget(self.button_provision_ldev, 1, 0)
        self.control_grid_ldev.addWidget(self.button_validate_ldev, 2, 0)

        # Create LED label and add to grid
        # Button 1
        self.led_delete_ldev = QLabel()
        self.led_delete_ldev.setFixedSize(20, 20)
        self.control_grid_ldev.addWidget(self.led_delete_ldev, 0, 1)
        # Button 2
        self.led_provision_ldev = QLabel()
        self.led_provision_ldev.setFixedSize(20, 20)
        self.control_grid_ldev.addWidget(self.led_provision_ldev, 1, 1)
        # Button 3
        self.led_validate_ldev = QLabel()
        self.led_validate_ldev.setFixedSize(20, 20)
        self.control_grid_ldev.addWidget(self.led_validate_ldev, 2, 1)

        # Connect buttons to API calls and update labels
        self.button_delete_ldev.clicked.connect(lambda: self.delete_ldev())
        self.button_provision_ldev.clicked.connect(lambda: self.provision_ldev())
        self.button_validate_ldev.clicked.connect(lambda: self.validate_ldev())

        self.tab_control_ldev = QWidget()
        self.tabs.addTab(self.tab_control_ldev, 'Control LDevID')
        self.tab_control_ldev.setLayout(self.control_grid_ldev)

        # ------------------
        # Tab for the IDevID
        # ------------------
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab2, 'IDevID')

        # Add label for IDevID
        self.output_idev = QLabel(self.tab2)
        self.output_idev.setWordWrap(True)
        self.output_idev.setMaximumSize(max_width, max_height)
        self.output_idev.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self.tab2)
        layout.addWidget(self.output_idev)

        # Set up timer for IDevID API call
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cycle_idev_api_call)
        self.timer.start(5000)

        # ------------------
        # Tab for the LDevID
        # ------------------
        self.tab3 = QWidget()
        self.tabs.addTab(self.tab3, 'LDevID')

        # Add label for LDevID
        self.output_ldev = QLabel(self.tab3)
        self.output_ldev.setWordWrap(True)
        self.output_ldev.setMaximumSize(max_width, max_height)
        self.output_ldev.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self.tab3)
        layout.addWidget(self.output_ldev)

        # Set up timer for LDevID API call
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cycle_ldev_api_call)
        self.timer.start(5000)

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

    def cycle_idev_api_call(self):
        idevapi = HighlevelIdev()
        response = idevapi.provide()
        self.results_idev_cycle.append(json.dumps(response["message"]))
        self.output_idev.setText(json.dumps(self.results_idev_cycle[-1]))

    def cycle_ldev_api_call(self):
        # Perform API call 3 and update label text
        call = RestApiClient(base_url='https://api.example.com/1')
        response = call.post(endpoint="/v1")
        self.results_ldev_cycle.append(json.dumps(response["message"]))
        self.output_ldev.setText(json.dumps(self.results_ldev_cycle[-1]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())