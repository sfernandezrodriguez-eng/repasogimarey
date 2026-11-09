from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QPushButton


class BotonBuscaminas(QPushButton):
    marcarSolicitado = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mina = False
        self.minasArredores = 0
        self.pulsado = False
        self.marcado = False
        # Mantiene todas las casillas iguales aunque cambie el texto o el color.
        self.setFixedSize(42, 42)
        self.setStyleSheet("background-color: white;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.marcarSolicitado.emit()
            event.accept()
            return
        super().mousePressEvent(event)

    def mostrar_contenido(self):
        if self.marcado:
            self.setText("⚑")
            self.setStyleSheet("background-color: white; color: red;")
        elif not self.pulsado:
            self.setText("")
            self.setStyleSheet("background-color: white;")
        elif self.mina:
            self.setText("*")
            self.setStyleSheet("background-color: black; color: white;")
        elif self.minasArredores == 0:
            self.setText("")
            self.setStyleSheet("background-color: lightgrey;")
        else:
            colores = {
                1: "lightgreen",
                2: "lightyellow",
                3: "orange",
                4: "salmon",
                5: "tomato",
                6: "red",
                7: "red",
                8: "red",
            }
            self.setText(str(self.minasArredores))
            self.setStyleSheet(
                f"background-color: {colores[self.minasArredores]}; color: black;"
            )
