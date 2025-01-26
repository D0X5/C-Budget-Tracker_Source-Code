from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QCalendarWidget,
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt
from datetime import datetime
from Features.Übersicht.view import TransactionWidget


class SuchleisteView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Suchfenster")
        self.setMinimumSize(1500, 800)
        self.showMaximized

        layout = QVBoxLayout()

        # Suchleisten Design
        title = QLabel("Suchleiste")
        title.setFont(QFont("Arial", 18, QFont.Bold))  
        title.setStyleSheet("color: #004A94;")  
        layout.addWidget(title)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suchbegriff eingeben...")
        layout.addWidget(self.search_input)

        # Suchbutton
        search_button = QPushButton("Suchen")
        search_button.clicked.connect(self.search_transactions)
        layout.addWidget(search_button)

        # Ergebnis Liste
        self.result_list = QListWidget()
        layout.addWidget(self.result_list)

        # Kalender Widget 
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.on_date_selected)
        layout.addWidget(self.calendar)

        self.setLayout(layout)


    # Suchfunktion
    def search_transactions(self):
        search_term = self.search_input.text()

        transactions = self.db_manager.search_transactions(search_term)

        self.result_list.clear()

        # Gruppiere die Transaktionen nach Datum
        grouped_transactions = {}
        for trans in transactions:
            id, amount, name, category, type_, date = trans
            date_obj = datetime.strptime(
                date, "%Y-%m-%d"
            )  # Datum in datetime-Objekt umwandeln
            formatted_date = date_obj.strftime(
                "%d.%m.%Y"
            )  # Formatierung: Tag.Monat.Jahr

            # Gruppiere Transaktionen nach Datum
            if formatted_date not in grouped_transactions:
                grouped_transactions[formatted_date] = []
            grouped_transactions[formatted_date].append((name, category, amount, type_))

        # Füge die gruppierten Transaktionen zur Ergebnisliste hinzu
        for date, transactions_on_date in grouped_transactions.items():
            # Füge das Datum als Header hinzu
            date_header = QListWidgetItem(date)
            date_header.setFont(QFont("Arial", 14, QFont.Bold))
            date_header.setBackground(QColor("#D3D3D3"))
            date_header.setTextAlignment(Qt.AlignCenter)
            self.result_list.addItem(date_header)

            # Füge jede Transaktion unter dem Datum hinzu
            for name, category, amount, type_ in transactions_on_date:
                transaction_widget = TransactionWidget(name, category, amount, type_)

                item = QListWidgetItem()
                item.setSizeHint(transaction_widget.sizeHint())
                self.result_list.addItem(item)
                self.result_list.setItemWidget(item, transaction_widget)

    # Funktion die aufgerufen wird, wenn Datum im Kalender ausgewählt wird
    def on_date_selected(self):
        # Wenn ein Datum im Kalender ausgewählt wird
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")

        # Suche Transaktionen für das ausgewählte Datum
        transactions = self.db_manager.search_transactions(selected_date)

        # Transaktionen anzeigen
        self.result_list.clear()
        for trans in transactions:
            id, amount, name, category, type_, date = trans
            date_obj = datetime.strptime(
                date, "%Y-%m-%d"
            )  # Datum in datetime-Objekt umwandeln
            formatted_date = date_obj.strftime(
                "%d.%m.%Y"
            )  # Formatierung: Tag.Monat.Jahr

            # Erstelle das TransactionWidget mit den Transaktionsdetails
            transaction_widget = TransactionWidget(name, category, amount, type_)

            # Erstelle das QListWidgetItem und füge das Widget hinzu
            item = QListWidgetItem()
            item.setSizeHint(transaction_widget.sizeHint())
            self.result_list.addItem(item)
            self.result_list.setItemWidget(item, transaction_widget)
