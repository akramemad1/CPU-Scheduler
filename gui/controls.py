from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QCheckBox, QTableWidget, 
                            QTableWidgetItem, QSpinBox, QHeaderView, QMessageBox)
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QMovie
import math
class ControlsWidget(QWidget):
    start_clicked = pyqtSignal()
    process_confirmed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.simulator = None  # ← placeholder

    def init_ui(self):
        main_layout = QHBoxLayout()
        controls_layout = QVBoxLayout()
        

        # Scheduler dropdown
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Scheduler Type:"))
        self.scheduler_box = QComboBox()
        self.scheduler_box.addItems(["FCFS", "SJF", "SRTF", "Priority (preemptive)", "Priority (non-preemptive)", "Round Robin"])
        self.scheduler_box.currentIndexChanged.connect(self.update_scheduler_fields)
        hlayout.addWidget(self.scheduler_box)

        # Live simulation checkbox
        self.live_checkbox = QCheckBox("Live Simulation (1 sec/unit)")
        self.live_checkbox.setChecked(True)
        self.live_checkbox.stateChanged.connect(self.toggle_live_mode)
        hlayout.addWidget(self.live_checkbox)
        controls_layout.addLayout(hlayout)






        # Process table
        controls_layout.addWidget(QLabel("Processes:"))
        self.process_table = QTableWidget(3, 3)
        self.process_table.setHorizontalHeaderLabels(["Name", "Arrival", "Burst"])
        self.process_table.setMinimumHeight(150)  # or any value that fits your layout
        self.process_table.setMinimumWidth(100)
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setup_table_validation()
        controls_layout.addWidget(self.process_table)

        # Process row buttons
        self.process_box = QHBoxLayout()
        self.add_row_button = QPushButton("Add Process")
        self.add_row_button.setIcon(QIcon("icons/leaves-3-svgrepo-com.svg"))
        self.add_row_button.setIconSize(QSize(24, 24))
        self.add_row_button.clicked.connect(self.add_process_row)
        self.process_box.addWidget(self.add_row_button)
        self.remove_row_button = QPushButton("Remove Process")
        self.remove_row_button.setIcon(QIcon("icons/tree-2-svgrepo-com.svg"))
        self.remove_row_button.setIconSize(QSize(24, 24))
        self.remove_row_button.clicked.connect(self.remove_process_row)
        self.process_box.addWidget(self.remove_row_button)
        self.confirm_add_button = QPushButton("Confirm Add")
        self.confirm_add_button.setIcon(QIcon("icons/bird-svgrepo-com.svg"))
        self.confirm_add_button.setIconSize(QSize(24, 24))
        self.confirm_add_button.clicked.connect(self.confirm_add_process)
        self.process_box.addWidget(self.confirm_add_button)
        controls_layout.addLayout(self.process_box)

        self.dynamic_layout = QVBoxLayout()
        controls_layout.addLayout(self.dynamic_layout)

        self.start_button = QPushButton("Start Simulation")
        self.start_button.setIcon(QIcon("icons/leaves-2-svgrepo-com.svg"))
        self.start_button.setIconSize(QSize(24, 24))
        self.start_button.clicked.connect(self.start_clicked.emit)
        controls_layout.addWidget(self.start_button)

        main_layout.addLayout(controls_layout)

        





        # Optional image section
        image_label = QLabel()
        pixmap = QtGui.QPixmap("dino2.png")
        image_label.setPixmap(pixmap.scaledToWidth(300, QtCore.Qt.SmoothTransformation))
        image_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(image_label)

        self.setLayout(main_layout)
        self.update_scheduler_fields()


    def set_simulator(self, simulator):
        self.simulator = simulator

    def toggle_live_mode(self, state):
        self.add_row_button.setVisible(state == Qt.Checked)



    def update_scheduler_fields(self):
        for i in reversed(range(self.dynamic_layout.count())):
            widget = self.dynamic_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        scheduler_type = self.get_scheduler_type()

        if scheduler_type == "Round Robin":
            self.quantum_label = QLabel("Quantum:")
            self.quantum_input = QSpinBox()
            self.quantum_input.setFixedWidth(80)
            self.quantum_input.setRange(1, 100)
            self.dynamic_layout.addWidget(self.quantum_label)
            self.dynamic_layout.addWidget(self.quantum_input)
            self.process_table.setColumnCount(3)
            self.process_table.setHorizontalHeaderLabels(["Name", "Arrival", "Burst"])

        elif "Priority" in scheduler_type:
            self.process_table.setColumnCount(4)
            self.process_table.setHorizontalHeaderLabels(["Name", "Arrival", "Burst", "Priority"])

        else:
            self.process_table.setColumnCount(3)
            self.process_table.setHorizontalHeaderLabels(["Name", "Arrival", "Burst"])

    def _get_item_text(self, row, col):
        item = self.process_table.item(row, col)
        return item.text().strip() if item else "0"

    def get_scheduler_type(self):
        return self.scheduler_box.currentText()

    def is_live_mode(self):
        return self.live_checkbox.isChecked()

    def get_processes(self):
        processes = []
        has_error = False  # Flag to track if any error occurred
        seen_names = set()

        for row in range(self.process_table.rowCount()):
            try:
                name = self._get_item_text(row, 0)
                if not name:
                    continue


                if name in seen_names:
                    QMessageBox.warning(self, "Duplicate Process Name", f"Process name '{name}' is duplicated! Please use unique names.")
                    has_error = True
                    continue
                seen_names.add(name)
                arrival = int(self._get_item_text(row, 1))
                burst = int(self._get_item_text(row, 2))
                if burst < 0:
                    QMessageBox.warning(self, "Invalid Input", f"Burst time cannot be negative for process '{name}'!")
                    has_error = True
                    continue  # Skip this process
                if burst == 0:
                    QMessageBox.warning(self, "Invalid Input", f"Burst time cannot be Zero for process '{name}'!")
                    has_error = True
                    continue  # Skip this process

                process = {'name': name, 'arrival': arrival, 'burst': burst}
                scheduler_type = self.get_scheduler_type()
                if "Priority" in scheduler_type:
                    priority = int(self._get_item_text(row, 3) or 0)
                    if priority < 0:
                        QMessageBox.warning(self, "Invalid Input", f"Priority cannot be negative for process '{name}'!")
                        has_error = True
                        continue  # Skip this process
                    process['priority'] = priority
                elif scheduler_type == "Round Robin":
                    quantum = int(self._get_item_text(row, 3) or 1)
                    process['quantum'] = quantum
                processes.append(process)
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", f"Invalid number format in process table (row {row + 1})!")
                has_error = True
                continue  # Skip this process
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred while reading process data (row {row + 1}): {e}")
                has_error = True
                continue  # Skip this process

        if has_error:
            return []  # Return an empty list if any error occurred
        else:
            return processes

    def confirm_add_process(self):
        try:
            last_row = self.process_table.rowCount() - 1
            if last_row < 0:
                raise ValueError("No process to add")
            process = self._get_validated_process(last_row)
            process['arrival'] = self.simulator.current_time + 1
            self.process_confirmed.emit(process)
            
        except ValueError as e:
            self._show_error(str(e))

    def _get_validated_process(self, row):
        name = self._get_item_text(row, 0)
        if not name:
            raise ValueError("Process name cannot be empty")
        burst = int(self._get_item_text(row, 2))
        process = {'name': name,  'burst': burst}
        scheduler_type = self.get_scheduler_type()
        if "Priority" in scheduler_type:
            process['priority'] = int(self._get_item_text(row, 3))
        elif scheduler_type == "Round Robin":
            process['quantum'] = int(self._get_item_text(row, 3))
        return process

    def _clear_row(self, row):
        for col in range(self.process_table.columnCount()):
            self.process_table.setItem(row, col, QTableWidgetItem(""))

    def _show_error(self, message):
        QMessageBox.warning(self, "Error", message)

    def add_process_row(self):
        row = self.process_table.rowCount()
        self.process_table.insertRow(row)
        for col in range(self.process_table.columnCount()):
            item = QTableWidgetItem("0" if col > 0 else "")
            self.process_table.setItem(row, col, item)

    def remove_process_row(self):
        row = self.process_table.currentRow()
        if row >= 0:
            self.process_table.removeRow(row)

    def setup_table_validation(self):
        for row in range(self.process_table.rowCount()):
            for col in [1, 2]:
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                item.setData(Qt.DisplayRole, "0")
                self.process_table.setItem(row, col, item)