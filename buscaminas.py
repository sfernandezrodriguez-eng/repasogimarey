import random
import sys

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QPushButton,
    QWidget,
)


class FiestraPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.filas = 8
        self.columnas = 8
        self.numeroMinas = 10
        self.juegoTerminado = False
        self.casillasAbiertas = 0

        self.setWindowTitle("Buscaminas")
        self.setFixedSize(400, 430)

        # Cada tipo de dato del juego se guarda en una matriz:
        # - campoDeMinas: -1 es una mina; 0-8 es el número de minas vecinas.
        # - pulsados: indica qué casillas ya se han abierto.
        # - bandeiras: indica qué casillas tienen una bandera.
        self.botons, layout = self.crearBotonsGrid()
        self.campoDeMinas = [
            [0 for _ in range(self.columnas)] for _ in range(self.filas)
        ]
        self.pulsados = [
            [False for _ in range(self.columnas)] for _ in range(self.filas)
        ]
        self.bandeiras = [
            [False for _ in range(self.columnas)] for _ in range(self.filas)
        ]

        self.minarCampo()
        self.contarMinas()

        contedor = QWidget()
        contedor.setLayout(layout)
        self.setCentralWidget(contedor)
        self.actualizar_estado()

    def crearBotonsGrid(self):
        layout = QGridLayout()
        layout.setSpacing(4)
        botons = []

        for fila in range(self.filas):
            fila_botons = []
            for columna in range(self.columnas):
                boton = QPushButton()
                boton.setFixedSize(42, 42)
                boton.clicked.connect(
                    lambda checked=False, f=fila, c=columna: self.abrir_casilla(f, c)
                )
                boton.setProperty("fila", fila)
                boton.setProperty("columna", columna)
                boton.installEventFilter(self)
                fila_botons.append(boton)
                layout.addWidget(boton, fila, columna)
            botons.append(fila_botons)

        return botons, layout

    def eventFilter(self, objeto, evento):
        if (
            evento.type() == QEvent.Type.MouseButtonPress
            and evento.button() == Qt.MouseButton.RightButton
            and isinstance(objeto, QPushButton)
        ):
            fila = objeto.property("fila")
            columna = objeto.property("columna")
            self.alternar_bandera(fila, columna)
            return True
        return super().eventFilter(objeto, evento)

    def vecinos(self, fila, columna):
        for f in range(max(0, fila - 1), min(self.filas, fila + 2)):
            for c in range(max(0, columna - 1), min(self.columnas, columna + 2)):
                if (f, c) != (fila, columna):
                    yield f, c

    def minarCampo(self):
        posiciones = random.sample(
            range(self.filas * self.columnas), self.numeroMinas
        )
        for posicion in posiciones:
            fila, columna = divmod(posicion, self.columnas)
            self.campoDeMinas[fila][columna] = -1

    def contarMinas(self):
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.campoDeMinas[fila][columna] != -1:
                    self.campoDeMinas[fila][columna] = sum(
                        self.campoDeMinas[f][c] == -1
                        for f, c in self.vecinos(fila, columna)
                    )

    def preparar_primer_clic(self, fila, columna):
        # La primera casilla y sus vecinas quedan libres de minas.
        zona_segura = {
            (f, c)
            for f in range(max(0, fila - 1), min(self.filas, fila + 2))
            for c in range(max(0, columna - 1), min(self.columnas, columna + 2))
        }
        minas_en_zona = [
            (f, c)
            for f, c in zona_segura
            if self.campoDeMinas[f][c] == -1
        ]
        destinos = [
            (f, c)
            for f in range(self.filas)
            for c in range(self.columnas)
            if (f, c) not in zona_segura and self.campoDeMinas[f][c] != -1
        ]
        random.shuffle(destinos)

        for (f_mina, c_mina), (f_destino, c_destino) in zip(
            minas_en_zona, destinos
        ):
            self.campoDeMinas[f_mina][c_mina] = 0
            self.campoDeMinas[f_destino][c_destino] = -1

        self.contarMinas()

    def abrir_casilla(self, fila, columna):
        if (
            self.juegoTerminado
            or self.pulsados[fila][columna]
            or self.bandeiras[fila][columna]
        ):
            return

        if self.casillasAbiertas == 0:
            self.preparar_primer_clic(fila, columna)

        if self.campoDeMinas[fila][columna] == -1:
            self.finalizar_partida(ganada=False)
            return

        self.abrir_zona_segura(fila, columna)
        if self.casillasAbiertas == self.filas * self.columnas - self.numeroMinas:
            self.finalizar_partida(ganada=True)
        else:
            self.actualizar_estado()

    def abrir_zona_segura(self, fila, columna):
        pendientes = [(fila, columna)]
        while pendientes:
            f, c = pendientes.pop()
            if (
                self.pulsados[f][c]
                or self.bandeiras[f][c]
                or self.campoDeMinas[f][c] == -1
            ):
                continue

            self.pulsados[f][c] = True
            self.casillasAbiertas += 1
            self.actualizar_aspecto_boton(f, c)

            if self.campoDeMinas[f][c] == 0:
                pendientes.extend(self.vecinos(f, c))

    def alternar_bandera(self, fila, columna):
        if self.juegoTerminado or self.pulsados[fila][columna]:
            return
        self.bandeiras[fila][columna] = not self.bandeiras[fila][columna]
        self.actualizar_aspecto_boton(fila, columna)
        self.actualizar_estado()

    def actualizar_aspecto_boton(self, fila, columna):
        boton = self.botons[fila][columna]
        valor = self.campoDeMinas[fila][columna]

        if self.bandeiras[fila][columna]:
            boton.setText("P")
            boton.setStyleSheet("background-color: white; color: red;")
        elif not self.pulsados[fila][columna]:
            boton.setText("")
            boton.setStyleSheet("background-color: white;")
        elif valor == -1:
            boton.setText("*")
            boton.setStyleSheet("background-color: black; color: white;")
        elif valor == 0:
            boton.setText("")
            boton.setStyleSheet("background-color: lightgrey;")
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
            boton.setText(str(valor))
            boton.setStyleSheet(
                f"background-color: {colores[valor]}; color: black;"
            )

    def finalizar_partida(self, ganada):
        self.juegoTerminado = True
        for fila in range(self.filas):
            for columna in range(self.columnas):
                if self.campoDeMinas[fila][columna] == -1:
                    if ganada:
                        self.bandeiras[fila][columna] = True
                    else:
                        self.pulsados[fila][columna] = True
                        self.bandeiras[fila][columna] = False
                    self.actualizar_aspecto_boton(fila, columna)

        if ganada:
            mensaje = "¡Ganaste! Has encontrado todas las casillas seguras."
        else:
            mensaje = "¡Has perdido! Has encontrado una mina."
        self.statusBar().showMessage(mensaje)

    def actualizar_estado(self):
        banderas = sum(sum(fila) for fila in self.bandeiras)
        self.statusBar().showMessage(
            f"Minas restantes: {self.numeroMinas - banderas}"
        )


if __name__ == "__main__":
    aplicacion = QApplication(sys.argv)
    fiestra = FiestraPrincipal()
    fiestra.show()
    sys.exit(aplicacion.exec())
