import sys
from PyQt6.QtCore import Qt, QAbstractListModel, QModelIndex
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QVBoxLayout, QPushButton, QWidget,
    QLineEdit, QHBoxLayout, QListView
)


# El modelo guarda cada tarea como una pareja: (hecha, texto).
# QListView le pregunta al modelo qué filas hay y qué texto debe mostrar.
class ModeloTarefas(QAbstractListModel):
    def __init__(self, tarefas=None):
        super().__init__()
        self.tarefas = tarefas or []

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        # Si la vista pide una posición que no existe, no hay nada que mostrar.
        if not index.isValid():
            return None

        # DisplayRole es el dato visible. Añadimos una marca según el estado.
        if role == Qt.ItemDataRole.DisplayRole:
            estado, texto = self.tarefas[index.row()]
            marca = "[✓] " if estado else "[ ] "
            return f"{marca}{texto}"

        return None

    def rowCount(self, parent=QModelIndex()):
        # La cantidad de filas de la lista es la cantidad de tareas guardadas.
        return len(self.tarefas)

    def engadir_tarefa(self, texto):
        # No se permiten tareas vacías o formadas solo por espacios.
        if not texto.strip():
            return

        # Avisamos a Qt antes y después de cambiar la lista para que la vista
        # actualice correctamente la fila nueva.
        posicion = len(self.tarefas)
        self.beginInsertRows(QModelIndex(), posicion, posicion)
        self.tarefas.append((False, texto))
        self.endInsertRows()

    def borrar_tarefas(self, posicions):
        # Borramos de la última posición a la primera: así los índices que faltan
        # por borrar no cambian cuando se elimina una tarea anterior.
        for pos in sorted(posicions, reverse=True):
            self.beginRemoveRows(QModelIndex(), pos, pos)
            del self.tarefas[pos]
            self.endRemoveRows()

    def marcar_como_feito(self, posicions):
        for pos in posicions:
            # Conservamos el texto y cambiamos el estado a "hecha".
            _, texto = self.tarefas[pos]
            self.tarefas[pos] = (True, texto)

            # Avisamos a la vista para que vuelva a dibujar esta tarea con su marca.
            idx = self.index(pos)
            self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole])


# Ventana principal: crea los controles y conecta sus botones con las acciones.
class FiestraPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Exemplo QListView")

        # Fijamos el ancho y permitimos que la ventana crezca en altura.
        self.setMinimumSize(400, 400)
        self.setMaximumSize(400, 600)

        # Las tareas iniciales: True significa hecha y False, pendiente.
        self.listaTarefas = [
            (True, "Ir o centro DC"),
            (False, "Ir o ximnasio"),
            (False, "Ir a compra"),
            (False, "Outra")
        ]

        self.modelo = ModeloTarefas(self.listaTarefas)

        # El diseño vertical coloca la lista, los botones y la entrada uno debajo de otro.
        caixaV = QVBoxLayout()

        self.lstTarefas = QListView()
        self.lstTarefas.setModel(self.modelo)
        # Permite seleccionar varias tareas a la vez.
        self.lstTarefas.setSelectionMode(QListView.SelectionMode.MultiSelection)
        caixaV.addWidget(self.lstTarefas)

        # Los botones Borrar y Feito se colocan en una fila horizontal.
        caixaBotons = QHBoxLayout()
        btnBorrar = QPushButton("Borrar")
        btnBorrar.clicked.connect(self.on_btnBorrar_clicked)
        btnFeito = QPushButton("Feito")
        btnFeito.clicked.connect(self.on_btnFeito_clicked)

        caixaBotons.addWidget(btnBorrar)
        caixaBotons.addWidget(btnFeito)

        caixaV.addLayout(caixaBotons)

        # Caja donde se escribe una tarea nueva.
        self.txtTarefa = QLineEdit()
        caixaV.addWidget(self.txtTarefa)

        # Al pulsar este botón, el texto de la caja se añade a la lista.
        btnEngadir = QPushButton("Engadir Tarefa")
        btnEngadir.clicked.connect(self.on_btnEngadir_clicked)
        caixaV.addWidget(btnEngadir)

        # Qt necesita un widget contenedor para mostrar el diseño en la ventana.
        contenedor = QWidget()
        contenedor.setLayout(caixaV)
        self.setCentralWidget(contenedor)

    def on_btnBorrar_clicked(self):
        # selectedIndexes() encuentra las tareas seleccionadas en la lista.
        indices_seleccionados = self.lstTarefas.selectedIndexes()
        filas_seleccionadas = [indice.row() for indice in indices_seleccionados]
        if filas_seleccionadas:
            self.modelo.borrar_tarefas(filas_seleccionadas)

    def on_btnFeito_clicked(self):
        # Enviamos al modelo las filas seleccionadas para marcarlas como hechas.
        indices = [index.row() for index in self.lstTarefas.selectedIndexes()]
        if indices:
            self.modelo.marcar_como_feito(indices)

    def on_btnEngadir_clicked(self):
        # Añadimos el texto escrito y vaciamos la caja para poder seguir escribiendo.
        txt = self.txtTarefa.text()
        if txt:
            self.modelo.engadir_tarefa(txt)
            self.txtTarefa.clear()


if __name__ == '__main__':
    # Este bloque se ejecuta al abrir este archivo directamente.
    aplicacion = QApplication(sys.argv)
    fiestra = FiestraPrincipal()
    fiestra.show()
    sys.exit(aplicacion.exec())