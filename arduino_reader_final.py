
import os
import sys
import time
import serial
import serial.tools.list_ports
import multiprocessing
import socket
import logging
from flask import Flask, jsonify, request
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QWidget, QStyle, QApplication, QLayout,
    QStackedWidget, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QHeaderView, QSpacerItem, QSizePolicy, QFrame, QItemDelegate
)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QRect, QRectF, QSize, QUrl
from PyQt5.QtGui import QFont, QFontDatabase, QCursor, QBrush, QColor, QPainter, QPen, QPainterPath, QPalette, QDesktopServices
from collections import deque

import styles


class PortLineEdit(QLineEdit):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.default_prefix = "Port: "
            self.original_text = "5001"  # Default port number
            self.setText(f"{self.default_prefix}{self.original_text}")
            self.editing = False

        def focusInEvent(self, event):
            """Remove the 'Port: ' prefix when entering editing mode."""
            if not self.editing:
                self.setText(self.original_text)
                self.editing = True
            super().focusInEvent(event)

        def focusOutEvent(self, event):
            """Restore the 'Port: ' prefix when exiting editing mode."""
            if self.editing:
                self.validate_and_restore()
            super().focusOutEvent(event)

        def keyPressEvent(self, event):
            """Handle Enter key to exit editing mode."""
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.clearFocus()  # Trigger focusOutEvent
            else:
                super().keyPressEvent(event)

        def validate_and_restore(self):
            """Validate input and restore 'Port: ' prefix."""
            text = self.text().strip()
            if text.isdigit():
                self.original_text = text
            self.setText(f"{self.default_prefix}{self.original_text}")
            self.editing = False

class ClickableWidget(QWidget):
    def mousePressEvent(self, event):
        """Clear focus from any child widget when clicking outside."""
        focused_widget = QApplication.focusWidget()
        if focused_widget:
            focused_widget.clearFocus()
        super().mousePressEvent(event)

from PyQt5.QtWidgets import QItemDelegate, QApplication
from PyQt5.QtGui import QPainter, QPainterPath, QBrush, QColor
from PyQt5.QtCore import Qt, QTimer, QRectF

class BottomRightRoundedCornerDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.previous_values = {}  # Cache previous values to reduce repaints

    def paint(self, painter, option, index):
        # 🔹 Detect dark mode
        dark_mode = QApplication.instance().palette().color(QPalette.Window).value() < 128  

        # 🔹 Define colors based on dark/light mode
        selected_bg_color = "#0072C3" if dark_mode else "#1192E8"
        text_color = "#FFFFFF" if dark_mode else "#121619"
        default_bg_color = "#171B1F" if dark_mode else "#F2F4F8"

        # Detect table and column properties
        table = index.model().parent()
        if not table:
            return super().paint(painter, option, index)

        first_column_x = table.columnViewportPosition(3)
        full_width = table.viewport().width() - first_column_x

        is_last_row = index.row() == index.model().rowCount() - 1
        is_selected = option.state & QStyle.State_Selected

        painter.save()
        rect = option.rect

        # 🔹 Always draw selection background (ensures selection is visible)
        if is_selected:
            path = QPainterPath()
            corner_radius = 15
            x, y, w, h = first_column_x, rect.y(), full_width, rect.height()

            path.moveTo(x, y)
            path.lineTo(x + w, y)

            if is_last_row:
                path.lineTo(x + w, y + h - corner_radius)
                path.arcTo(QRectF(x + w - corner_radius * 2, y + h - corner_radius * 2, corner_radius * 2, corner_radius * 2), 0, -90)
            else:
                path.lineTo(x + w, y + h)

            path.lineTo(x, y + h)

            if is_last_row:
                path.lineTo(x, y + h)

            path.lineTo(x, y)

            painter.setClipPath(path)
            painter.fillPath(path, QBrush(QColor(selected_bg_color)))

        # 🔹 Optimize: Skip unnecessary repaints, but always paint last column
        current_value = index.data(Qt.DisplayRole)
        previous_value = self.previous_values.get((index.row(), index.column()), None)

        if current_value != previous_value or index.column() == table.columnCount() - 1:
            # Store new value in cache
            self.previous_values[(index.row(), index.column())] = current_value

            # Draw text **after** background to ensure visibility
            painter.setPen(QColor(text_color))
            if current_value:
                painter.drawText(
                    rect.adjusted(5, 0, -5, 0),
                    Qt.AlignLeft | Qt.AlignVCenter,
                    current_value
                )

        painter.restore()

