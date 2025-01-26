import unittest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication
from Features.Budget_insgesamt.view import BudgetDiagrammView
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class TestBudgetDiagrammView(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        Setzt eine QApplication auf und stellt sicher, dass sie nur einmal gestartet wird.
        """
        cls.ensure_qapplication()

    @classmethod
    def ensure_qapplication(cls):
        """Stellt sicher, dass eine QApplication existiert."""
        if not QApplication.instance():
            QApplication([])

    def setUp(self):
        """
        Setzt die Testumgebung für jeden Testfall.
        """
        # Mock für den DB-Manager erstellen
        self.db_manager = MagicMock()

        # Beispieldaten für Budget und Ausgaben
        self.db_manager.execute.return_value.fetchall.return_value = [
            (1000,)
        ]  # Mock für alle Abfragen
        self.db_manager.execute.return_value.fetchone.return_value = (
            1000,
        )  # Mock für einzelne Abfragen

        # Instanz von BudgetDiagrammView erstellen
        self.view = BudgetDiagrammView(self.db_manager)

        # Mock für das Canvas-Objekt
        self.view.canvas = MagicMock(spec=FigureCanvas)

    def tearDown(self):
        """
        Entfernt die Instanz nach jedem Test.
        """
        self.view.deleteLater()

    def test_initialization(self):
        """
        Testet, ob die Klasse korrekt initialisiert wurde.
        """
        # Überprüfen, ob die Canvas für das Diagramm erstellt wurde
        self.assertIsInstance(self.view.canvas, FigureCanvas)

    def test_fetch_budget_data(self):
        """
        Testet, ob die Methode `fetch_budget_data` korrekt funktioniert.
        """
        expected_data = [("Verbleibendes Budget", 1000), ("Ausgaben", 0)]
        data = self.view.fetch_budget_data()
        self.assertEqual(data, expected_data)

    def test_plot_pie_chart(self):
        """
        Testet, ob das Kreisdiagramm korrekt geplottet wird.
        """
        # Die `plot_pie_chart` Methode aufrufen
        self.view.plot_pie_chart()

        # Überprüfen, ob das Diagramm korrekt gezeichnet wurde
        self.assertEqual(self.view.ax.get_title(), "Monatliches Budget")
        self.assertEqual(
            len(self.view.ax.patches), 2
        )  # 2 Segmente für verbleibendes Budget und Ausgaben

    def test_update_chart(self):
        """
        Testet, ob das Diagramm aktualisiert wird.
        """
        # Alte Werte überprüfen
        old_patches = len(self.view.ax.patches)

        # Die `update_chart` Methode aufrufen
        self.view.update_chart()

        # Überprüfen, ob das Diagramm nach dem Update weiterhin 2 Segmente hat
        self.assertEqual(
            len(self.view.ax.patches), old_patches
        )  # Sollte keine Veränderung geben

        # Überprüfen, ob draw() aufgerufen wurde
        self.view.canvas.draw.assert_called_once()  # Überprüfen, ob das Diagramm nach dem Update gezeichnet wurde


if __name__ == "__main__":
    unittest.main()
