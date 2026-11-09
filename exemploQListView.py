import sys

from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QListView,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ModeloTarefas import ModeloTarefas


class JanelaTarefas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exemplo QListView")
        self.resize(180, 210)

        self.modelo = ModeloTarefas(
            [
                "Ir o centro DC",
                "Ir o ximnasio",
                "Ir a compra",
                "Outra",
            ],
            self,
        )
        self.lista_tarefas = QListView()
        self.lista_tarefas.setModel(self.modelo)
        self.lista_tarefas.setSelectionMode(
            QListView.SelectionMode.MultiSelection
        )

        botao_borrar = QPushButton("Borrar")
        botao_borrar.clicked.connect(self.borrar_tarefas_selecionadas)
        botao_feito = QPushButton("Feito")
        botao_feito.clicked.connect(self.marcar_tarefas_selecionadas)

        layout_botoes = QHBoxLayout()
        layout_botoes.addWidget(botao_borrar)
        layout_botoes.addWidget(botao_feito)

        self.entrada_tarefa = QLineEdit()
        botao_adicionar = QPushButton("Engadir tarefa")
        botao_adicionar.clicked.connect(self.adicionar_tarefa)
        self.entrada_tarefa.returnPressed.connect(self.adicionar_tarefa)

        layout_vertical = QVBoxLayout()
        layout_vertical.addWidget(self.lista_tarefas)
        layout_vertical.addLayout(layout_botoes)
        layout_vertical.addWidget(self.entrada_tarefa)
        layout_vertical.addWidget(botao_adicionar)

        conteudo = QWidget()
        conteudo.setLayout(layout_vertical)
        self.setCentralWidget(conteudo)

    def borrar_tarefas_selecionadas(self):
        filas = [
            indice.row()
            for indice in self.lista_tarefas.selectionModel().selectedIndexes()
        ]
        self.modelo.remover_tarefas(filas)

    def marcar_tarefas_selecionadas(self):
        filas = [
            indice.row()
            for indice in self.lista_tarefas.selectionModel().selectedIndexes()
        ]
        self.modelo.marcar_como_feitas(filas)

    def adicionar_tarefa(self):
        tarefa = self.entrada_tarefa.text().strip()
        if not tarefa:
            return
        self.modelo.adicionar_tarefa(tarefa)
        self.entrada_tarefa.clear()


def main():
    app = QApplication(sys.argv)
    janela = JanelaTarefas()
    janela.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
