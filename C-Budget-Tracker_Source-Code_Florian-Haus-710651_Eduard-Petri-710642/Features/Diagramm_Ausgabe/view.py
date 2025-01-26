from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class DiagrammView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.plot_pie_chart()

    def plot_pie_chart(self):
        """
        Plottet ein Kreisdiagramm basierend auf den Ausgaben nach Kategorien.
        Zeigt eine Nachricht an, wenn keine Daten vorhanden sind.
        """
        category_data = self.fetch_expenses_per_category()

        self.ax.clear()  # Lösche den aktuellen Plot

        if category_data:
            # Wenn Daten vorhanden sind, plotte das Diagramm
            labels, values = zip(*category_data)
            total = sum(values)

            def autopct_func(pct, allvalues):
                absolute = pct / 100.0 * total
                # Zeige Prozentanzeige nur für Segmente > 5%
                return f"{pct:.1f}%" if absolute > total * 0.05 else ""

            # Erstelle das Kreisdiagramm
            self.ax.pie(
                values,
                labels=labels,
                autopct=lambda pct: autopct_func(pct, values),
                startangle=140,
            )
            self.ax.set_title(
                "Ausgaben pro Kategorie", color="#004A94", fontweight="bold"
            )
        else:
            # Wenn keine Daten vorhanden sind, zeige eine Nachricht an
            self.ax.text(
                0.5,
                0.5,
                "Keine Daten verfügbar",
                fontsize=14,
                ha="center",
                va="center",
                color="gray",
            )
            self.ax.set_title(
                "Ausgaben pro Kategorie", color="#004A94", fontweight="bold"
            )

        self.canvas.draw()

    def fetch_expenses_per_category(self):
        """
        Holt die Summen der Ausgaben gruppiert nach Kategorien.
        """
        return self.db_manager.fetch_expenses_per_category()

    def update_chart(self):
        """
        Aktualisiert das Diagramm basierend auf den neuesten Daten.
        """
        self.plot_pie_chart()
