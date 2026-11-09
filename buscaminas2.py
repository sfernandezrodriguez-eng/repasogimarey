import random
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QSizePolicy,
    QWidget,
)

from botonBuscaminas import BotonBuscaminas


class FiestraPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.filas = 8
        self.columnas = 8
        self.numeroMinas = 10
        self.juegoTerminado = False
        self.casillasAbiertas = 0

        self.setWindowTitle("Buscaminas")
        self.setFixedSize(400, 400)

        self.botons, layout = self.crearBotonsGrid()
        self.minarCampo()
        self.contarMinas()
        self.actualizar_estado()

        contedor = QWidget()
        contedor.setLayout(layout)
        self.setCentralWidget(contedor)

    def crearBotonsGrid(self):
        layout = QGridLayout()
        layout.setSpacing(4)
        botons = []

        for fila in range(self.filas):
            fila_botons = []
            for columna in range(self.columnas):
                boton = BotonBuscaminas()
                boton.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Expanding,
                )
                boton.clicked.connect(
                    lambda checked=False, f=fila, c=columna: self.abrir_casilla(f, c)
                )
                boton.marcarSolicitado.connect(
                    lambda f=fila, c=columna: self.alternar_bandera(f, c)
                )
                fila_botons.append(boton)
                layout.addWidget(boton, fila, columna)
            botons.append(fila_botons)

        return botons, layout

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
            self.botons[fila][columna].mina = True

    def contarMinas(self):
        for fila in range(self.filas):
            for columna in range(self.columnas):
                boton = self.botons[fila][columna]
                if not boton.mina:
                    boton.minasArredores = sum(
                        self.botons[f][c].mina
                        for f, c in self.vecinos(fila, columna)
                    )

    def abrir_casilla(self, fila, columna):
        boton = self.botons[fila][columna]
        if self.juegoTerminado or boton.pulsado or boton.marcado:
            return

        # La primera jugada abre una zona vacía, sin minas ni números alrededor.
        if self.casillasAbiertas == 0:
            zona_inicial = {
                (f, c)
                for f in range(max(0, fila - 1), min(self.filas, fila + 2))
                for c in range(max(0, columna - 1), min(self.columnas, columna + 2))
            }
            minas_en_zona = [
                (f, c)
                for f, c in zona_inicial
                if self.botons[f][c].mina
            ]
            destinos = [
                (f, c)
                for f in range(self.filas)
                for c in range(self.columnas)
                if (f, c) not in zona_inicial and not self.botons[f][c].mina
            ]
            random.shuffle(destinos)
            for (f_mina, c_mina), (f_destino, c_destino) in zip(
                minas_en_zona, destinos
            ):
                self.botons[f_mina][c_mina].mina = False
                self.botons[f_destino][c_destino].mina = True
            self.contarMinas()

        if boton.mina:
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
            boton = self.botons[f][c]
            if boton.pulsado or boton.marcado or boton.mina:
                continue

            boton.pulsado = True
            boton.mostrar_contenido()
            self.casillasAbiertas += 1

            if boton.minasArredores == 0:
                pendientes.extend(self.vecinos(f, c))

    def alternar_bandera(self, fila, columna):
        boton = self.botons[fila][columna]
        if self.juegoTerminado or boton.pulsado:
            return
        boton.marcado = not boton.marcado
        boton.mostrar_contenido()
        self.actualizar_estado()

    def finalizar_partida(self, ganada):
        self.juegoTerminado = True
        if ganada:
            for fila in self.botons:
                for boton in fila:
                    if boton.mina:
                        boton.marcado = True
                        boton.mostrar_contenido()
            self.statusBar().showMessage("¡Ganaste! Has encontrado todas las casillas seguras.")
        else:
            for fila in self.botons:
                for boton in fila:
                    if boton.mina:
                        boton.pulsado = True
                        boton.marcado = False
                        boton.mostrar_contenido()
            self.statusBar().showMessage("¡Has perdido! Has encontrado una mina.")

    def actualizar_estado(self):
        banderas = sum(
            boton.marcado for fila in self.botons for boton in fila
        )
        self.statusBar().showMessage(
            f"Minas restantes: {self.numeroMinas - banderas}"
        )


if __name__ == "__main__":
    aplicacion = QApplication(sys.argv)
    fiestra = FiestraPrincipal()
    fiestra.show()
    sys.exit(aplicacion.exec())