# --------------------------------------------------------------------
# Logging Configuration
# --------------------------------------------------------------------
logging.basicConfig(
    filename='arduino_dashboard.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --------------------------------------------------------------------
# Flask App
# --------------------------------------------------------------------
app = Flask(__name__)

def run_flask_app(host, port, arduino_data, outgoing_data):
    """
    arduino_data: Manager dict storing data read from the Arduino.
    outgoing_data: Manager list for posted data to send to Arduino.
    """
    @app.route('/', methods=['GET', 'POST'])
    def dashboard_route():
        if request.method == 'GET':
            # Return ONLY the data that came from Arduino
            if not arduino_data:
                return jsonify({"message": "No Arduino data available"}), 200
            return jsonify(dict(arduino_data)), 200

        elif request.method == 'POST':
            data = request.get_json()
            if not data or not isinstance(data, dict):
                return jsonify({"error": "Invalid data format. Expected a JSON object."}), 400

            for key, value in data.items():
                if key is None or value is None:
                    return jsonify({"error": "All keys and values must be non-null."}), 400

            # Add data to the outgoing list
            outgoing_data.append(data)
            return jsonify({"message": "Data received and queued to send to Arduino."}), 200

    app.run(host=host, port=port, use_reloader=False)

# --------------------------------------------------------------------
# Custom Labels
# --------------------------------------------------------------------
class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip("Click to copy")

    def mousePressEvent(self, event):
        if self.text():
            QApplication.clipboard().setText(self.text())
        super().mousePressEvent(event)


class CodeCopyLabel(QLabel):
    """
    A QLabel that opens a URL on click instead of copying text.
    """
    def __init__(self, display_text, url, parent=None):
        super().__init__(display_text, parent)
        self.url = url
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet("background-color: none;")
        self.setAlignment(Qt.AlignCenter)
        self.setToolTip("Click to download files")

    def mousePressEvent(self, event):
        if self.url:
            QDesktopServices.openUrl(QUrl(self.url))
        super().mousePressEvent(event)

# --------------------------------------------------------------------
# Arduino Searcher Thread
# --------------------------------------------------------------------
class ArduinoSearcher(QThread):
    found_port = pyqtSignal(str)
    no_port = pyqtSignal()
    progress = pyqtSignal(str)

    def __init__(self, baud_rate, identifier, test_duration=5):
        super().__init__()
        self.baud_rate = baud_rate
        self.identifier = identifier
        self.test_duration = test_duration

    def run(self):
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            self.no_port.emit()
            return

        for port in ports:
            self.progress.emit(f"Testing port: {port.device}")
            try:
                with serial.Serial(port.device, self.baud_rate, timeout=0.5) as ser_:
                    start_time = time.time()
                    end_time = start_time + self.test_duration
                    while time.time() < end_time:
                        if ser_.in_waiting:
                            line = ser_.readline().decode('utf-8').strip()
                            if line == self.identifier:
                                self.found_port.emit(port.device)
                                return
                        else:
                            time.sleep(0.1)
            except serial.SerialException:
                pass
        self.no_port.emit()

# --------------------------------------------------------------------
# Main ArduinoApp
# --------------------------------------------------------------------
class ArduinoApp(QMainWindow):
    def __init__(self, arduino_data, outgoing_data,
                 baud_rate=9600, identifier="ARDUINO_READY"):
        super().__init__()

        # (1) Detect system dark/light mode
        dark_mode = QApplication.instance().palette().color(QPalette.Window).value() < 128  

        # (2) Fetch styles from styles.py and store them as an instance variable
        self.styles_dict = styles.get_stylesheet(dark_mode)

        # (1) Dynamically resolve the font path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(script_dir, "fonts", "ReadexPro-Medium.ttf")

        # (2) Load and apply the font
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Failed to load the font! Falling back to default system font.")
            font_family = "Arial"
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            print(f"Loaded custom font: {font_family}")

        # Set the global font for the entire application
        QApplication.setFont(QFont(font_family, 12))

        # Setup global layout and styles
        self.setup_global_layout_constants()
        self.setup_global_styles()

        # Rest of your initialization
        self.arduino_data = arduino_data
        self.outgoing_data = outgoing_data
        self.baud_rate = baud_rate
        self.identifier = identifier

        self.arduino = None
        self.port = None
        self.arduino_name = None

        self.data = {}
        self.server_process = None
        self.is_server_running = False

        self.sent_data = {}
        self.received_data = {}
        self.sent_attempt_times_buffer = {}
        self.received_update_times_buffer = {}

        self.sent_baseline_averages = {}
        self.received_baseline_averages = {}
        self.last_sent_values = {}

        self.threshold_percentage = 0.10

        
        self.setGeometry(100, 100, 800, 600)
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Setup global layout constants
        self.setup_global_layout_constants()

        self.start_screen()
        self.searching_screen()
        self.dashboard_screen()
        self.stacked_widget.setCurrentWidget(self.start_screen_widget)
        self.stacked_widget.setStyleSheet(self.styles_dict["background_style"])

        # Timers
        self.age_timer = QTimer()
        self.age_timer.timeout.connect(self.update_table)
        self.age_timer.start(1000)

        self.outgoing_timer = QTimer()
        self.outgoing_timer.timeout.connect(self.process_outgoing_data)
        self.outgoing_timer.start(500)

        
    # ----------------------------------------------------------------
    # UI Setup
    # ----------------------------------------------------------------


    def setup_global_layout_constants(self):
        """Define global layout constants."""
        self.spacer_distance_1 = QSpacerItem(5, 20, QSizePolicy.Fixed, QSizePolicy.Fixed)  # Small distance
        self.spacer_distance_2 = QSpacerItem(20, 40, QSizePolicy.Fixed, QSizePolicy.Fixed)  # Larger distance

    def setup_global_styles(self):
        """Applies global styles based on system dark/light mode."""

        # Detect system theme mode
        dark_mode = QApplication.instance().palette().color(QPalette.Window).value() < 128  
        # Define text colors based on theme
        text_color = "#FFFFFF" if dark_mode else "#121619"  # White for dark mode, black for light mode


        # Fetch the correct styles
        styles_dict = styles.get_stylesheet(dark_mode)

        # Apply the styles to the application
        self.setStyleSheet(
            styles_dict["box_style"] +
            styles_dict["box_style_2"] +
            styles_dict["box_style_3"] +
            styles_dict["button_style"] +
            styles_dict["button_style_server"] +
            styles_dict["button_style_disconnect"] +
            styles_dict["button_style_inactive"] +
            styles_dict["button_small_style"] +
            styles_dict["label_style"] +
            styles_dict["background_style"] +
            styles_dict["table_style"]
        )

    def start_screen(self):
        self.start_screen_widget = QWidget()
        layout = QVBoxLayout()
        self.setWindowTitle("Device Setup")
        # Add stretch space at the top
        layout.addStretch(1)

        # Add "Make sure Arduino code is correct" text
        arduino_code = """unsigned long lastSendTimeData = 0;  // ...
    [Your Arduino code here]
    """

        arduino_url = "http://maxemrich.de/Downloads/Examples_Arduino_Grasshopper.zip"
        self.copy_code_label = CodeCopyLabel(
            display_text="Grab the correct Arduino and Grasshopper files (click to download)",
            url=arduino_url
        )
        self.copy_code_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.copy_code_label, alignment=Qt.AlignCenter)

        # Add distance between the text and button
        layout.addItem(self.spacer_distance_1)

        # Add "Search for Arduino" button
        self.start_button = QPushButton("Search for Arduino")
        self.start_button.setStyleSheet(self.styles_dict["button_style"])
        self.start_button.setFixedSize(200, 50)
        self.start_button.clicked.connect(self.start_search)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Add larger distance (Distance 2) below the button
        layout.addItem(self.spacer_distance_2)

        # Final layout setup
        self.start_screen_widget.setLayout(layout)
        self.stacked_widget.addWidget(self.start_screen_widget)

    def searching_screen(self):

        self.searching_screen_widget = QWidget()
        layout = QVBoxLayout()

        # Add larger distance (Distance 2) above the text
        layout.addItem(self.spacer_distance_2)

        # Add "Testing ports" text
        self.search_label = QLabel("Testing ports...")
        self.search_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.search_label, alignment=Qt.AlignCenter)

        # Add stretch space at the top
        layout.addStretch(1)

        # Add a label for showing progress (current line)
        self.current_line_label = QLabel("")
        self.current_line_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.current_line_label, alignment=Qt.AlignCenter)

        # Add smaller distance (Distance 1) before the button
        layout.addItem(self.spacer_distance_1)

        # Add "Cancel Search" button
        self.cancel_button = QPushButton("Cancel Search")
        self.cancel_button.setStyleSheet(self.styles_dict["button_style_disconnect"])
        self.cancel_button.setFixedSize(200, 50)
        self.cancel_button.clicked.connect(self.cancel_search)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignCenter)

        # Add larger distance (Distance 2) below the button
        layout.addItem(self.spacer_distance_2)

        # Final layout setup
        self.searching_screen_widget.setLayout(layout)
        self.stacked_widget.addWidget(self.searching_screen_widget)

    def dashboard_screen(self):
        self.dashboard_widget = ClickableWidget()
        main_layout = QVBoxLayout()
        # Horizontal Layout for Name and Port Boxes
        top_layout = QHBoxLayout()

        main_layout.setContentsMargins(20, 20, 20, 40)
        main_layout.setSpacing(0)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)
        
        main_layout.setSizeConstraint(QLayout.SetMinimumSize)

        # Arduino Name Box
        self.name_label = QLabel("Arduino: Not Connected")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet(self.styles_dict["box_style_2"])  # Apply style for the text
        self.name_label.setFixedHeight(30)  # Fixed height
        self.name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Adaptive width

        # Add stretch space at the top

        # Port Field
        self.port_input = PortLineEdit()
        self.port_input.setStyleSheet(self.styles_dict["label_style"])
        self.port_input.setFixedHeight(30)  # Fixed height
        self.port_input.setFixedWidth(100)

        # Server Address Label
        self.server_address_label = ClickableLabel("")
        self.server_address_label.setStyleSheet(self.styles_dict["box_style_3"])
        self.server_address_label.setFixedHeight(30)  # Fixed height
        self.server_address_label.hide()

        # Layout
        top_layout.addWidget(self.name_label)
        top_layout.addStretch(1)
        top_layout.addWidget(self.port_input)
        top_layout.addWidget(self.server_address_label)
        main_layout.addLayout(top_layout)        

        # Data Table with Rounded Frame
        table_frame = QFrame()
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 10, 0, 10)
        table_layout.setSpacing(0)  # Remove spacing between widgets

        self.data_table = QTableWidget(5, 4)  # Start with 5 rows, 4 columns


        # Remove any existing minimum or maximum sizes
        self.data_table.setMinimumSize(0, 0)
        self.data_table.verticalHeader().setDefaultSectionSize(30)  # Each row 30px

        # Similarly, reset size constraints on the frame
        table_frame.setMinimumSize(0, 0)

        # Apply the custom delegate
        delegate = BottomRightRoundedCornerDelegate()
        self.data_table.setItemDelegateForColumn(self.data_table.columnCount() - 1, delegate)
        self.data_table.setHorizontalHeaderLabels(["Parameter", "Value", "Last Update (ms)", "Source"])
        self.data_table.setStyleSheet(self.styles_dict["table_style"])
        self.data_table.setCornerButtonEnabled(False)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.data_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.data_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.data_table.setShowGrid(False)

        vertical_header = self.data_table.verticalHeader()
        vertical_header.setDefaultAlignment(Qt.AlignCenter)
        

        # Adjust header sections
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Stretch first column
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        # Set the stretch alignment for the entire header
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Add table to layout
        table_layout.addWidget(self.data_table, stretch=2)  # Let table take up all available space

        # Clear Data Button
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.setContentsMargins(0, 10, 0, 0)
        self.clear_button = QPushButton("Clear Data")
        self.clear_button.setFixedHeight(30)
        self.clear_button.setStyleSheet(self.styles_dict["button_small_style"])
        self.clear_button.clicked.connect(self.clear_data)
        button_layout.addWidget(self.clear_button)
        table_layout.addLayout(button_layout)


        # Add table frame to main layout
        main_layout.addWidget(table_frame, stretch=1)  # Allow table to take up available space

        # Add stretch space between the "Clear Data" button and the next buttons
        stretch_spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(stretch_spacer)



        # Add Start Local Server and Disconnect Arduino Buttons
        button_layout2 = QVBoxLayout()
        button_layout2.addStretch(0)

        # Start Local Server Button
        self.server_button = QPushButton("Start Local Server")
        self.server_button.setFixedSize(200, 50)
        self.server_button.setStyleSheet(self.styles_dict["button_style_server"])
        self.server_button.clicked.connect(self.toggle_server)
        button_layout2.addWidget(self.server_button, alignment=Qt.AlignCenter)

        button_layout2.addItem(self.spacer_distance_1)

        # Disconnect Arduino Button
        self.disconnect_button = QPushButton("Disconnect Arduino")
        self.disconnect_button.setFixedSize(200, 50)
        self.disconnect_button.setStyleSheet(self.styles_dict["button_style_disconnect"])
        self.disconnect_button.clicked.connect(self.handle_disconnect)
        button_layout2.addWidget(self.disconnect_button, alignment=Qt.AlignCenter)

        main_layout.addLayout(button_layout2)
        

        self.dashboard_widget.setLayout(main_layout)
        self.stacked_widget.addWidget(self.dashboard_widget)

    # ----------------------------------------------------------------
    # Searching & Connection
    # ----------------------------------------------------------------
            
    def update_port_display(self):
        """Update the displayed port value when editing is finished."""
        port_text = self.port_input.text().strip()
        if port_text.isdigit():
            self.port_input.setText(f"Port: {port_text}")  # Format the display
        else:
            self.port_input.setText("Port: 5001")  # Revert to default if invalid

    def show_server_ui(self, server_url):
        """Show the server address view."""
        self.server_address_label.setText(server_url)
        self.server_address_label.show()
        self.port_input.hide()

    def show_port_ui(self):
        """Show the port input view."""
        self.server_address_label.hide()
        self.port_input.show()

    def start_search(self):
        self.reset_connection()
        self.stacked_widget.setCurrentWidget(self.searching_screen_widget)
        self.current_line_label.setText("")  # Clear the progress label
        self.searcher = ArduinoSearcher(self.baud_rate, self.identifier, test_duration=5)
        self.searcher.found_port.connect(self.on_port_found)
        self.searcher.no_port.connect(self.on_no_port)
        self.searcher.progress.connect(self.on_search_progress)
        self.searcher.start()
        self.setWindowTitle("Searing for Device")

    def cancel_search(self):
        if hasattr(self, 'searcher') and self.searcher and self.searcher.isRunning():
            self.searcher.found_port.disconnect(self.on_port_found)
            self.searcher.no_port.disconnect(self.on_no_port)
            self.searcher.progress.disconnect(self.on_search_progress)
            self.searcher.quit()
            self.searcher.wait(500)
            if self.searcher.isRunning():
                self.searcher.terminate()
                self.searcher.wait()
            self.searcher = None

        self.current_line_label.setText("Search canceled.")
        QApplication.processEvents()
        QTimer.singleShot(2000,
                          lambda: self.stacked_widget.setCurrentWidget(self.start_screen_widget))
        self.setWindowTitle("Device Setup")

    def on_search_progress(self, message):
        self.current_line_label.setText(message)
        QApplication.processEvents()

    def on_port_found(self, port):
        self.port = port
        if self.searcher and self.searcher.isRunning():
            self.searcher.quit()
            self.searcher.wait()
            self.searcher = None
        self.connect_to_arduino()

    def on_no_port(self):
        self.current_line_label.setText("No ports found.")
        QTimer.singleShot(2000, self.start_search)

    def connect_to_arduino(self):
        global ser
        try:
            self.arduino = serial.Serial(self.port, self.baud_rate, timeout=1)
            ser = self.arduino
            self.stacked_widget.setCurrentWidget(self.dashboard_widget)
            self.show_port_ui()
            self.arduino.write(b"CONNECTED\n")
            QTimer.singleShot(500, self.read_arduino_name)
            self.last_sent_values.clear()
        except serial.SerialException as e:
            self.search_label.setText(f"Error: {e}")
            QTimer.singleShot(2000, self.start_search)
        self.setWindowTitle("Dashboard")

    def read_arduino_name(self):
        """Read the Arduino name and transition to data reading."""
        if not self.arduino or not self.arduino.is_open:
            logging.error("Cannot read Arduino name: Serial connection is not open.")
            return

        timeout = 5  # Timeout for reading name
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.arduino.in_waiting:
                try:
                    # Read line from the serial buffer
                    line = self.arduino.readline().decode('utf-8').strip()
                    logging.debug(f"Received from Arduino: {line}")

                    # Check if the line contains the name
                    if line.startswith("NAME:"):
                        self.arduino_name = line[5:].strip()
                        self.name_label.setText(f"Arduino: {self.arduino_name}")
                        logging.info(f"Arduino name updated: {self.arduino_name}")
                        break  # Exit the name-reading loop
                except Exception as e:
                    logging.error(f"Error reading Arduino name: {e}")

        # Transition to data reading
        QTimer.singleShot(100, self.read_data)  # Start reading data

    def handle_disconnect(self):
        if self.is_server_running:
            logging.info("Stopping server before disconnecting Arduino.")
            self.stop_server()

        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            logging.info("Arduino disconnected.")

        self.reset_connection()
        self.stacked_widget.setCurrentWidget(self.start_screen_widget)
        self.setWindowTitle("Device Setup")

    # ----------------------------------------------------------------
    # Clearing & Reset
    # ----------------------------------------------------------------
    def clear_data(self):
        self.data.clear()
        self.sent_data.clear()
        self.received_data.clear()
        self.sent_attempt_times_buffer.clear()
        self.received_update_times_buffer.clear()
        self.sent_baseline_averages.clear()
        self.received_baseline_averages.clear()
        self.last_sent_values.clear()
        self.data_table.setRowCount(0)

        self.arduino_data.clear()
        logging.info("All data and buffers cleared.")

    def reset_connection(self):
        self.port = None
        self.arduino = None
        self.data.clear()
        self.sent_data.clear()
        self.received_data.clear()
        self.sent_attempt_times_buffer.clear()
        self.received_update_times_buffer.clear()
        self.sent_baseline_averages.clear()
        self.received_baseline_averages.clear()
        self.last_sent_values.clear()

        self.arduino_data.clear()
        logging.info("Connection & buffers reset.")

        self.name_label.setText("Arduino: Not Connected")
        self.server_address_label.setText("")
        self.show_port_ui()

    # ----------------------------------------------------------------
    # Server
    # ----------------------------------------------------------------
    def toggle_server(self):
        if not self.is_server_running:
            self.start_server()
        else:
            self.stop_server()

    def is_port_available(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    def start_server(self):
        port_text = self.port_input.text().replace("Port: ", "").strip()
        port = 5001
        if port_text:
            try:
                port = int(port_text)
                if not (1 <= port <= 65535):
                    raise ValueError("Port out of range")
            except ValueError:
                QMessageBox.warning(self, "Invalid Port",
                                    "Please enter a valid port number (1-65535) or leave blank for 5001.")
                logging.warning(f"Invalid port: {port_text}")
                return

        if not self.is_port_available(port):
            QMessageBox.warning(self, "Port in Use",
                                f"Port {port} is in use.")
            logging.warning(f"Port {port} is in use.")
            return

        self.server_button.setText("Starting Server...")
        self.server_button.setStyleSheet(self.styles_dict["button_style_inactive"])
        self.server_button.setEnabled(False)

        self.server_process = multiprocessing.Process(
            target=run_flask_app,
            args=('0.0.0.0', port, self.arduino_data, self.outgoing_data)
        )
        self.server_process.start()
        self.is_server_running = True
        QTimer.singleShot(500, lambda: self.update_server_started(port))
        logging.info(f"Started Flask server on port {port}.")

    def update_server_started(self, port):
        self.server_button.setText("Stop Server")
        self.server_button.setStyleSheet(self.styles_dict["button_style_disconnect"])
        self.server_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.setStyleSheet(self.styles_dict["button_style_inactive"])

        ip = socket.gethostbyname(socket.gethostname())
        server_url = f"http://{ip}:{port}"
        self.show_server_ui(server_url)
        logging.info(f"Flask server running at {server_url}.")

    def stop_server(self):
        self.server_button.setText("Stopping Server...")
        self.server_button.setStyleSheet(self.styles_dict["button_style_inactive"])
        self.server_button.setEnabled(False)
        if self.is_server_running and self.server_process_running():
            self.server_process.terminate()
            self.server_process.join()
            logging.info("Flask server terminated.")
        self.is_server_running = False
        self.server_process = None
        QTimer.singleShot(500, self.update_server_stopped)
        self.show_port_ui()

    def update_server_stopped(self):
        self.server_button.setText("Start Local Server")
        self.server_button.setEnabled(True)
        self.server_button.setStyleSheet(self.styles_dict["button_style_server"])
        self.disconnect_button.setEnabled(True)
        self.disconnect_button.setStyleSheet(self.styles_dict["button_style_disconnect"])
        logging.info("Flask server stopped.")
        self.show_port_ui()

    def server_process_running(self):
        return self.server_process and self.server_process.is_alive()

    # ----------------------------------------------------------------
    # Baseline Calculation
    # ----------------------------------------------------------------
    def calculate_baseline(self, buffer, min_samples=20):
        if len(buffer) < min_samples:
            logging.debug(f"Not enough samples for baseline: {len(buffer)}/{min_samples}.")
            return None

        intervals = [buffer[i] - buffer[i - 1] for i in range(1, len(buffer))]
        if not intervals:
            return None

        avg_interval_ms = int(sum(intervals) / len(intervals) * 1000)
        logging.debug(f"Baseline: {avg_interval_ms} ms from {len(buffer)} timestamps.")
        return avg_interval_ms

    # ----------------------------------------------------------------
    # Reading from Arduino
    # ----------------------------------------------------------------
    def read_data(self):
        if not self.arduino or not self.arduino.is_open:
            return

        try:
            while self.arduino.in_waiting:
                line = self.arduino.readline().decode('utf-8').strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    key, value = key.strip(), value.strip()

                    if key.lower() == "name":
                        continue

                    now_ts = time.time()
                    buf = self.received_update_times_buffer.setdefault(key, deque(maxlen=50))
                    buf.append(now_ts)

                    old_val = self.data.get(key)
                    if old_val != value:
                        self.data[key] = value
                        self.arduino_data[key] = value
                        self.received_data[key] = {'value': value, 'timestamp': now_ts}
                        logging.info(f"'{key}' changed => {value}")
                    else:
                        self.received_data[key] = {'value': value, 'timestamp': now_ts}
                        logging.debug(f"'{key}' unchanged. Timestamp appended.")

                    new_baseline = self.calculate_baseline(buf, min_samples=20)
                    if new_baseline:
                        self.received_baseline_averages[key] = new_baseline

        except (serial.SerialException, OSError, Exception) as e:
            logging.error(f"Exception in read_data: {e}")
            self.handle_disconnect()

        QTimer.singleShot(100, self.read_data)

    # ----------------------------------------------------------------
    # Updating the Table
    # ----------------------------------------------------------------
    def update_table(self):

        # Detect dark/light mode
        dark_mode = QApplication.instance().palette().color(QPalette.Window).value() < 128  

        # Define colors based on theme
        bg_color = "#171B1F" if dark_mode else "#DDE1E6"  # Dark background for dark mode, light for light mode
        text_color = "#FFFFFF" if dark_mode else "#121619"  # White text for dark mode, black for light mode

        current_time = time.time()
        self.data_table.setRowCount(len(self.data))
        row = 0

        for key, value in self.data.items():
            if key in self.received_data and self.received_data[key]['value'] == value:
                source = "From Arduino"
                buf = self.received_update_times_buffer.get(key, deque())
                baseline_ms = self.received_baseline_averages.get(key)
            elif key in self.sent_attempt_times_buffer:
                source = "To Arduino"
                buf = self.sent_attempt_times_buffer.get(key, deque())
                baseline_ms = self.sent_baseline_averages.get(key)
            else:
                source = "Unknown"
                buf = deque()
                baseline_ms = None

            if baseline_ms is None or len(buf) < 2:
                age_item_text = "N/A"
                exceeds_threshold = False
            else:
                intervals = [buf[i] - buf[i - 1] for i in range(1, len(buf))]
                partial = current_time - buf[-1]
                all_intervals = intervals + [partial]
                avg_int_sec = sum(all_intervals) / len(all_intervals)
                avg_interval_ms = int(avg_int_sec * 1000)

                threshold_ms = baseline_ms * (1 + self.threshold_percentage)
                exceeds_threshold = avg_interval_ms > threshold_ms
                age_item_text = f"{avg_interval_ms} ms"

            param_item = QTableWidgetItem(key)
            value_item = QTableWidgetItem(str(value))
            age_item = QTableWidgetItem(age_item_text)
            source_item = QTableWidgetItem(source)

            for item in (param_item, value_item, age_item, source_item):
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Remove the editable flag
        
            if exceeds_threshold:
                age_item.setForeground(QBrush(QColor('red')))
            else:
                age_item.setForeground(QBrush(QColor('darkgray')))
            # Style the first column
            if param_item:
                param_item.setBackground(QBrush(QColor(bg_color)))  # Dark mode = dark bg, Light mode = light bg
                param_item.setForeground(QBrush(QColor(text_color)))  # Dark mode = white text, Light mode = black text

            # Add items to table
            self.data_table.setItem(row, 0, param_item)
            self.data_table.setItem(row, 1, value_item)
            self.data_table.setItem(row, 2, age_item)
            self.data_table.setItem(row, 3, source_item)

            row += 1

         # Apply rounded corner styles to the corner cells
        self.round_table_corners()
        self.adjust_table_height()

    def adjust_table_height(self):
        """Dynamically set table height based on row count, but limit it relative to window size."""
        
        row_count = self.data_table.rowCount()
        row_height = self.data_table.verticalHeader().defaultSectionSize()
        header_height = self.data_table.horizontalHeader().height()

        # Calculate required height based on row count
        required_height = header_height + (row_height * row_count)

        # Get window height and set a max limit (e.g., 50% of window height)
        max_table_height = int(self.height() - 300)  # Adjust percentage as needed

        # Set the table height, ensuring it does not exceed max_table_height
        final_height = min(required_height, max_table_height)

        self.data_table.setFixedHeight(final_height)  # Strictly enforce height
        self.data_table.updateGeometry()
        
    def round_table_corners(self):
        if self.data_table.rowCount() == 0:
            return

        # Top-left corner
        top_left_item = self.data_table.item(0, 0)
        if top_left_item:
            self.data_table.item(0, 0).setData(Qt.UserRole, "border-radius: 15px; border-top-left-radius: 15px;")

        # Top-right corner
        top_right_item = self.data_table.item(0, self.data_table.columnCount() - 1)
        if top_right_item:
            self.data_table.item(0, self.data_table.columnCount() - 1).setData(Qt.UserRole, "border-top-right-radius: 15px;")

        # Bottom-left corner
        bottom_left_item = self.data_table.item(self.data_table.rowCount() - 1, 0)
        if bottom_left_item:
            self.data_table.item(self.data_table.rowCount() - 1, 0).setData(Qt.UserRole, "border-bottom-left-radius: 15px;")

        # Bottom-right corner
        bottom_right_item = self.data_table.item(self.data_table.rowCount() - 1, self.data_table.columnCount() - 1)
        if bottom_right_item:
            self.data_table.item(self.data_table.rowCount() - 1, self.data_table.columnCount() - 1).setData(Qt.UserRole, "border-bottom-right-radius: 15px;")

    def resizeEvent(self, event):
        """Resize table dynamically when the window size changes."""
        super().resizeEvent(event)
        self.adjust_table_height()  # Adjust table height dynamically
    # ----------------------------------------------------------------
    # Processing Outgoing Data
    # ----------------------------------------------------------------
    def process_outgoing_data(self):
        while len(self.outgoing_data) > 0:
            post_data = self.outgoing_data.pop(0)
            if not isinstance(post_data, dict):
                logging.error(f"Invalid data: {post_data}. Expected dict.")
                continue

            for param, val in post_data.items():
                if param is None or val is None:
                    logging.error(f"Invalid data entry: {param}={val}. Skipped.")
                    continue

                now_ts = time.time()
                buf = self.sent_attempt_times_buffer.setdefault(param, deque(maxlen=50))
                buf.append(now_ts)

                old_val = self.last_sent_values.get(param)
                if old_val == val:
                    logging.debug(f"No change in '{param}'; not sending to Arduino.")
                else:
                    if self.arduino and self.arduino.is_open:
                        try:
                            msg = f"{param}:{val}\n".encode('utf-8')
                            self.arduino.write(msg)
                            logging.info(f"Sent to Arduino: {param}={val}")
                            self.last_sent_values[param] = val
                            self.sent_data[param] = {'value': val, 'timestamp': now_ts}
                            self.data[param] = val
                        except serial.SerialException as e:
                            logging.error(f"Failed to send data: {e}")
                            self.handle_disconnect()
                            break
                    else:
                        logging.error("Arduino not connected. Cannot send.")

                new_baseline = self.calculate_baseline(buf, min_samples=20)
                if new_baseline:
                    self.sent_baseline_averages[param] = new_baseline

                self.update_table()

    def closeEvent(self, event):
        if self.is_server_running:
            self.stop_server()
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
            logging.info("Arduino closed on exit.")
        event.accept()


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------
if __name__ == '__main__':
    multiprocessing.freeze_support()

    manager = multiprocessing.Manager()

    # Manager dictionary for Arduino data
    arduino_data = manager.dict()

    # Manager list for data to send to Arduino
    outgoing_data = manager.list()

    qt_app = QApplication(sys.argv)
    main_window = ArduinoApp(arduino_data, outgoing_data)
    main_window.show()
    sys.exit(qt_app.exec_())