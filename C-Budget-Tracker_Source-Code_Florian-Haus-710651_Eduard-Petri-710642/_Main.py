from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)
from PySide6.QtGui import QIcon
from Features.Suchleiste.view import SuchleisteView
from Features.Übersicht.view import UebersichtView
from Features.Kategorien_Budget_Editor.view import CategoryEditDialog
from Features.Transaktionen_bearbeiten.view import TransactionDialog
from Features.Diagramm_Ausgabe.view import DiagrammView
from PySide6.QtCore import Qt
from Core.database import DatabaseManager
from Features.Budget_insgesamt.view import BudgetDiagrammView
from Features.Budget_Kategorie.view import BudgetBarChartView


class MainPage(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()

        self.setWindowTitle("Finanzplaner")

        self.setMinimumSize(1500, 800)

        # Die Referenzen für die Ansicht und den Controller
        self.db_manager = db_manager
        self.uebersicht_view = UebersichtView(self.db_manager)

        icon_path = "Resources/Logo-_Sparkassen-App_–_die_mobile_Filiale.ico"
        self.setWindowIcon(QIcon(icon_path))
        # Hauptlayout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Linkes Layout mit Diagrammen und Features
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # Horizontales Layout für die beiden Diagramme oben
        top_layout = QHBoxLayout()

        # Diagramme nebeneinander oben
        self.kreisdiagramm_view = DiagrammView(self.db_manager)  # Erstes Kreisdiagramm
        self.budgetdiagramm_view = BudgetDiagrammView(
            self.db_manager
        )  # Zweites Kreisdiagramm

        # Beide Diagramme erhalten denselben Platz
        top_layout.addWidget(self.kreisdiagramm_view, stretch=2)
        top_layout.addWidget(self.budgetdiagramm_view, stretch=2)

        # Container für das horizontale Layout
        top_widget = QWidget()
        top_widget.setLayout(top_layout)

        left_layout.addWidget(top_widget)  # Container mit beiden Diagrammen

        # Das dritte Diagramm darunter
        self.budget_chart_view = BudgetBarChartView(
            self.db_manager
        )  # Instanziiere das Säulendiagramm
        left_layout.addWidget(self.budget_chart_view)  # Füge das Säulendiagramm hinzu

        # Übersicht
        self.uebersicht = UebersichtView(self.db_manager)
        main_layout.addWidget(left_widget, 3)  # Left-Widget nimmt mehr Platz
        main_layout.addWidget(
            self.uebersicht, 2
        )  # Übersicht bekommt etwas weniger Platz

        # Toolbar mit Buttons oben
        self.create_toolbar()

    # Toolbar mit Buttons oben
    def create_toolbar(self):
        toolbar = QToolBar("Aktionen")
        self.addToolBar(Qt.TopToolBarArea, toolbar)

    # Buttons für die Toolbar
        add_button = QPushButton("Transaktion hinzufügen")
        add_button.setFixedSize(150, 30)
        add_button.clicked.connect(self.add_transaction)
        toolbar.addWidget(add_button)

        edit_button = QPushButton("Transaktion editieren")
        edit_button.clicked.connect(self.edit_transaction)
        edit_button.setFixedSize(150, 30)

        toolbar.addWidget(edit_button)

        delete_button = QPushButton("Transaktion löschen")
        delete_button.setFixedSize(150, 30)
        delete_button.clicked.connect(self.delete_transaction)
        toolbar.addWidget(delete_button)

        category_button = QPushButton("Kategorien Bearbeiten")
        category_button.setFixedSize(150, 30)
        category_button.clicked.connect(self.open_category_editor)
        toolbar.addWidget(category_button) 
        toolbar.addWidget(QWidget())  
        search_button = QPushButton("Suche")
        search_button.setFixedSize(100, 30)
        search_button.clicked.connect(self.open_search_window)
        toolbar.addWidget(search_button)

    # Öffnen des Kategorien-Editors
    def open_category_editor(self):
        dialog = CategoryEditDialog(self.db_manager)
        if dialog.exec():  # Dialog wird modal geöffnet
            self.update_view()  # Aktualisiere Hauptansicht, wenn der Dialog geschlossen wurde
            self.update_charts()  # Aktualisiere Hauptansicht, wenn der Dialog geschlossen wurde

    # Öffnen des Transaktionsdialogs zum Bearbeiten
    def edit_transaction(self):
        selected_item = self.uebersicht.transaction_list.currentItem()
        if not selected_item:
            print("Keine Transaktion ausgewählt!")
            return

        # Abrufen der ID aus dem ausgewählten Item
        transaction_id = selected_item.data(Qt.UserRole)
        if not transaction_id:
            print("Keine gültige ID gefunden!")
            return

        # Abrufen der Transaktionsdaten über die ID
        query = "SELECT * FROM Haupt WHERE id = ?"
        cursor = self.db_manager.execute(query, (transaction_id,))
        transaction_data = cursor.fetchone()

        # Transaktionsdialog mit den Daten füllen
        if transaction_data:
            dialog = TransactionDialog(
                "Transaktion bearbeiten", self.db_manager, transaction_data
            )
            if dialog.exec():
                print("Transaktion erfolgreich bearbeitet.")
                self.update_view()
        else:
            print("Fehler beim Abrufen der Transaktionsdaten.")

    # Abrufen der ausgewählten Transaktionsdaten
    def get_selected_transaction_data(self, item_text):
        parts = item_text.split(":")
        name_part = parts[0].strip()
        query = "SELECT * FROM Haupt WHERE Name_Transaktion = ?"
        cursor = self.db_manager.execute(query, (name_part,))
        return cursor.fetchone() if cursor else None

    # Löschen der ausgewählten Transaktion
    def delete_transaction(self, transaction_id):
        selected_item = self.uebersicht.transaction_list.currentItem()
        if not selected_item:
            print("Keine Transaktion ausgewählt!")
            return

        # ID der ausgewählten Transaktion abrufen
        transaction_id = selected_item.data(Qt.UserRole)
        if not transaction_id:
            print("Keine gültige ID gefunden!")
            return

        # Warnmeldung anzeigen, um das Löschen zu bestätigen
        confirm = QMessageBox.question(
            self,
            "Transaktion Löschen",
            f"Sind Sie sicher, dass Sie die Transaktion mit ID {transaction_id} löschen möchten?",  
            QMessageBox.Yes | QMessageBox.No,
        )

        # Falls Benutzer "Nein" auswählt, abbrechen
        if confirm == QMessageBox.No:
            print("Löschvorgang abgebrochen.")
            return

        # Löschoperation in der Datenbank
        query = "DELETE FROM Haupt WHERE id = ?"
        try:
            self.db_manager.execute(query, (transaction_id,))
            print(f"Transaktion mit ID {transaction_id} erfolgreich gelöscht.")
            self.update_view()  # Ansicht aktualisieren
        except Exception as e:
            print(f"Fehler beim Löschen der Transaktion: {e}")

    # Öffnen des Sufhcfensters
    def open_search_window(self):
        self.search_window = SuchleisteView(self.db_manager)
        self.search_window.show()

    # Hinzuüfgen einer Transaktion
    def add_transaction(self):
        dialog = TransactionDialog("Neue Transaktion", self.db_manager)
        if dialog.exec():  # exec() für den Dialog anzeigen
            print("Transaktion hinzugefügt")
        self.update_view()  # Aktualisierung der Liste

    # Aktualisierung der Diagramme
    def update_charts(self):
        print("Diagramme werden aktualisiert...")
        self.kreisdiagramm_view.update_chart()  # Aktualisiere Kreisdiagramm
        self.budgetdiagramm_view.update_chart()  # Aktualisiere Budget-Kreisdiagramm
        self.budget_chart_view.update_chart()  # Aktualisiere Balkendiagramm

    # Methode zum Aktualisieren der Ansicht
    def update_view(self):
        self.uebersicht.update_list()  # Aktualisierung der Liste
        self.budget_chart_view.update_chart()  # Aktualisierung des Säulendiagramms
        self.kreisdiagramm_view.update_chart()  # Aktualisierung der Kreisdiagramme
        self.budgetdiagramm_view.update_chart()  # Aktualisierung des Budget-Kreisdiagramms


def main():
    import sys

    print("Starte Anwendung...")

    # Initialisiere die Anwendung
    app = QApplication([])

    # Initialisiere die Datenbank (fiktiver Pfad zur DB-Datei)
    db_manager = DatabaseManager(
        "dingsbums.db"
    )  # Stellen Sie sicher, dass die Datenbankdatei existiert

    # Hauptseite laden
    main_page = MainPage(db_manager)
    main_page.showMaximized()

    # Starte die Event-Schleife der Anwendung
    sys.exit(app.exec())


# Einstiegspunkt für das Skript
if __name__ == "__main__":
    main()
