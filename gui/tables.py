# gui/tables.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import  Qt

class ProcessTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Process Status")
        layout.addWidget(self.label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Arrival", "Burst", "Remaining"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def update_table(self, data):
        """Properly update table without duplicates"""
        # Create mapping of process names to rows
        existing_rows = {}
        for row in range(self.table.rowCount()):
            if item := self.table.item(row, 0):
                existing_rows[item.text()] = row

        # Update or add rows
        for proc in data:
            if proc['name'] in existing_rows:
                row = existing_rows[proc['name']]
            else:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
            self.table.setItem(row, 0, QTableWidgetItem(proc['name']))
            self.table.setItem(row, 1, QTableWidgetItem(str(proc['arrival'])))
            self.table.setItem(row, 2, QTableWidgetItem(str(proc['burst'])))
            self.table.setItem(row, 3, QTableWidgetItem(str(proc['remaining'])))

        # Remove finished processes
        current_processes = {p['name'] for p in data}
        for name, row in list(existing_rows.items()):
            if name not in current_processes:
                self.table.removeRow(row)

        self.table.resizeColumnsToContents()

class StatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Statistics")
        layout.addWidget(self.label)

        self.avg_wt_label = QLabel("Avg Waiting Time: -")
        self.avg_tat_label = QLabel("Avg Turnaround Time: -")

        layout.addWidget(self.avg_wt_label)
        layout.addWidget(self.avg_tat_label)

        self.setLayout(layout)

    def update_stats(self, avg_wt, avg_tat):
        self.avg_wt_label.setText(f"Average Waiting Time: {avg_wt:.2f}")
        self.avg_tat_label.setText(f"Average Turnaround Time: {avg_tat:.2f}")
