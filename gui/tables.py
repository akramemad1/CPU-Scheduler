# gui/tables.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
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
        self.table.setFixedHeight(200)  # or any value that fits your layout
        self.table.setFixedWidth(450)
        
        self.table.setHorizontalHeaderLabels(["Name", "Arrival", "Burst", "Remaining"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def update_table(self, data):
        """Properly update table without duplicates and keep row order consistent"""

        # Sort processes by name to ensure consistent order
        data.sort(key=lambda p: p['arrival'])

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

            # Add items and make them read-only
            for col, key in enumerate(['name', 'arrival', 'burst', 'remaining']):
                item = QTableWidgetItem(str(proc[key]))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # Make cell read-only
                self.table.setItem(row, col, item)

        # Remove finished processes
        current_processes = {p['name'] for p in data}
        for name, row in sorted(existing_rows.items(), key=lambda x: -x[1]):
            if name not in current_processes:
                self.table.removeRow(row)

        

class StatsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Statistics")
        layout.addWidget(self.label)

        self.avg_wt_label = QLabel("Average Waiting Time: -")
        self.avg_tat_label = QLabel("Average Turnaround Time: -")

        layout.addWidget(self.avg_wt_label)
        layout.addWidget(self.avg_tat_label)


        self.setLayout(layout)

    def update_stats(self, avg_wt, avg_tat):
        self.avg_wt_label.setText(f"Average Waiting Time: {avg_wt:.2f}")
        self.avg_tat_label.setText(f"Average Turnaround Time: {avg_tat:.2f}")
