from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QDoubleSpinBox,
    QLabel,
    QMessageBox,
)
from PySide6.QtCore import Qt


class CategoryEditDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Kategorien Bearbeiten")
        self.resize(400, 300)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Kategorie Liste
        self.category_list = QListWidget()
        self.category_list.itemSelectionChanged.connect(self.on_category_selected)
        self.layout.addWidget(self.category_list)

        # Bearbeitungsfelder
        self.name_edit = QLineEdit()
        self.budget_edit = QDoubleSpinBox()
        self.budget_edit.setPrefix("€ ")
        self.budget_edit.setMaximum(1_000_000)  # Maximalwert für das Budget

        # Labels für die Bearbeitungsfelder
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Kategorie Name:"))
        form_layout.addWidget(self.name_edit)
        form_layout.addWidget(QLabel("Budget:"))
        form_layout.addWidget(self.budget_edit)
        self.layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Speichern")
        self.save_button.clicked.connect(self.save_category)
        button_layout.addWidget(self.save_button)

        self.add_button = QPushButton("Kategorie Hinzufügen")
        self.add_button.clicked.connect(self.add_category)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Löschen")
        self.delete_button.clicked.connect(self.delete_category)
        button_layout.addWidget(self.delete_button)

        self.layout.addLayout(button_layout)

        # Kategorien laden
        self.load_categories()

        self.category_list.itemSelectionChanged.connect(self.on_category_selected)

    def load_categories(self):
        """Lade Kategorien aus der Datenbank und zeige sie in der Liste an."""
        query = "SELECT Kategorie_ID, Kategorie, Budget FROM Kategorie"
        cursor = self.db_manager.execute(query)
        categories = cursor.fetchall() if cursor else []

        # Kategorie-Liste leeren
        self.category_list.clear()

        # Füge alle Kategorien zur Liste hinzu
        for cat_id, name, budget in categories:
            # Fallback für None-Werte im Budget
            budget = budget if budget is not None else 0.0

            # Erstelle Listeneintrag ohne Überschreiben
            item = QListWidgetItem(f"{name} - € {budget:.2f}")
            item.setData(Qt.UserRole, {"id": cat_id, "name": name, "budget": budget})
            self.category_list.addItem(item)  # Kategorie hinzufügen

        print(f"{len(categories)} Kategorien wurden geladen.")  

    def on_category_selected(self):
        """Zeige die Details der ausgewählten Kategorie in den Bearbeitungsfeldern."""
        selected_item = self.category_list.currentItem()
        if not selected_item:
           
            self.name_edit.clear()
            self.budget_edit.setValue(0.0)
            return

        # Hole die gespeicherten Daten des ausgewählten Elements
        category_data = selected_item.data(Qt.UserRole)
        self.name_edit.setText(category_data["name"])
        self.budget_edit.setValue(category_data["budget"])

    def save_category(self):
        """Speichere Änderungen an der ausgewählten Kategorie."""
        selected_item = self.category_list.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self, "Keine Auswahl", "Bitte wählen Sie eine Kategorie aus."
            )
            return

        category_data = selected_item.data(Qt.UserRole)
        category_id = category_data["id"]
        new_name = (
            self.name_edit.text().strip()
        ) 
        new_budget = self.budget_edit.value()

        # Validierung des Namens
        if not new_name:
            QMessageBox.critical(
                self,
                "Ungültiger Name",
                "Bitte geben Sie einen gültigen Kategorienamen ein.",
            )
            return

        # Update der Kategorie in der Datenbank
        query = "UPDATE Kategorie SET Kategorie = ?, Budget = ? WHERE Kategorie_ID = ?"
        self.db_manager.execute(query, (new_name, new_budget, category_id))
        self.db_manager.connection.commit()

        # Aktualisiere die Liste und schließe den Dialog
        self.load_categories()
        self.accept()

    def add_category(self):
        """Füge eine neue Kategorie hinzu."""
        new_name = self.name_edit.text().strip()
        new_budget = self.budget_edit.value()

        # Validierung des Namens
        if not new_name:
            QMessageBox.critical(
                self,
                "Ungültiger Name",
                "Bitte geben Sie einen gültigen Kategorienamen ein.",
            )
            return

        # Überprüfung, ob der Kategoriename bereits existiert
        query_check = "SELECT COUNT(*) FROM Kategorie WHERE Kategorie = ?"
        result = self.db_manager.execute(query_check, (new_name,)).fetchone()

        if result and result[0] > 0:  # Wenn die Kategorie bereits existiert
            QMessageBox.critical(
                self,
                "Kategorie existiert bereits",
                f"Die Kategorie '{new_name}' existiert bereits.",
            )
            return

        # Neue Kategorie in die Datenbank einfügen
        query_insert = "INSERT INTO Kategorie (Kategorie, Budget) VALUES (?, ?)"
        self.db_manager.execute(query_insert, (new_name, new_budget))
        self.db_manager.connection.commit()

        # Aktualisiere die Liste und schließe den Dialog
        self.load_categories()
        self.accept()

    def delete_category(self):
        """Lösche die ausgewählte Kategorie."""
        selected_item = self.category_list.currentItem()
        if not selected_item:
            QMessageBox.warning(
                self, "Keine Auswahl", "Bitte wählen Sie eine Kategorie aus."
            )
            return

        category_data = selected_item.data(Qt.UserRole)
        category_id = category_data["id"]

        # Löschoperation bestätigen
        confirm = QMessageBox.question(
            self,
            "Kategorie Löschen",
            f"Sind Sie sicher, dass Sie die Kategorie '{category_data['name']}' löschen möchten?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.No:
            return

        # Lösche die Kategorie aus der Datenbank
        query = "DELETE FROM Kategorie WHERE Kategorie_ID = ?"
        self.db_manager.execute(query, (category_id,))
        self.db_manager.connection.commit()

        # Aktualisiere die Liste
        self.load_categories()
        QMessageBox.information(self, "Gelöscht", "Kategorie wurde gelöscht.")
