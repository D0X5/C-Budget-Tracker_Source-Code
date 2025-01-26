import unittest
import sqlite3
from PySide6.QtWidgets import QApplication
from Features.Budget_Kategorie.view import (
    BudgetBarChartView,
)


class TestBudgetBarChartView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Setzt eine Testdatenbank auf und fügt Beispieldaten ein.
        """
        cls.db_path = "test_database.db"
        cls.connection = sqlite3.connect(cls.db_path)
        cls.cursor = cls.connection.cursor()

        # Tabellen erstellen
        cls.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Kategorie (
                Kategorie_ID INTEGER PRIMARY KEY,
                Kategorie TEXT,
                Budget INTEGER
            )
        """
        )
        cls.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Haupt (
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

        # Einfügen von Transaktionen mit Ausgabe_Einnahme und Datum
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

        # QApplication nur einmal starten
        cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        """
        Schließt die Verbindung zur Testdatenbank und entfernt die Datenbankdatei.
        """
        cls.connection.close()
        import os

        os.remove(cls.db_path)

        # QApplication nur einmal beenden
        cls.app.quit()

    def setUp(self):
        """
        Erstellt eine Instanz von BudgetBarChartView mit der Testdatenbank.
        """
        self.view = BudgetBarChartView(self)  # Instanz der BudgetBarChartView

    def tearDown(self):
        """
        Schließt die Qt-Anwendung nach jedem Test.
        """
        self.view.deleteLater()  # Entfernt die View aus der Anwendung, falls nötig

    def fetchall(self, query, params=None):
        """
        Führt eine SELECT-Abfrage auf der Testdatenbank aus und gibt die Ergebnisse zurück.
        """
        if params:
            return self.cursor.execute(query, params).fetchall()
        return self.cursor.execute(query).fetchall()

    def test_load_categories(self):
        """
        Testet, ob Kategorien korrekt in die ComboBox geladen werden.
        """
        expected_categories = {"Alle Kategorien", "Lebensmittel", "Freizeit", "Miete"}
        loaded_categories = {
            self.view.category_combo.itemText(i)
            for i in range(self.view.category_combo.count())
        }
        self.assertEqual(expected_categories, loaded_categories)

    def test_plot_bar_chart_all_categories(self):
        """
        Testet, ob das Diagramm für alle Kategorien korrekt geplottet wird.
        """
        self.view.plot_bar_chart("Alle Kategorien")
        # Sicherstellen, dass die Achsentitel korrekt gesetzt sind
        self.assertEqual(
            self.view.ax.get_title(),
            "Genutztes und verbleibendes Budget - Alle Kategorien",
        )
        self.assertEqual(self.view.ax.get_ylabel(), "Betrag (€)")

    def test_plot_bar_chart_specific_category(self):
        """
        Testet, ob das Diagramm für eine spezifische Kategorie korrekt geplottet wird.
        """
        self.view.plot_bar_chart("Lebensmittel")
        self.assertEqual(
            self.view.ax.get_title(),
            "Genutztes und verbleibendes Budget - Lebensmittel",
        )

    def test_update_chart(self):
        """
        Testet, ob das Diagramm aktualisiert wird, wenn die Kategorie gewechselt wird.
        """
        self.view.category_combo.setCurrentText("Freizeit")
        self.assertEqual(
            self.view.ax.get_title(), "Genutztes und verbleibendes Budget - Freizeit"
        )


if __name__ == "__main__":
    unittest.main()
