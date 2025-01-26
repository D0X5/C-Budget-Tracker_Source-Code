from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class BudgetDiagrammView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        # Layout für das Widget
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Matplotlib-Figure und -Canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Initialisiere das Diagramm
        self.plot_pie_chart()

    def plot_pie_chart(self):
        """
        Plottet ein Kreisdiagramm für das monatliche Budget und die Ausgaben.
        """
        budget_data = self.fetch_budget_data()
        if budget_data:
            labels, values = zip(*budget_data)
            self.ax.clear()
            self.ax.pie(values, labels=labels, autopct="%1.2f%%", startangle=140)
            self.ax.set_title("Monatliches Budget", color="#004A94", fontweight="bold")
            self.canvas.draw()

    def fetch_budget_data(self):
        """
        Holt das Budget und die Ausgaben für den aktuellen Monat.
        """
        # Budget aus der Datenbank abrufen
        budget_query = "SELECT SUM(Budget) FROM Kategorie"
        budget_row = self.db_manager.execute(budget_query).fetchone()
        if budget_row is None or budget_row[0] is None:
            print("Fehler: Keine Kategorien mit Budgets gefunden.")
            return None
        total_budget = budget_row[0]

        # Ausgaben aus der Datenbank abrufen
        expenses_query = """
        SELECT SUM(Transaktion)
        FROM Haupt
        WHERE Ausgabe_Einnahme = '0'
        AND strftime('%Y-%m', Datum) = strftime('%Y-%m', 'now')
        """
        expenses_row = self.db_manager.execute(expenses_query).fetchone()
        expenses = expenses_row[0] if expenses_row[0] is not None else 0

        # Verbleibendes Budget berechnen
        remaining_budget = max(total_budget - expenses, 0)

        # Daten für das Diagramm vorbereiten
        return [("Budget", remaining_budget), ("Ausgaben", expenses)]

    def update_chart(self):
        """
        Aktualisiert das Diagramm basierend auf den neuesten Daten.
        """
        self.fetch_budget_data()
        self.plot_pie_chart()
