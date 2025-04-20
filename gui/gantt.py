from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsTextItem, QGraphicsPathItem, QGraphicsRectItem
)
from PyQt5.QtGui import (
    QColor, QBrush, QPen, QPainter, QPainterPath, QLinearGradient, QFont
)
from PyQt5.QtCore import QRectF, Qt
import random
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl
import os


class GanttChartWidget(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.process_colors = {}
        self.current_time = 0
        self.block_width = 55
        self.block_height = 65
        self.sound = QSoundEffect()
        sound_path = os.path.join(os.path.dirname(__file__), "../mixkit-hard-pop-click-2364.wav")
        self.sound.setSource(QUrl.fromLocalFile(sound_path))
        self.sound.setVolume(0.2)  # Volume between 0.0 and 1.0

        self.setMinimumHeight(120)
        self.setRenderHint(QPainter.Antialiasing)

        # Zoom
        self._zoom = 1.0

    def add_block(self, process_name, time_unit):
        if process_name not in self.process_colors:
            self.process_colors[process_name] = self._random_color()

        color = self.process_colors[process_name]
        x = time_unit * self.block_width

        # Rounded block with gradient fill
        rect = QRectF(x, 0, self.block_width, self.block_height)
        path = QPainterPath()
        path.addRoundedRect(rect, 18, 18)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(110))

        rounded_rect = QGraphicsPathItem(path)
        rounded_rect.setBrush(QBrush(gradient))
        rounded_rect.setPen(QPen(Qt.transparent))
        rounded_rect.setToolTip(f"Process: {process_name}\nTime: {time_unit}")
        self.scene.addItem(rounded_rect)

        # Adaptive text color (based on background)
        text_color = Qt.white if color.lightness() < 128 else Qt.black

        # Process label (inside block)
        text = QGraphicsTextItem(process_name)
        text.setDefaultTextColor(text_color)
        text.setFont(QFont("Poppins", 20))
        text.setPos(x + 8, 8)
        text.setZValue(1)
        self.scene.addItem(text)

        # Time label (below block)
        time_text = QGraphicsTextItem(str(time_unit))
        time_text.setDefaultTextColor(Qt.white)
        time_text.setFont(QFont("Segoe UI", 15))
        time_text.setPos(x , self.block_height + 5)
        self.scene.addItem(time_text)
        self.sound.play()

        # Grid line
        line = self.scene.addLine(x, 0, x, self.block_height + 30, QPen(Qt.lightGray, 0.5))
        line.setZValue(-1)

        self.current_time += 1
        self.setSceneRect(0, 0, (time_unit + 2) * self.block_width, self.block_height + 40)

        # Auto scroll to latest block
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().maximum())
        

    def clear_chart(self):
        self.scene.clear()
        self.current_time = 0
        self.process_colors = {}

    def _random_color(self):
        return QColor(
            random.randint(70, 200),
            random.randint(70, 200),
            random.randint(70, 200)
        )

