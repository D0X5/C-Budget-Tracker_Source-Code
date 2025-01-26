import unittest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication, QLabel
from Features.Übersicht.view import UebersichtView, TransactionWidget


class TestUebersichtView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Stelle sicher, dass QApplication nur einmal erstellt wird
        if not QApplication.instance():  # Prüfe, ob QApplication bereits existiert
            cls.app = QApplication([])  # Nur einmal instanziieren
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        # Erstelle ein Mock für den DatabaseManager
        self.db_manager = MagicMock()

        # Beispiel-Datenbankantwort mit Transaktionen
        self.db_manager.fetch_transactions.return_value = [
            (1, 50.0, "Einnahme1", "Kategorie1", 1, "2025-01-25 10:00:00"),
            (2, 30.0, "Ausgabe1", "Kategorie2", 0, "2025-01-25 12:00:00"),
            (3, 20.0, "Einnahme2", "Kategorie1", 1, "2025-01-24 09:00:00")
        ]

        # Erstelle das UebersichtView mit dem gemockten DatabaseManager
        self.view = UebersichtView(self.db_manager)

    def tearDown(self):
        # Bereinige nach jedem Test
        self.view.deleteLater()

    @classmethod
    def tearDownClass(cls):
        # Beende QApplication nur einmal nach allen Tests
        cls.app.quit()

    def test_initial_balance(self):
        # Überprüfe den initialen Kontostand nach dem Laden der Transaktionen
        self.view.load_transactions()
        self.assertEqual(self.view.balance_label.text(), "Kontostand: 40.00 €")

    def test_load_transactions(self):
        # Lade die Transaktionen
        self.view.load_transactions()

        # Gib die Anzahl der Items aus
        item_count = self.view.transaction_list.count()
        print(f"Anzahl der Items in der Liste: {item_count}")

        # Überprüfe jedes einzelne Item in der Liste
        for index in range(item_count):
            item = self.view.transaction_list.item(index)
            widget = self.view.transaction_list.itemWidget(item)
            if widget:
                # Gib den Text des Widgets (TransactionWidget oder QLabel) aus
                print(f"Item {index}: {widget.findChild(QLabel).text() if isinstance(widget, TransactionWidget) else 'Datum: ' + widget.text()}")

        # Überprüfe, ob die Anzahl der Items 5 ist (2 Datumseinträge + 3 Transaktionen)
        self.assertEqual(item_count, 7)


    def test_transaction_widget_display(self):
        # Überprüfe, ob die Transaktionen korrekt im Widget angezeigt werden
        self.view.load_transactions()
        
        # Prüfe, ob der erste Transaktionseintrag das erwartete Widget hat
        item = self.view.transaction_list.item(1)  # Zweites Item sollte eine Transaktion sein
        transaction_widget = self.view.transaction_list.itemWidget(item)
        
        self.assertIsInstance(transaction_widget, TransactionWidget)
        self.assertEqual(transaction_widget.findChild(QLabel).text(), "Einnahme1")

    def test_balance_style_positive(self):
        # Überprüfe den Stil des Kontostands bei positivem Wert
        self.view.load_transactions()
        self.assertEqual(self.view.balance_label.styleSheet(), "color: #4CAF50; font-weight: bold;")

    def test_balance_style_negative(self):
        # Füge eine negative Transaktion hinzu und überprüfe den Stil
        self.db_manager.fetch_transactions.return_value.append(
            (4, 100.0, "Ausgabe2", "Kategorie3", 0, "2025-01-24 15:00:00")
        )
        self.view.load_transactions()
        self.assertEqual(self.view.balance_label.styleSheet(), "color: red; font-weight: bold;")

if __name__ == "__main__":
    unittest.main()
