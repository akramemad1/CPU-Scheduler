# gui/gantt.py
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtCore import QRectF, Qt



import random
from PyQt5.QtGui import QPainter


class GanttChartWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.process_colors = {}
        self.current_time = 0
        self.block_width = 30
        self.block_height = 40

        self.setMinimumHeight(100)
        self.setRenderHint(QPainter.Antialiasing)

    def add_block(self, process_name, time_unit):
       

        if process_name not in self.process_colors:
            self.process_colors[process_name] = self._random_color()
            print(f"Added new color for {process_name}")  # Debug

        color = self.process_colors[process_name]
        x = time_unit * self.block_width

        # Draw block
        rect = QGraphicsRectItem(QRectF(x, 0, self.block_width, self.block_height))
        rect.setBrush(QBrush(color))
        rect.setPen(QPen(Qt.black))
        self.scene.addItem(rect)

        # Process label
        text = QGraphicsTextItem(process_name)
        text.setDefaultTextColor(Qt.black)
        text.setPos(x + 5, 5)
        self.scene.addItem(text)

        # Time unit label (below block)
        time_text = QGraphicsTextItem(str(time_unit))
        time_text.setDefaultTextColor(Qt.darkGray)
        time_text.setPos(x , self.block_height + 5)
        self.scene.addItem(time_text)

        self.current_time += 1
        self.setSceneRect(0, 0, (time_unit + 1) * self.block_width + 100, self.block_height + 30)

        self.viewport().update()  # Force immediate redraw



    def clear_chart(self):
        self.scene.clear()
        self.current_time = 0
        self.process_colors = {}

    def _random_color(self):
        return QColor(
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200)
        )
