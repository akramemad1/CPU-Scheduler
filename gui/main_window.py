from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QCheckBox, QTableWidget, 
                            QTableWidgetItem, QSpinBox, QHeaderView, QMessageBox)
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from gui.controls import ControlsWidget
from gui.gantt import GanttChartWidget
from gui.tables import ProcessTableWidget, StatsWidget
from PyQt5 import QtCore, QtGui
from core.simulator import Simulator
from core.schedulers.fcfs import FCFSScheduler
from core.schedulers.sjf import SJFScheduler
from core.schedulers.srtf import SRTFScheduler
#from core.schedulers.round_robin import RoundRobinScheduler
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Scheduler")
        self.setGeometry(100, 100, 900, 600)

        self.controls = ControlsWidget()
        self.gantt_chart = GanttChartWidget()
        self.table_widget = ProcessTableWidget()
        self.stats_widget = StatsWidget()

        self.simulator = None
        self.simulation_started = False

        central_widget = QtWidgets.QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.controls)
        layout.addWidget(self.gantt_chart)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.table_widget)
        h_layout.addWidget(self.stats_widget)
        layout.addLayout(h_layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.controls.start_clicked.connect(self.start_simulation)
        self.controls.process_confirmed.connect(self.handle_confirmed_process)

    def start_simulation(self):
        try:
            processes = self.controls.get_processes()
            if not processes:
                QMessageBox.warning(self, "Error", "Add at least one process")
                return

            scheduler_type = self.controls.get_scheduler_type()
            if scheduler_type == "FCFS":
                scheduler = FCFSScheduler()
            elif scheduler_type == "SJF":
                scheduler = SJFScheduler()
            elif scheduler_type == "SRTF":
                scheduler = SRTFScheduler()



                
            #elif scheduler_type == "Round Robin":
               # quantum = self.controls.quantum_input.value() if hasattr(self.controls, "quantum_input") else 2
               # scheduler = RoundRobinScheduler(quantum)
            else:
                QMessageBox.warning(self, "Error", "Unsupported scheduler")
                return

            if self.simulator and self.simulator.isRunning():
                self.simulator.stop()
                self.simulator.wait()

            self.simulator = Simulator(
                scheduler=scheduler,
                processes=processes,
                time_unit=1,
                live=self.controls.is_live_mode()
            )

            self.simulator.update_gantt.connect(self.gantt_chart.add_block)
            self.simulator.update_table.connect(self.table_widget.update_table)
            self.simulator.update_stats.connect(self.stats_widget.update_stats)
            self.simulator.simulation_done.connect(self.simulation_complete)

            self.gantt_chart.clear_chart()
            self.table_widget.update_table([])
            self.stats_widget.update_stats(0, 0)

            self.simulation_started = True
            self.simulator.start()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def handle_confirmed_process(self, process):
        if not self.simulation_started or not self.simulator or not self.simulator.isRunning():
            QMessageBox.warning(self, "Error", "Simulation not running")
            return

        try:
            if self.simulator.add_process(process):
                QMessageBox.information(self, "Success", f"Process {process['name']} added successfully!")
            else:
                QMessageBox.warning(self, "Error", "Process already exists")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def simulation_complete(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Done")
        msg.setText("Simulation finished!")

        # Set a custom icon (QPixmap)
        icon = QtGui.QPixmap("likedino.png")
        msg.setIconPixmap(icon.scaled(100, 100))  # You can scale it to your desired size

        msg.exec_()
        self.simulation_started = False