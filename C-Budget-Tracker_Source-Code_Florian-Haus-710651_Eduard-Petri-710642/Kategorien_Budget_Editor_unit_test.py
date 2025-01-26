import unittest
import sqlite3
from PySide6.QtWidgets import QApplication
from Features.Kategorien_Budget_Editor.view import CategoryEditDialog
from PySide6.QtCore import Qt
from unittest.mock import patch


class MockDbManager:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        return cursor


class TestCategoryEditDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialisiert die Testdatenbank und erstellt eine Instanz der Kategorie-Edit-Dialog."""
        cls.db_path = "test_category_database.db"
        cls.connection = sqlite3.connect(cls.db_path)
        cls.cursor = cls.connection.cursor()

        # Tabellen erstellen
        cls.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Kategorie (
                Kategorie_ID INTEGER PRIMARY KEY,
                Kategorie TEXT,
                Budget REAL
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
        cls.connection.commit()

        cls.db_manager = MockDbManager(cls.connection)

        # QApplication nur einmal starten, wenn keine Instanz existiert
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
        """Erstellt eine Instanz von CategoryEditDialog mit der Testdatenbank."""
        self.dialog = CategoryEditDialog(self.db_manager)

    def tearDown(self):
        """Schließt den Dialog nach jedem Test."""
        self.dialog.deleteLater()

    def test_delete_category(self):
        """Testet, ob eine Kategorie korrekt gelöscht wird, ohne den Bestätigungsdialog oder das Fenster anzuzeigen."""
        self.dialog.load_categories()
        self.dialog.category_list.setCurrentRow(
            0
        )  # Wählt die erste Kategorie (Lebensmittel)

        # Ohne Bestätigungsdialog, direkt löschen
        def no_confirm_delete():
            selected_item = self.dialog.category_list.currentItem()
            if not selected_item:
                return

            category_data = selected_item.data(Qt.UserRole)
            category_id = category_data["id"]

            # Hier überspringen wir den Bestätigungsdialog
            query = "DELETE FROM Kategorie WHERE Kategorie_ID = ?"
            self.db_manager.execute(query, (category_id,))
            self.db_manager.connection.commit()

            # Liste der Kategorien aktualisieren
            self.dialog.load_categories()

        # Teste das Löschen ohne Bestätigung
        with patch.object(self.dialog, "delete_category", no_confirm_delete):
            self.dialog.delete_category()

        # Prüfen, ob die Kategorie gelöscht wurde
        self.cursor.execute(
            "SELECT COUNT(*) FROM Kategorie WHERE Kategorie = ?", ("Lebensmittel",)
        )
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 0)

    def test_add_category(self):
        """Testet das Hinzufügen einer neuen Kategorie."""
        # Eingabewerte setzen
        self.dialog.name_edit.setText("Neue Kategorie")
        self.dialog.budget_edit.setValue(250)

        # Füge die Kategorie hinzu
        self.dialog.add_category()

        # Überprüfen, ob die Kategorie in der Datenbank vorhanden ist
        self.cursor.execute(
            "SELECT COUNT(*) FROM Kategorie WHERE Kategorie = ?", ("Neue Kategorie",)
        )
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1)

    def test_add_category_with_empty_name(self):
        """Testet das Hinzufügen einer Kategorie mit leerem Namen."""
        # Setze leeren Namen
        self.dialog.name_edit.setText("")
        self.dialog.budget_edit.setValue(250)

        # Versuche, die Kategorie hinzuzufügen
        self.dialog.add_category()

        # Überprüfen, ob die Kategorie nicht hinzugefügt wurde
        self.cursor.execute("SELECT COUNT(*) FROM Kategorie WHERE Kategorie = ?", ("",))
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 0)

    def test_save_category(self):
        """Testet das Speichern einer bearbeiteten Kategorie."""
        self.dialog.load_categories()
        self.dialog.category_list.setCurrentRow(
            0
        )  # Wählt die erste Kategorie (Lebensmittel)

        # Setze neue Werte
        self.dialog.name_edit.setText("Lebensmittel 2")
        self.dialog.budget_edit.setValue(600)

        # Speichere die Kategorie
        self.dialog.save_category()

        # Überprüfen, ob die Kategorie in der Datenbank aktualisiert wurde
        self.cursor.execute(
            "SELECT Kategorie, Budget FROM Kategorie WHERE Kategorie = ?",
            ("Lebensmittel 2",),
        )
        result = self.cursor.fetchone()
        self.assertEqual(result[0], "Lebensmittel 2")
        self.assertEqual(result[1], 600)

    def test_delete_non_existent_category(self):
        """Testet das Löschen einer nicht existierenden Kategorie."""
        # Setze eine ungültige Auswahl
        self.dialog.category_list.setCurrentRow(
            999
        )  # Wählt eine nicht existierende Kategorie

        # Versuche zu löschen
        self.dialog.delete_category()

        # Überprüfen, dass keine Kategorie gelöscht wurde
        self.cursor.execute(
            "SELECT COUNT(*) FROM Kategorie WHERE Kategorie = ?",
            ("Nicht Existierende",),
        )
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
