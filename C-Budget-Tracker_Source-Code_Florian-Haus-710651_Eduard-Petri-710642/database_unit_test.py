import unittest
import sqlite3
from datetime import datetime
import os
from Core.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Vorbereitung der Testdatenbank und Initialisierung des DatabaseManagers"""
        cls.db_path = "test_database.db"
        cls.create_test_database()
        cls.db_manager = DatabaseManager(cls.db_path)

    @classmethod
    def create_test_database(cls):
        """Erstelle die Tabellen und füge Beispieltransaktionen in die Testdatenbank ein"""
        query_create_kategorie = """
        CREATE TABLE IF NOT EXISTS Kategorie (
            Kategorie_ID INTEGER PRIMARY KEY,
            Kategorie TEXT,
            Budget REAL NOT NULL DEFAULT 0
        )
        """
        query_create_haupt = """
        CREATE TABLE IF NOT EXISTS Haupt (
            ID INTEGER PRIMARY KEY,
            Transaktion REAL,
            Name_Transaktion TEXT,
            Kategorie_FK INTEGER,
            Ausgabe_Einnahme INTEGER,
            Datum TEXT,
            FOREIGN KEY (Kategorie_FK) REFERENCES Kategorie(Kategorie_ID)
        )
        """

        with sqlite3.connect(cls.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS Haupt")
            cursor.execute("DROP TABLE IF EXISTS Kategorie")
            cursor.execute(query_create_kategorie)
            cursor.execute(query_create_haupt)

            cursor.execute(
                "INSERT INTO Kategorie (Kategorie_ID, Kategorie, Budget) VALUES (1, 'Lebensmittel', 500)"
            )
            cursor.execute(
                "INSERT INTO Kategorie (Kategorie_ID, Kategorie, Budget) VALUES (2, 'Freizeit', 300)"
            )
            cursor.execute(
                "INSERT INTO Haupt (Transaktion, Name_Transaktion, Kategorie_FK, Ausgabe_Einnahme, Datum) VALUES (100, 'Kauf Lebensmittel', 1, 0, ?)",
                (str(datetime.now()),),
            )
            cursor.execute(
                "INSERT INTO Haupt (Transaktion, Name_Transaktion, Kategorie_FK, Ausgabe_Einnahme, Datum) VALUES (200, 'Kino', 2, 0, ?)",
                (str(datetime.now()),),
            )
            cursor.execute(
                "INSERT INTO Haupt (Transaktion, Name_Transaktion, Kategorie_FK, Ausgabe_Einnahme, Datum) VALUES (50, 'Kaffee', 1, 0, ?)",
                (str(datetime.now()),),
            )
            conn.commit()

    @classmethod
    def tearDownClass(cls):
        """Aufräumen nach den Tests"""
        if hasattr(cls, "db_manager"):
            cls.db_manager.close()  # Schließe die Datenbankverbindung sicher
        # Sicherstellen, dass die Datenbankdatei entfernt werden kann
        try:
            os.remove(cls.db_path)  # Entferne die Testdatenbank
        except PermissionError:
            print(
                f"Fehler beim Löschen der Datei: {cls.db_path}. Die Datei wird möglicherweise von einem anderen Prozess verwendet."
            )

    # Testmethoden wie test_add_transaction, test_fetch_expenses_per_category, etc.

    def test_fetch_transactions(self):
        """Testet die Methode `fetch_transactions`."""
        transactions = self.db_manager.fetch_transactions()

        # Überprüfen, ob Transaktionen zurückgegeben werden
        self.assertGreater(len(transactions), 0)

        # Beispiel: Überprüfen, ob der Name der ersten Transaktion korrekt ist
        self.assertEqual(transactions[0][2], "Kauf Lebensmittel")

    def test_search_transactions(self):
        """Testet die Methode `search_transactions` nach Name."""
        search_term = "Kino"
        results = self.db_manager.search_transactions(search_term)

        # Überprüfen, ob die korrekte Transaktion gefunden wird
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0][2], "Kino")

    def test_fetch_expenses_per_category(self):
        """Testet die Methode `fetch_expenses_per_category`."""
        expenses = self.db_manager.fetch_expenses_per_category()

        # Überprüfen, ob Ausgaben für die Kategorie 'Lebensmittel' und 'Freizeit' zurückgegeben werden
        self.assertGreater(len(expenses), 0)
        self.assertEqual(expenses[0][0], "Freizeit")
        self.assertEqual(expenses[1][0], "Lebensmittel")

    def test_add_transaction(self):
        """Testet die Methode `add_transaction`."""
        transaction_data = {
            "Transaktion": 300,
            "Name_Transaktion": "Buch Kauf",
            "Kategorie_FK": 1,  # 'Lebensmittel'
            "Ausgabe_Einnahme": 0,  # Ausgabe
            "Datum": str(datetime.now()),
        }

        # Transaktion hinzufügen
        result = self.db_manager.add_transaction(transaction_data)

        # Überprüfen, ob die Transaktion erfolgreich hinzugefügt wurde
        self.assertTrue(result)

        # Überprüfen, ob die Transaktion in der Datenbank existiert
        transactions = self.db_manager.fetch_transactions()
        self.assertGreater(len(transactions), 3)  # Es gibt nun mehr als 3 Transaktionen

    def test_update_transaction(self):
        """Testet die Methode `update_transaction`."""
        transaction_data = {
            "Transaktion": 400,
            "Name_Transaktion": "Buch Kauf Update",
            "Kategorie_FK": 1,  # 'Lebensmittel'
            "Ausgabe_Einnahme": 0,  # Ausgabe
            "Datum": str(datetime.now()),
        }

        # Zuerst eine Transaktion hinzufügen
        self.db_manager.add_transaction(transaction_data)

        # Die ID der zuletzt hinzugefügten Transaktion ermitteln
        transaction_id = self.db_manager.fetch_transactions()[-1][0]

        # Neue Daten für die Transaktion vorbereiten
        updated_data = {
            "Transaktion": 500,
            "Name_Transaktion": "Buch Kauf Update Final",
            "Kategorie_FK": 1,  # 'Lebensmittel'
            "Ausgabe_Einnahme": 0,  # Ausgabe
            "Datum": str(datetime.now()),
        }

        # Transaktion aktualisieren
        self.db_manager.update_transaction(transaction_id, updated_data)

        # Überprüfen, ob die Transaktion erfolgreich aktualisiert wurde
        updated_transaction = self.db_manager.fetch_transaction_by_id(transaction_id)
        self.assertEqual(updated_transaction["Transaktion"], 500)
        self.assertEqual(
            updated_transaction["Name_Transaktion"], "Buch Kauf Update Final"
        )


if __name__ == "__main__":
    unittest.main()
