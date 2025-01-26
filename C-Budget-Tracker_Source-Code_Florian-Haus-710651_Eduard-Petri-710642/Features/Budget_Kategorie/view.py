from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class BudgetBarChartView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        # Layout einrichten
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # ComboBox für die Auswahl der Kategorie
        self.category_combo = QComboBox()
        self.category_combo.addItem("Alle Kategorien")  # Option für alle Kategorien
        self.category_combo.currentTextChanged.connect(self.update_chart)
        layout.addWidget(self.category_combo)  # Dropdown direkt oben im Layout

        # Matplotlib-Canvas
        self.figure, self.ax = plt.subplots(figsize=(8, 6))  # Größe der Figur anpassen
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Kategorien in die ComboBox einfügen und Diagramm zeichnen
        self.load_categories()
        self.plot_bar_chart()  # Initialisiere Diagramm

    def load_categories(self):
        """
        Holt die Kategorien aus der Datenbank und fügt sie der ComboBox hinzu,
        vermeidet Duplikate.
        """
        categories = self.fetch_categories()
        existing_items = set(
            self.category_combo.itemText(i) for i in range(self.category_combo.count())
        )

        for category in categories:
            if category not in existing_items:
                self.category_combo.addItem(category)

    def fetch_categories(self):
        """
        Holt alle Kategorien aus der Datenbank.
        """
        query = "SELECT Kategorie FROM Kategorie"
        categories = self.db_manager.fetchall(query)
        return [category[0] for category in categories]

    def update_chart(self):
        """
        Aktualisiert das Diagramm basierend auf der ausgewählten Kategorie.
        """
        selected_category = self.category_combo.currentText()
        self.plot_bar_chart(selected_category)

    def plot_bar_chart(self, selected_category="Alle Kategorien"):
        """
        Erstellt ein Diagramm, das basierend auf der ausgewählten Kategorie (oder allen Kategorien)
        das genutzte und verbleibende Budget anzeigt.
        """
        category_data = self.fetch_category_data(selected_category)
        if not category_data:
            self.ax.text(
                0.5,
                0.5,
                "Keine Kategorien mit definiertem Budget gefunden",
                horizontalalignment="center",
                verticalalignment="center",
            )
            self.canvas.draw()
            return

        # Daten aufteilen
        categories, budgets, used_budgets = zip(*category_data)

        # Verbleibendes Budget berechnen
        remaining_budgets = [
            max(0, budget - used) for budget, used in zip(budgets, used_budgets)
        ]

        # Berechnung der Überschreitungen (rote Balken)
        overflow_budgets = [
            max(0, used - budget) for used, budget in zip(used_budgets, budgets)
        ]

        # Diagramm erstellen
        x = range(len(categories))
        self.ax.clear()

        # Dynamische Balkenbreite: Wenn nur eine Kategorie, Balken schmaler machen
        if len(categories) == 1:
            bar_width = 0.2  
        else:
            bar_width = max(
                0.1, 0.35 / len(categories)
            )  # Dynamisch abhängig von der Anzahl der Kategorien

        # Gestapeltes Balkendiagramm (schmalere Balken)
        self.ax.bar(
            x, used_budgets, width=bar_width, label="Genutztes Budget", color="darkblue"
        )
        self.ax.bar(
            x,
            remaining_budgets,
            width=bar_width,
            bottom=used_budgets,
            label="Verbleibendes Budget",
            color="skyblue",
        )

        # Rote Balken für Überschreitungen (oberhalb des Budgetbalkens)
        self.ax.bar(
            x,
            overflow_budgets,
            width=bar_width,
            bottom=budgets,
            label="Überschreitung",
            color="red",
        )

        # Diagramm-Details
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(
            categories, rotation=45, ha="right"
        )  
        self.ax.set_ylabel("Betrag (€)")
        self.ax.set_title(f"Genutztes und verbleibendes Budget - {selected_category}")

        # Nutze den höchsten Wert
        max_value = max(
            max(used_budgets), max(remaining_budgets), max(overflow_budgets)
        )

        # Y-Achse anpassen: max_value + 300 Euro als oberer Wert
        self.ax.set_ylim(0, max_value + 300)

        # Legende oben rechts positionieren und mit dem Diagramm skalieren
        self.ax.legend(loc="upper right", bbox_to_anchor=(1, 1), borderaxespad=0.0)

        # Den Abstand anpassen, um sicherzustellen, dass die Beschriftungen nicht abgeschnitten werden
        plt.subplots_adjust(
            bottom=0.3, right=0.85
        )  

        # Diagramm aktualisieren
        self.canvas.draw()

    def fetch_category_data(self, selected_category):
        """
        Holt die Daten für die ausgewählte Kategorie oder alle Kategorien.
        """
        if selected_category == "Alle Kategorien":
            query = """
            SELECT 
                Kategorie.Kategorie, 
                Kategorie.Budget, 
                COALESCE(SUM(Haupt.Transaktion), 0) AS UsedBudget
            FROM Kategorie
            LEFT JOIN Haupt ON Kategorie.Kategorie_ID = Haupt.Kategorie_FK
            WHERE Kategorie.Budget > 0
            GROUP BY Kategorie.Kategorie_ID, Kategorie.Kategorie, Kategorie.Budget
            """
        else:
            query = """
            SELECT 
                Kategorie.Kategorie, 
                Kategorie.Budget, 
                COALESCE(SUM(Haupt.Transaktion), 0) AS UsedBudget
            FROM Kategorie
            LEFT JOIN Haupt ON Kategorie.Kategorie_ID = Haupt.Kategorie_FK
            WHERE Kategorie.Kategorie = ? AND Kategorie.Budget > 0
            GROUP BY Kategorie.Kategorie_ID, Kategorie.Kategorie, Kategorie.Budget
            """
            # Kategorie als Parameter übergeben
            return self.db_manager.fetchall(query, (selected_category,))

        return self.db_manager.fetchall(query)
