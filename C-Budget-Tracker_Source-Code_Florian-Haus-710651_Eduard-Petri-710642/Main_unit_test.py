import unittest
import sqlite3
from PySide6.QtWidgets import QApplication
from Core.database import DatabaseManager
from Features.Kategorien_Budget_Editor.view import CategoryEditDialog
from Features.Transaktionen_bearbeiten.view import TransactionDialog
import os
from _Main import MainPage
from PySide6.QtCore import QDate
import time


class TestMainPage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            # Initialisiere QApplication nur einmal für alle Tests
            cls.app = QApplication([])

        cls.db_path = "test_database.db"
        cls.connection = sqlite3.connect(cls.db_path)
        cls.cursor = cls.connection.cursor()

        # Lösche bestehende Tabellen
        cls.cursor.execute("DROP TABLE IF EXISTS Kategorie")
        cls.cursor.execute("DROP TABLE IF EXISTS Haupt")

        # Tabellen erstellen
        cls.cursor.execute(
            """ 
            CREATE TABLE Kategorie (
                Kategorie_ID INTEGER NOT NULL UNIQUE,
                Kategorie TEXT,
                Budget INTEGER,
                PRIMARY KEY("Kategorie_ID" AUTOINCREMENT)
            )
        """
        )
        cls.cursor.execute(
            """ 
            CREATE TABLE Haupt (
                ID INTEGER NOT NULL UNIQUE,
                Transaktion INTEGER NOT NULL,
                Name_Transaktion TEXT NOT NULL,
                Kategorie_FK INTEGER NOT NULL DEFAULT 0,
                Ausgabe_Einnahme TEXT NOT NULL,
                Datum TEXT NOT NULL,
                PRIMARY KEY(ID AUTOINCREMENT),
                FOREIGN KEY (Kategorie_FK) REFERENCES Kategorie(Kategorie_ID) ON UPDATE CASCADE
            )
        """
        )
        cls.connection.commit()

        # Beispieldaten einfügen
        cls.cursor.execute(
            "INSERT INTO Kategorie (Kategorie, Budget) VALUES ('Lebensmittel', 500)"
        )
        cls.cursor.execute(
            "INSERT INTO Kategorie (Kategorie, Budget) VALUES ('Freizeit', 300)"
        )
        cls.cursor.execute(
            "INSERT INTO Kategorie (Kategorie, Budget) VALUES ('Miete', 1000)"
        )

        # Einfügen von Transaktionen
        cls.cursor.execute(
            "INSERT INTO Haupt (Kategorie_FK, Name_Transaktion, Transaktion, Ausgabe_Einnahme, Datum) VALUES (1, 'Einkauf', 200, 'Ausgabe', '2025-01-01')"
        )
        cls.cursor.execute(
            "INSERT INTO Haupt (Kategorie_FK, Name_Transaktion, Transaktion, Ausgabe_Einnahme, Datum) VALUES (2, 'Kino', 100, 'Ausgabe', '2025-01-01')"
        )
        cls.cursor.execute(
            "INSERT INTO Haupt (Kategorie_FK, Name_Transaktion, Transaktion, Ausgabe_Einnahme, Datum) VALUES (3, 'Miete Januar', 1200, 'Ausgabe', '2025-01-01')"
        )
        cls.connection.commit()

        cls.db_manager = DatabaseManager(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        # Schließe die Datenbank und QApplication ordnungsgemäß
        cls.db_manager.close()
        cls.connection.close()
        if QApplication.instance():
            QApplication.instance().quit()  # QApplication ordnungsgemäß beenden
        os.remove(cls.db_path)

    def setUp(self):
        # Vermeide die erneute Erstellung der QApplication-Instanz
        self.main_page = MainPage(self.db_manager)

    # Deine anderen Testmethoden bleiben unverändert

    def test_transaction_addition(self):
        initial_transactions = len(self.fetchall("SELECT * FROM Haupt"))
        self.add_transaction_automatically()
        updated_transactions = len(self.fetchall("SELECT * FROM Haupt"))
        self.assertEqual(updated_transactions, initial_transactions + 1)

    def test_transaction_edit(self):
        transaction_id = self.fetchall("SELECT ID FROM Haupt")[0][0]
        self.edit_transaction(transaction_id, new_name="Neuer Einkauf", new_amount=250)
        edited_transaction = self.fetchall(
            "SELECT Name_Transaktion, Transaktion FROM Haupt WHERE ID = ?",
            (transaction_id,),
        )[0]
        self.assertEqual(edited_transaction[0], "Neuer Einkauf")
        self.assertEqual(edited_transaction[1], 250)

    def test_transaction_deletion(self):
        initial_count = len(self.fetchall("SELECT * FROM Haupt"))
        transaction_id = self.fetchall("SELECT ID FROM Haupt")[0][0]
        self.delete_transaction(transaction_id)
        updated_count = len(self.fetchall("SELECT * FROM Haupt"))
        self.assertEqual(updated_count, initial_count - 1)

    def test_empty_transaction_deletion(self):
        """Testet das Löschen, wenn keine Transaktionen in der Liste vorhanden sind."""
        self.delete_transaction(9999)  # Ungültige ID
        current_count = len(self.fetchall("SELECT * FROM Haupt"))
        self.assertEqual(
            current_count, 3
        )  # Es sollten immer noch 3 Transaktionen vorhanden sein

    def test_invalid_transaction_edit(self):
        """Testet das Bearbeiten einer nicht existierenden Transaktion."""
        invalid_transaction_id = 9999  # Ungültige ID
        self.edit_transaction(
            invalid_transaction_id, new_name="Falsche Transaktion", new_amount=500
        )
        # Keine Änderungen sollten erfolgt sein
        transaction = self.fetchall(
            "SELECT * FROM Haupt WHERE ID = ?", (invalid_transaction_id,)
        )
        self.assertEqual(len(transaction), 0)  # Keine Transaktion mit dieser ID

    def test_ui_category_editor_open(self):
        """Testet das Öffnen des Dialogs für den Kategorieneditor."""
        category_dialog = CategoryEditDialog(self.main_page.db_manager)
        category_dialog.show()  # Dialog sichtbar machen
        self.assertTrue(
            category_dialog.isVisible()
        )  # Überprüfen, ob der Dialog sichtbar ist

    def test_ui_transaction_dialog_open(self):
        """Testet das Öffnen des Dialogs zum Hinzufügen einer Transaktion."""
        self.add_transaction_automatically()

        # Nach dem Hinzufügen einer Transaktion, den Dialog öffnen und testen
        transaction_dialog = TransactionDialog(
            title="Transaktion Hinzufügen", db_manager=self.db_manager
        )
        transaction_dialog.show()
        self.assertTrue(
            transaction_dialog.isVisible()
        )  # Überprüfe, ob der Dialog sichtbar ist.

    def test_update_charts_after_transaction_addition(self):
        """Testet, ob die Diagramme nach dem Hinzufügen einer Transaktion aktualisiert werden."""
        initial_pie_chart_data = len(self.main_page.kreisdiagramm_view.ax.patches)

        # Füge eine Transaktion hinzu
        self.add_transaction_automatically()

        # Aktualisiere die Diagramme
        self.main_page.kreisdiagramm_view.update_chart()  # Aktualisiere das Kreisdiagramm
        self.main_page.budgetdiagramm_view.update_chart()  # Aktualisiere das Budget-Diagramm
        self.main_page.budget_chart_view.update_chart()  # Aktualisiere das Budget-Balkendiagramm

        # Warte, um sicherzustellen, dass die Diagramme aktualisiert wurden
        time.sleep(1)

        # Gib die Anzahl der Patches aus, um den Fortschritt zu prüfen
        print(
            f"Anzahl der Patches im Kreisdiagramm vor der Aktualisierung: {initial_pie_chart_data}"
        )
        print(
            f"Anzahl der Patches im Kreisdiagramm nach der Aktualisierung: {len(self.main_page.kreisdiagramm_view.ax.patches)}"
        )

        # Überprüfe, ob die Diagramme aktualisiert wurden
        self.assertTrue(
            len(self.main_page.kreisdiagramm_view.ax.patches) > initial_pie_chart_data
        )

    def add_transaction_automatically(self):
        dialog = TransactionDialog(
            title="Transaktion Hinzufügen", db_manager=self.db_manager
        )
        dialog.show()

        transaktion_name = "Einkauf"
        betrag = 200
        kategorie_id = 1
        ausgabe_einnahme = "Ausgabe"
        datum = "2025-01-01"

        dialog.name_input.setText(transaktion_name)
        dialog.amount_input.setText(str(betrag))
        dialog.category_input.setCurrentIndex(kategorie_id - 1)
        dialog.type_input.setCurrentText(ausgabe_einnahme)
        dialog.date_input.setDate(QDate.fromString(datum, "yyyy-MM-dd"))

        save_button = dialog.save_button
        if save_button:
            save_button.click()
        else:
            self.fail("Speichern-Button wurde nicht gefunden.")

        dialog.accept()

    def edit_transaction(self, transaction_id, new_name, new_amount):
        query = "UPDATE Haupt SET Name_Transaktion = ?, Transaktion = ? WHERE ID = ?"
        self.db_manager.execute(query, (new_name, new_amount, transaction_id))

    def delete_transaction(self, transaction_id):
        query = "DELETE FROM Haupt WHERE ID = ?"
        self.db_manager.execute(query, (transaction_id,))

    def fetchall(self, query, params=None):
        self.cursor.execute(query, params or [])
        return self.cursor.fetchall()


if __name__ == "__main__":
    unittest.main()
