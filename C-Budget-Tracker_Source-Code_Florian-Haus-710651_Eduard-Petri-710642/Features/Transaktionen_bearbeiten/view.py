from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QLabel,
    QDateEdit,
    QMessageBox,
)
from PySide6.QtCore import QDate


class TransactionDialog(QDialog):
    def __init__(self, title, db_manager, transaction_data=None):
        super().__init__()
        self.setWindowTitle(title)
        self.db_manager = db_manager
        self.transaction_data = transaction_data

        layout = QVBoxLayout()
        # QLabel und Eingabefeld für "Name der Transaktion" mit Farbe und Stil
        self.name_input = QLineEdit()
        label = QLabel("Name der Transaktion:")
        label.setStyleSheet(
            "color: #004A94; font-weight: bold;"
        )  # Farbe und Stil ändern
        layout.addWidget(label)
        layout.addWidget(self.name_input)
        self.name_input.setPlaceholderText("(z.B. Miete)")

        self.amount_input = QLineEdit()

        # Neues QLabel für "Betrag"
        amount_label = QLabel("Betrag:")
        amount_label.setStyleSheet(
            "color: #004A94; font-weight: bold;"
        )  # Farbe und Stil ändern
        layout.addWidget(amount_label)  # Das angepasste Label zum Layout hinzufügen

        # Eingabefeld für Betrag
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText(
            "(z.B. 10.99 oder 10)"
        )  # Platzhaltertext für Betrag

        layout.addWidget(self.amount_input)

        # Kategorie Auswahl in ComboBox
        self.category_input = QComboBox()
        self.populate_categories()  # Kategorien aus der Datenbank laden

        # Neues Label für "Kategorie" mit Farbe und Stil
        category_label = QLabel("Kategorie:")
        category_label.setStyleSheet(
            "color: #004A94; font-weight: bold;"
        )  
        layout.addWidget(category_label)
        layout.addWidget(self.category_input)

        # Typ (Ausgabe/Einnahme) in ComboBox
        self.type_input = QComboBox()
        self.type_input.addItems(["Ausgabe", "Einnahme"])  # '0' oder '1'

        # Neues Label für "Typ (Ausgabe/Einnahme)" mit Farbe und Stil
        type_label = QLabel("Typ (Ausgabe/Einnahme):")
        type_label.setStyleSheet("color: #004A94; font-weight: bold;")  
        layout.addWidget(type_label)
        layout.addWidget(self.type_input)

        # Datum Eingabe
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        # Neues Label für "Datum" mit Farbe und Stil
        date_label = QLabel("Datum:")
        date_label.setStyleSheet("color: #004A94; font-weight: bold;") 
        layout.addWidget(date_label)
        layout.addWidget(self.date_input)

        # Speichern-Button
        self.save_button = QPushButton("Speichern")
        self.save_button.clicked.connect(self.save_transaction)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        if transaction_data:
            self.fill_data()

    # Kategorien aus Datenbank laden
    def populate_categories(self):
        
        query = "SELECT Kategorie_ID, Kategorie FROM Kategorie"
        cursor = self.db_manager.execute(query)

        if cursor is None:
            print("Fehler: Kategorien konnten nicht geladen werden.")
            return

        categories = cursor.fetchall()
        for category_id, category_name in categories:
            self.category_input.addItem(category_name, category_id)

    # Daten aus der Datenbank in die Eingabefelder einfügen
    def fill_data(self):
        self.name_input.setText(self.transaction_data[2])  # Name_Transaktion
        self.amount_input.setText(str(self.transaction_data[1]))  # Transaktion (Betrag)
        self.category_input.setCurrentIndex(
            self.category_input.findData(self.transaction_data[3])  # Kategorie_FK
        )
        self.type_input.setCurrentIndex(
            0 if self.transaction_data[4] == 0 else 1
        )  # Ausgabe_Einnahme
        self.date_input.setDate(
            QDate.fromString(self.transaction_data[5], "yyyy-MM-dd")
        )  # Datum

    # Transaktion speichern
    def save_transaction(self):
        datum = self.date_input.date().toString("yyyy-MM-dd")

        # Validierung des Betrags
        amount_text = self.amount_input.text()
        try:
            amount = float(amount_text)
        except ValueError:
            QMessageBox.critical(
                self, "Ungültiger Betrag", "Bitte geben Sie einen gültigen Betrag ein."
            )
            return

        # Überprüfe, ob der Betrag negativ ist
        if amount < 0:
            QMessageBox.critical(
                self, "Ungültiger Betrag", "Der Betrag kann nicht negativ sein."
            )
            return

        # Validierung des Namens
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.critical(
                self,
                "Ungültiger Name",
                "Bitte geben Sie einen Namen für die Transaktion ein.",
            )
            return

        # Daten für die Spedicherung der Transaktion
        data = {
            "Transaktion": amount,
            "Name_Transaktion": name,
            "Kategorie_FK": self.category_input.currentData(),
            "Ausgabe_Einnahme": "0" if self.type_input.currentIndex() == 0 else "1",
            "Datum": datum,
        }

        # Unterscheidung: Neue Transaktion oder Bearbeitung
        if self.transaction_data:
            transaction_id = self.transaction_data[
                0
            ]  # Die ID der Transaktion (aus dem Tuple)
            self.db_manager.update_transaction(transaction_id, data)
        else:
            self.db_manager.add_transaction(data)

        self.accept()  # Schließt den Dialog nach erfolgreichem Speichern
