import unittest
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication, QMessageBox
from Features.Transaktionen_bearbeiten.view import TransactionDialog
from PySide6.QtCore import QDate


class TestTransactionDialog(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Setze die QApplication nur einmal für alle Tests"""
        if not QApplication.instance():
            cls.app = QApplication([])

    def setUp(self):
        """Setze den Testaufbau."""
        self.db_manager = MagicMock()  # Mock für den Datenbank-Manager
        self.dialog = TransactionDialog("Transaktion bearbeiten", self.db_manager)

    @patch.object(QMessageBox, "critical")  # Patching der QMessageBox.critical Methode
    def test_save_invalid_transaction(self, mock_critical):
        """Testet, ob ungültige Transaktionen richtig behandelt werden."""
        self.dialog.name_input.setText("")  # Kein Name
        self.dialog.amount_input.setText("500")  # Gültiger Betrag
        self.dialog.save_transaction()

        mock_critical.assert_called_once_with(
            self.dialog,
            "Ungültiger Name",
            "Bitte geben Sie einen Namen für die Transaktion ein.",
        )

    @patch.object(QMessageBox, "critical")  # Patching der QMessageBox.critical Methode
    def test_save_invalid_amount(self, mock_critical):
        """Testet, ob ungültige Beträge richtig behandelt werden."""
        self.dialog.name_input.setText("Einkauf")  # Gültiger Name
        self.dialog.amount_input.setText("Invalid Amount")  # Ungültiger Betrag
        self.dialog.save_transaction()

        mock_critical.assert_called_once_with(
            self.dialog,
            "Ungültiger Betrag",
            "Bitte geben Sie einen gültigen Betrag ein.",
        )

    def test_save_valid_transaction(self):
        """Testet, ob gültige Transaktionen korrekt gespeichert werden."""
        self.dialog.name_input.setText("Einkauf")
        self.dialog.amount_input.setText("500")
        self.dialog.category_input.addItem("Lebensmittel", 1)  # Beispielkategorie
        self.dialog.type_input.setCurrentIndex(0)
        self.dialog.date_input.setDate(QDate(2025, 1, 1))

        self.dialog.save_transaction()

        self.db_manager.add_transaction.assert_called_once_with(
            {
                "Transaktion": 500.0,
                "Name_Transaktion": "Einkauf",
                "Kategorie_FK": 1,
                "Ausgabe_Einnahme": "0",  # Ausgabe
                "Datum": "2025-01-01",
            }
        )

    def test_fill_data(self):
        """Testet, ob die Transaktionsdaten korrekt im Dialog angezeigt werden."""
        transaction_data = (1, 500.0, "Einkauf", 1, 0, "2025-01-01")
        self.dialog.transaction_data = transaction_data

        # Simuliere das Laden von Kategorien im ComboBox
        self.dialog.category_input.addItem("Lebensmittel", 1)  # Beispielkategorie

        self.dialog.fill_data()

        # Überprüfen, ob die Felder korrekt gefüllt wurden
        self.assertEqual(self.dialog.name_input.text(), "Einkauf")
        self.assertEqual(self.dialog.amount_input.text(), "500.0")
        self.assertEqual(
            self.dialog.category_input.currentIndex(), 0
        )  # Jetzt sollte der Index korrekt sein
        self.assertEqual(self.dialog.type_input.currentIndex(), 0)  # Ausgabe
        self.assertEqual(
            self.dialog.date_input.date().toString("yyyy-MM-dd"), "2025-01-01"
        )

    @classmethod
    def tearDownClass(cls):
        """Zerstöre QApplication nach allen Tests"""
        if QApplication.instance():
            QApplication.instance().quit()


if __name__ == "__main__":
    unittest.main()
