from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from datetime import datetime


class TransactionWidget(QWidget):
    def __init__(self, name, category, amount, type_):
        super().__init__()

        # Styling für das Widget (grauer, abgerundeter Block)
        self.setStyleSheet(
            """
            background-color: #E0E0E0;  /* Hellgrau */
            border-radius: 10px;
            padding: 10px;
        """
        )

        # Hauptlayout des Blocks
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)  
        main_layout.setContentsMargins(10, 10, 10, 10) 

        # Linker Bereich: Name und Kategorie
        text_layout = QVBoxLayout()
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_label.setStyleSheet("color: black;")

        # Kategorie Label
        category_label = QLabel(category)
        category_label.setFont(QFont("Arial", 12))
        category_label.setStyleSheet("color: gray;")

        text_layout.addWidget(name_label)
        text_layout.addWidget(category_label)

        # Rechter Bereich: Betrag
        amount_label = QLabel(f"{amount:.2f} €")
        amount_label.setFont(QFont("Arial", 14, QFont.Bold))
        amount_label.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )  
        if type_ == 1:  # Einnahme
            amount_label.setStyleSheet("color: green;")
        else:  # Ausgabe
            amount_label.setStyleSheet("color: red;")

        # Elemente ins Hauptlayout einfügen
        main_layout.addLayout(text_layout)  
        main_layout.addWidget(amount_label)  

        # Hauptlayout setzen
        self.setLayout(main_layout)


class UebersichtView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setMinimumWidth(400)

        # Layout einrichten
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Header (Titel)
        title = QLabel("Übersicht der Transaktionen")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #004A94;")
        main_layout.addWidget(title)

        # Kontostand-Label
        self.balance_label = QLabel("Kontostand: 0 €")
        self.balance_label.setFont(QFont("Arial", 16))
        self.balance_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        main_layout.addWidget(self.balance_label)

        # Transaktionsliste
        self.transaction_list = QListWidget()
        self.transaction_list.setSelectionMode(
            QListWidget.SingleSelection
        )  # Nur ein Element kann ausgewählt werden
        self.transaction_list.setStyleSheet(
            """
            background-color: #FFFFFF; 
            border: none;
            selection-background-color: #B3D9FF;  /* Markierung bei Auswahl */
        """
        )
        self.transaction_list.setAlternatingRowColors(
            True
        )  
        main_layout.addWidget(self.transaction_list)

        # Layout anwenden
        self.setLayout(main_layout)

        # Initalisiere Kontostand
        self.balance = 0.0 

        # Lade Transaktionen und berechne den Kontostand
        self.load_transactions()

    def load_transactions(self):
        transactions = self.db_manager.fetch_transactions()
        self.transaction_list.clear()

        # Gruppiere Transaktionen nach Datum
        grouped_transactions = {}

        for trans in transactions:
            id, amount, name, category, type_, date = trans
            # Entferne den Zeitanteil, falls vorhanden
            date_obj = datetime.strptime(
                date.split(" ")[0], "%Y-%m-%d"
            )  # Nur das Datum ohne Zeit
            formatted_date = date_obj.strftime(
                "%d.%m.%Y"
            )  # Datum im Format "dd.mm.yyyy"

            if formatted_date not in grouped_transactions:
                grouped_transactions[formatted_date] = []

            grouped_transactions[formatted_date].append(trans)

        # Sortiere die Datumsgruppen absteigend
        sorted_dates = sorted(
            grouped_transactions.keys(),
            key=lambda x: datetime.strptime(x, "%d.%m.%Y"),
            reverse=True,
        )

        # Durchlaufe die gruppierten Transaktionen und füge sie zur Liste hinzu
        total_balance = 0.0  

        for date in sorted_dates:
            # Füge das Datum als Header hinzu
            date_header = QLabel(date)
            date_header.setFont(QFont("Arial", 16, QFont.Bold))
            date_header.setFixedHeight(40) 
            date_header.setAlignment(Qt.AlignCenter)  
            date_header.setStyleSheet(
                "color: #004A94; margin: 10px 0;"  
            )

            # Erstelle ein QListWidgetItem und füge das QLabel als Widget hinzu
            item = QListWidgetItem()
            item.setSizeHint(date_header.sizeHint())  
            item.setFlags(
                item.flags() & ~Qt.ItemIsSelectable & ~Qt.ItemIsEnabled
            )  # Deaktivieren von Auswahl und Interaktivität
            self.transaction_list.addItem(item)  
            self.transaction_list.setItemWidget(
                item, date_header
            )  # Setze das Datum als Widget
            item.setData(
                Qt.UserRole, "no-hover"
            )  

            # Füge Transaktionen unter dem Datum hinzu
            for trans in grouped_transactions[date]:
                id, amount, name, category, type_, date = trans

                # Erstelle das TransactionWidget für jede Transaktion
                transaction_widget = TransactionWidget(name, category, amount, type_)

                # Erstelle ein QListWidgetItem für die Transaktion
                item = QListWidgetItem()
                item.setSizeHint(
                    transaction_widget.sizeHint()
                ) 

                # Speichere die Transaktions-ID im Item
                item.setData(Qt.UserRole, id)

                # Füge das Widget zum Item hinzu
                self.transaction_list.addItem(item)
                self.transaction_list.setItemWidget(item, transaction_widget)

                # Berechne den Kontostand
                if type_ == 1:  # Einnahme
                    total_balance += amount
                else:  # Ausgabe
                    total_balance -= amount

            # Füge nach jeder Gruppe einen Abstand hinzu
            self.transaction_list.addItem(
                QListWidgetItem()
            )  # Leeres Item für den Abstand

        # Setze den aktuellen Kontostand
        self.balance_label.setText(f"Kontostand: {total_balance:.2f} €")

        # Ändere die Farbe des Kontostands basierend auf dem Wert
        if total_balance < 0:
            self.balance_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.balance_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

    # Funktion zum uptaden der Grafen
    def update_list(self):
        self.load_transactions()
        self.transaction_list.repaint()
