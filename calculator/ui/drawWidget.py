from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QImage, QPen
from PyQt5.QtCore import Qt, QPoint


class DrawWidget(QWidget):
    def __init__(self, w=300, h=300, parent=None):
        super().__init__(parent)
        self.setFixedSize(w, h)

        self.image = QImage(w, h, QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.last_point = QPoint()
        self.drawing = False
        self._callback = None

        self.tool = "pen"
        self.pen_size = 4
        self.eraser_size = 20

        # History
        self.strokes = []
        self.current_stroke = []

    # -------- callback --------
    def setOnDraw(self, callback):
        self._callback = callback

    # -------- tools --------
    def setTool(self, tool):
        self.tool = tool

    # 🔥 BACKWARD COMPATIBILITY (FIX)
    def setPenMode(self):
        self.setTool("pen")

    def setEraseMode(self):
        self.setTool("eraser")

    # -------- load image --------
    def loadImage(self, path):
        img = QImage(path)
        if img.isNull():
            return
        img = img.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image.fill(Qt.white)
        painter = QPainter(self.image)
        painter.drawImage(0, 0, img)
        painter.end()
        self.strokes.clear()
        self.update()

    # -------- mouse events --------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.drawing = True
            self.current_stroke = [event.pos()]

    def mouseMoveEvent(self, event):
        if self.drawing and (event.buttons() & Qt.LeftButton):
            painter = QPainter(self.image)

            if self.tool == "eraser":
                pen = QPen(Qt.white, self.eraser_size, Qt.SolidLine, Qt.RoundCap)
            else:
                pen = QPen(Qt.black, self.pen_size, Qt.SolidLine, Qt.RoundCap)

            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()

            self.last_point = event.pos()
            self.current_stroke.append(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            if len(self.current_stroke) > 1:
                self.strokes.append(self.current_stroke)
            self.current_stroke = []

            if self._callback:
                self._callback(self.image)

    # -------- paint --------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    # -------- clear --------
    def clear(self):
        self.image.fill(Qt.white)
        self.strokes.clear()
        self.update()

    # -------- undo --------
    def undo(self):
        if not self.strokes:
            return

        self.strokes.pop()
        self.image.fill(Qt.white)
        painter = QPainter(self.image)

        for stroke in self.strokes:
            pen = QPen(Qt.black, self.pen_size, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            for i in range(1, len(stroke)):
                painter.drawLine(stroke[i - 1], stroke[i])

        painter.end()
        self.update()
