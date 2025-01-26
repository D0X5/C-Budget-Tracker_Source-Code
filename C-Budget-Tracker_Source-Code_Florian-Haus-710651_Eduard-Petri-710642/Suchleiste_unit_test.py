import unittest
import sqlite3
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QCalendarWidget,
)
from PySide6.QtCore import Qt
from datetime import datetime
from unittest.mock import patch


# Simuliere eine einfache Datenbankabfrage
class MockDbManager:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        return cursor

    def search_transactions(self, search_term):
        """Simuliert eine Suche nach Transaktionen in der Datenbank."""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            SELECT * FROM Transaktionen
            WHERE name LIKE ? OR category LIKE ? OR date LIKE ?
        """,
            ("%" + search_term + "%", "%" + search_term + "%", "%" + search_term + "%"),
        )
        transactions = cursor.fetchall()
        print(
            "Suchergebnisse:", transactions
        )  # Zeigt die Ergebnisse der Abfrage im Terminal an
        return transactions


# Das View, das die Suchleiste implementiert
class SuchleisteView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Suchfenster")
        self.setMinimumSize(1500, 800)
        self.showMaximized()

        layout = QVBoxLayout()

        title = QLabel("Suchleiste")
        layout.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suchbegriff eingeben...")
        layout.addWidget(self.search_input)

        # Suchbutton
        search_button = QPushButton("Suchen")
        search_button.clicked.connect(self.search_transactions)
        layout.addWidget(search_button)

        # Ergebnis Liste
        self.result_list = QListWidget()
        layout.addWidget(self.result_list)

        # Kalender Widget
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.on_date_selected)
        layout.addWidget(self.calendar)

        self.setLayout(layout)

    def search_transactions(self):
        search_term = self.search_input.text()

        # Hole Transaktionen aus der Datenbank
        transactions = self.db_manager.search_transactions(search_term)

        self.result_list.clear()

        # Gruppiere die Transaktionen nach Datum
        grouped_transactions = {}
        for trans in transactions:
            id, amount, name, category, type_, date = trans
            date_obj = datetime.strptime(
                date, "%Y-%m-%d"
            )  # Datum in datetime-Objekt umwandeln
            formatted_date = date_obj.strftime(
                "%d.%m.%Y"
            )  # Formatierung: Tag.Monat.Jahr

            if formatted_date not in grouped_transactions:
                grouped_transactions[formatted_date] = []
            grouped_transactions[formatted_date].append((name, category, amount, type_))

        # Füge die gruppierten Transaktionen zur Ergebnisliste hinzu
        for date, transactions_on_date in grouped_transactions.items():
            date_header = QListWidgetItem(date)
            self.result_list.addItem(date_header)

            for name, category, amount, type_ in transactions_on_date:
                transaction_widget = QListWidgetItem(
                    f"{name} - {category} - {amount} {type_}"
                )
                self.result_list.addItem(transaction_widget)

    def on_date_selected(self):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        transactions = self.db_manager.search_transactions(selected_date)

        self.result_list.clear()
        for trans in transactions:
            id, amount, name, category, type_, date = trans
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")

            transaction_widget = QListWidgetItem(
                f"{name} - {category} - {amount} {type_}"
            )
            self.result_list.addItem(transaction_widget)


# Unittest Klasse für die Suchleiste
class TestSuchleisteView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialisiert die Testdatenbank und erstellt eine Instanz der Kategorie-Edit-Dialog."""
        cls.db_path = "test_category_database.db"
        cls.connection = sqlite3.connect(cls.db_path)
        cls.cursor = cls.connection.cursor()

        # Tabellen erstellen
        cls.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Transaktionen (
                id INTEGER PRIMARY KEY,
                name TEXT,
                category TEXT,
                amount REAL,
                type_ TEXT,
                date TEXT
            )
        """
        )
        cls.connection.commit()

        # Beispieldaten einfügen
        cls.cursor.execute(
            "INSERT INTO Transaktionen (name, category, amount, type_, date) VALUES ('Einkauf', 'Lebensmittel', 50, 'Ausgabe', '2025-01-20')"
        )
        cls.cursor.execute(
            "INSERT INTO Transaktionen (name, category, amount, type_, date) VALUES ('Freizeit', 'Freizeit', 100, 'Ausgabe', '2025-01-21')"
        )
        cls.connection.commit()

        cls.db_manager = MockDbManager(cls.connection)

        # QApplication nur einmal starten
        cls.ensure_qapplication()

    @classmethod
    def tearDownClass(cls):
        """Schließt die Verbindung zur Testdatenbank und entfernt die Datenbankdatei."""
        cls.connection.close()
        import os

        os.remove(cls.db_path)

    @staticmethod
    def ensure_qapplication():
        """Stellt sicher, dass eine QApplication existiert."""
        if not QApplication.instance():
            QApplication([])

    def setUp(self):
        """Erstellt eine Instanz von SuchleisteView mit der Testdatenbank."""
        self.widget = SuchleisteView(self.db_manager)

    def tearDown(self):
        """Schließt das Widget nach jedem Test."""
        self.widget.deleteLater()

    def test_search_transactions(self):
        """Testet, ob die Transaktionssuche korrekt funktioniert."""
        self.widget.search_input.setText("Einkauf")
        self.widget.search_transactions()

        result_items = self.widget.result_list.findItems("Einkauf", Qt.MatchContains)
        print(f"Gefundene Items: {result_items}")  # Zum Debuggen
        self.assertGreater(
            len(result_items), 0, "Die Transaktion 'Einkauf' wurde nicht gefunden."
        )

    def test_date_selected(self):
        """Testet, ob bei Auswahl eines Datums die richtigen Transaktionen angezeigt werden."""
        self.widget.calendar.setSelectedDate(datetime(2025, 1, 20))
        self.widget.on_date_selected()

        result_items = self.widget.result_list.findItems("Einkauf", Qt.MatchContains)
        print(f"Gefundene Items: {result_items}")  # Zum Debuggen
        self.assertGreater(
            len(result_items),
            0,
            "Die Transaktion 'Einkauf' wurde nicht für das ausgewählte Datum gefunden.",
        )


if __name__ == "__main__":
    unittest.main()
