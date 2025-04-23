from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QCheckBox, QTableWidget, 
                            QTableWidgetItem, QSpinBox, QHeaderView, QMessageBox)
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QStackedLayout
from gui.controls import ControlsWidget
from gui.gantt import GanttChartWidget
from gui.tables import ProcessTableWidget, StatsWidget
from PyQt5 import QtCore, QtGui
from core.simulator import Simulator
from core.simulator_RR import SimulatorPreem  # Import the new SimulatorPreem
from core.simulator_pri import SimulatorPriority
from core.simulator_preem import SimulatorPreemitives
from core.schedulers.fcfs import FCFSScheduler
from core.schedulers.sjf import SJFScheduler
from core.schedulers.srtf import SRTFScheduler
from core.schedulers.priority_preem import priority_preem
from core.schedulers.priority_nonpreem import PriorityNonPreemptiveScheduler
from core.schedulers.round_robin import RRScheduler
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
import os

from PyQt5.QtGui import QMovie
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPU Scheduler")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowIcon(QIcon("icons/dinosaur-svgrepo-com.svg")) 
        

        self.controls = ControlsWidget()
        self.gantt_chart = GanttChartWidget()
        self.table_widget = ProcessTableWidget()
        self.stats_widget = StatsWidget()

        self.simulator = None
        self.simulation_started = False


        self.finish_sound = QSoundEffect()
        sound_path = os.path.join(os.path.dirname(__file__), "../mixkit-magic-marimba-2820.wav")
        self.finish_sound.setSource(QUrl.fromLocalFile(sound_path))
        self.finish_sound.setVolume(0.2)

        self.start_sound = QSoundEffect()
        sound_ppath = os.path.join(os.path.dirname(__file__), "../zzz.wav")
        self.start_sound.setSource(QUrl.fromLocalFile(sound_ppath))
        self.start_sound.setVolume(0.9)

        self.gif_label = QLabel(self)
        self.movie = QMovie("10-c3794c29-unscreenn.gif")  
        self.gif_label.setMovie(self.movie)
        self.gif_label.setFixedSize(500, 500)




       

        central_widget = QtWidgets.QWidget()


        
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.controls)



        # GIF label
        self.gif_label = QLabel()
        self.movie = QMovie("output-onlinegiftools.gif")
        self.gif_label.setMovie(self.movie)
        self.gif_label.hide()  # Hide it initially
        

     


        # Add the container to your layout
        layout.addWidget(self.gantt_chart)
        

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.table_widget)
        h_layout.addWidget(self.stats_widget)
        h_layout.addWidget(self.gif_label)

        
        layout.addLayout(h_layout)
        central_widget.setLayout(layout)

        self.controls.start_clicked.connect(self.start_simulation)
        self.controls.process_confirmed.connect(self.handle_confirmed_process)






    def start_simulation(self):
        try:
            
            processes = self.controls.get_processes()
            if not processes:
                # An error occurred during process retrieval, so don't start the simulation
                QMessageBox.warning(self, "Error", "Simulation cannot start due to invalid process input. Change the values in order to proceed")
                print("Simulation cannot start due to invalid process input.")
                return  # Or potentially disable the start button, etc.

            scheduler_type = self.controls.get_scheduler_type()
            if scheduler_type == "FCFS":
                scheduler = FCFSScheduler()
            elif scheduler_type == "SJF":
                scheduler = SJFScheduler()
            elif scheduler_type == "SRTF":
                scheduler = SRTFScheduler()
            elif scheduler_type == "Priority (preemptive)":
                scheduler = priority_preem()
            elif scheduler_type == "Priority (non-preemptive)":
                scheduler = PriorityNonPreemptiveScheduler()
            elif scheduler_type == "Round Robin":
                scheduler = RRScheduler()
            else:
                QMessageBox.warning(self, "Error", "Unsupported scheduler")
                return



            # Instantiate the chosen simulator
            if scheduler_type == "FCFS" or scheduler_type == "SJF" :
                self.simulator = Simulator(
                    scheduler=scheduler,
                    processes=processes,
                    time_unit=1,
                    live=self.controls.is_live_mode()
                )
            if scheduler_type == "SRTF" :
                self.simulator = SimulatorPreemitives(
                    scheduler=scheduler,
                    processes=processes,
                    time_unit=1,
                    live=self.controls.is_live_mode()
                )
            elif  scheduler_type == "Round Robin" :
                quan = self.controls.quantum_input.value() if hasattr(self.controls, "quantum_input") else 2
                self.simulator = SimulatorPreem(  # Use SimulatorPreem if selected
                    scheduler=scheduler,
                    processes=processes,
                    time_unit=1,
                    live=self.controls.is_live_mode(),
                    quantum=quan
                )
            elif scheduler_type == "Priority (preemptive)" or scheduler_type == "Priority (non-preemptive)" :
                self.simulator = SimulatorPriority(
                    scheduler=scheduler,
                    processes=processes,
                    time_unit=1,
                    live=self.controls.is_live_mode()
                )

            self.controls.set_simulator(self.simulator)
            self.controls.has_pending_process = False  


            self.simulator.update_gantt.connect(self.gantt_chart.add_block)
            self.simulator.update_table.connect(self.table_widget.update_table)
            self.simulator.update_stats.connect(self.stats_widget.update_stats)
            self.simulator.simulation_done.connect(self.simulation_complete)

            self.gantt_chart.clear_chart()
            self.table_widget.update_table([])
            self.stats_widget.update_stats(0, 0)

            self.simulation_started = True

            self.start_sound.play()
            self.gif_label.show()
            self.movie.start()

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
        self.controls.set_arrival_column_readonly(False)
        self.controls.has_pending_process = False  
 
        msg = QMessageBox(self)
        msg.setWindowTitle("Done")
        msg.setText("Simulation finished!")
        self.finish_sound.play()

        
        icon = QtGui.QPixmap("likedino.png")
        msg.setIconPixmap(icon.scaled(100, 100))  

        
        exit_button = msg.addButton("Exit Simulation", QMessageBox.RejectRole)
        restart_button = msg.addButton("Restart", QMessageBox.YesRole)
        back_button = msg.addButton("Close", QMessageBox.NoRole)

        msg.exec_()
        self.simulation_started = False

        if msg.clickedButton() == exit_button:
            QtWidgets.qApp.quit()

        elif msg.clickedButton() == restart_button:
            self.start_simulation()  

