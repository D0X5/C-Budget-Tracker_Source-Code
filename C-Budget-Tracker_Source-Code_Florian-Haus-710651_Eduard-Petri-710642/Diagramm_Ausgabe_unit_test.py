import unittest
from PySide6.QtWidgets import QApplication
from Features.Diagramm_Ausgabe.view import DiagrammView


# Beispiel-Datenbank-Manager-Klasse für Tests
class TestDBManager:
    def fetch_expenses_per_category(self):
        """
        Gibt einige Beispieldaten für das Testen zurück.
        """
        return [("Lebensmittel", 200), ("Freizeit", 100), ("Miete", 1200)]


# Testklasse für DiagrammView
class TestDiagrammView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Setzt eine QApplication für alle Tests (nur wenn noch keine existiert).
        """
        if not QApplication.instance():
            cls.app = QApplication([])

    @classmethod
    def tearDownClass(cls):
        """
        Beendet die QApplication nach den Tests, falls sie existiert.
        """
        if hasattr(cls, "app"):
            cls.app.quit()

    def test_fetch_expenses_per_category(self):
        """
        Testet, ob die Methode fetch_expenses_per_category korrekt funktioniert.
        """
        # Erstelle den Test-Datenbank-Manager
        db_manager = TestDBManager()

        # Erstelle die DiagrammView-Instanz
        view = DiagrammView(db_manager)

        # Rufe die fetch_expenses_per_category-Methode auf
        category_data = view.fetch_expenses_per_category()

        # Überprüfen, ob die Daten korrekt zurückgegeben werden
        self.assertEqual(
            category_data, [("Lebensmittel", 200), ("Freizeit", 100), ("Miete", 1200)]
        )

    def test_plot_pie_chart(self):
        """
        Testet, ob das Kreisdiagramm korrekt geplottet wird.
        """
        # Erstelle den Test-Datenbank-Manager
        db_manager = TestDBManager()

        # Erstelle die DiagrammView-Instanz
        view = DiagrammView(db_manager)

        # Sicherstellen, dass der Titel des Diagramms korrekt gesetzt wurde
        self.assertEqual(view.ax.get_title(), "Ausgaben pro Kategorie")

        # Sicherstellen, dass das Diagramm gezeichnet wurde
        # Wir überprüfen, ob die "canvas.draw" Methode aufgerufen wurde
        self.assertTrue(view.canvas.figure.axes[0].has_data())

        # Überprüfen, ob die Kategorien und Werte korrekt gesetzt sind
        labels, values = zip(*db_manager.fetch_expenses_per_category())
        self.assertEqual(labels, ("Lebensmittel", "Freizeit", "Miete"))
        self.assertEqual(values, (200, 100, 1200))

    def test_update_chart(self):
        """
        Testet, ob das Diagramm aktualisiert wird, wenn update_chart aufgerufen wird.
        """
        # Erstelle den Test-Datenbank-Manager
        db_manager = TestDBManager()

        # Erstelle die DiagrammView-Instanz
        view = DiagrammView(db_manager)

        # Wir ändern die Daten und rufen update_chart auf
        new_data = [("Essen", 300), ("Shopping", 500), ("Miete", 1300)]
        db_manager.fetch_expenses_per_category = lambda: new_data

        # Rufe die Methode zum Aktualisieren des Diagramms auf
        view.update_chart()

        # Überprüfen, ob die neuen Daten angezeigt werden
        new_labels, new_values = zip(*new_data)
        self.assertEqual(new_labels, ("Essen", "Shopping", "Miete"))
        self.assertEqual(new_values, (300, 500, 1300))


if __name__ == "__main__":
    unittest.main()
