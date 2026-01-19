import sys
import io
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, QBuffer
from sympy import sympify
from sympy.printing.latex import latex

from calculator.ui.drawWidget import DrawWidget


class CalculatorWidget(QWidget):

    def __init__(self, calculator, useLatex=True):
        super().__init__()
        self.calculator = calculator
        self.useLatex = useLatex

        self.setWindowTitle("Handwriting Calculator")
        self.setFixedSize(520, 420)

        self.initCanvas()
        self.initLabels()
        self.initButtons()

    # -------- canvas --------
    def initCanvas(self):
        self.canvas = DrawWidget(300, 300, self)
        self.canvas.move(10, 10)
        self.canvas.setOnDraw(self.onDraw)

    # -------- labels --------
    def initLabels(self):
        self.exprLabel = QLabel("Expression:", self)
        self.exprLabel.setGeometry(320, 30, 180, 80)
        self.exprLabel.setAlignment(Qt.AlignCenter)
        self.exprLabel.setWordWrap(True)
        self.exprLabel.setStyleSheet(
            "font-size: 16px; font-weight: bold; background: #f5f5f5; padding: 6px;"
        )

        self.ansLabel = QLabel("Result:", self)
        self.ansLabel.setGeometry(300, 140, 200, 120)
        self.ansLabel.setAlignment(Qt.AlignCenter)
        self.ansLabel.setWordWrap(True)
        self.ansLabel.setStyleSheet(
            "font-size: 18px; font-weight: bold; background: #f5f5f5; padding: 6px;"
        )

    # -------- buttons --------
    def initButtons(self):
        self.penBtn = QPushButton("Pen", self)
        self.penBtn.move(10, 360)
        self.penBtn.clicked.connect(self.canvas.setPenMode)

        self.eraseBtn = QPushButton("Eraser", self)
        self.eraseBtn.move(100, 360)
        self.eraseBtn.clicked.connect(self.canvas.setEraseMode)

        self.undoBtn = QPushButton("Undo", self)
        self.undoBtn.move(200, 360)
        self.undoBtn.clicked.connect(self.canvas.undo)

        self.clearBtn = QPushButton("Clear", self)
        self.clearBtn.move(300, 360)
        self.clearBtn.clicked.connect(self.clearCanvas)

        self.uploadBtn = QPushButton("Upload", self)
        self.uploadBtn.move(400, 360)
        self.uploadBtn.clicked.connect(self.uploadImage)

    # -------- clear --------
    def clearCanvas(self):
        self.canvas.clear()
        self.exprLabel.setText("Expression:")
        self.ansLabel.setText("Result:")

    # -------- draw callback --------
    def onDraw(self, qimage):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        qimage.save(buffer, "PNG")
        image_bytes = io.BytesIO(buffer.data())

        expr, ans = self.calculator.calculate(image_bytes)
        self.display(expr, ans)

    # -------- upload --------
    def uploadImage(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        if path:
            self.canvas.loadImage(path)
            expr, ans = self.calculator.calculate(path)
            self.display(expr, ans)

    # -------- display --------
    def display(self, expr, ans):
        try:
            expr = latex(sympify(expr, evaluate=False)) if self.useLatex else str(expr)
        except Exception:
            expr = str(expr)

        try:
            ans = latex(sympify(ans, evaluate=False)) if self.useLatex else str(ans)
        except Exception:
            ans = str(ans)

        self.exprLabel.setText(f"Expression:\n{expr}")
        self.ansLabel.setText(f"Result:\n{ans}")


class GUICalculatorApplication(QApplication):
    def __init__(self, calculator, useLatex=True):
        super().__init__(sys.argv)
        self.window = CalculatorWidget(calculator, useLatex)
        self.window.show()

    def run(self):
        self.exec_()
