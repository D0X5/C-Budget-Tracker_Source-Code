import sqlite3


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def fetch_transactions(self):
        """
        Holt alle Transaktionen aus der Tabelle 'Haupt' mit der Kategorie aus der Tabelle 'Kategorie' und das Datum.
        """
        query = """
        SELECT Haupt.ID, 
            Haupt.Transaktion, 
            Haupt.Name_Transaktion, 
            Kategorie.Kategorie, 
            CAST(Haupt.Ausgabe_Einnahme AS INTEGER),
            Haupt.Datum  -- Datum hinzufügen
        FROM Haupt
        LEFT JOIN Kategorie ON Haupt.Kategorie_FK = Kategorie.Kategorie_ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()  # Cursor lokal hier erstellen
            cursor.execute(query)
            return cursor.fetchall()

    def search_transactions(self, search_term):
        """
        Sucht Transaktionen nach Name, Kategorie, ID oder Datum.
        """
        query = """
        SELECT Haupt.ID, 
            Haupt.Transaktion, 
            Haupt.Name_Transaktion, 
            Kategorie.Kategorie, 
            CAST(Haupt.Ausgabe_Einnahme AS INTEGER),
            Haupt.Datum
        FROM Haupt
        LEFT JOIN Kategorie ON Haupt.Kategorie_FK = Kategorie.Kategorie_ID
        WHERE Haupt.Name_Transaktion LIKE ? 
        OR Kategorie.Kategorie LIKE ? 
        OR Haupt.ID LIKE ? 
        OR Haupt.Datum LIKE ?
        """
        # Suchbegriff für die SQL-Abfrage vorbereiten
        search_term = f"%{search_term}%"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (search_term, search_term, search_term, search_term))
            return cursor.fetchall()

    def fetch_expenses_per_category(self):
        """
        Holt die Summen der Ausgaben gruppiert nach Kategorien.
        """
        query = """
        SELECT Kategorie.Kategorie, 
               SUM(Haupt.Transaktion) 
        FROM Haupt
        LEFT JOIN Kategorie ON Haupt.Kategorie_FK = Kategorie.Kategorie_ID
        WHERE Haupt.Ausgabe_Einnahme = 0
        GROUP BY Kategorie.Kategorie
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()  # Cursor lokal hier erstellen
            cursor.execute(query)
            return cursor.fetchall()

    # Summe der Einnahmen pro Kategorie
    def execute(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()  # Änderungen explizit speichern
            return cursor
        except Exception as e:
            print(f"Fehler bei der Datenbankoperation: {e}")
            return None

    # Daten aus der Datenbank abfragen
    def fetchall(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Fehler bei der Datenbankabfrage: {e}")
            return []

    def add_transaction(self, data):
        """
        Fügt eine neue Transaktion in die Tabelle Transaktion ein.

        Args:
            data (dict): Ein Dictionary mit den Transaktionsdetails:
                - 'Transaktion' (int): Betrag der Transaktion
                - 'Name_Transaktion' (str): Name der Transaktion
                - 'Kategorie_FK' (int): ID der Kategorie (FK)
                - 'Ausgabe_Einnahme' (str): '0' für Ausgabe, '1' für Einnahme
                - 'Datum' (str): Das Datum der Transaktion im Format "yyyy-MM-dd"
        """
        query = """
        INSERT INTO Haupt (transaktion, name_transaktion, kategorie_fk, ausgabe_einnahme, datum)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            data["Transaktion"],
            data["Name_Transaktion"],
            data["Kategorie_FK"],
            data["Ausgabe_Einnahme"],
            data["Datum"],  
        )

        try:
            self.execute(query, params)
            print("Transaktion erfolgreich hinzugefügt.")
            return True  # Erfolgreich hinzugefügt
        except Exception as e:
            print(f"Fehler beim Hinzufügen der Transaktion: {e}")
            return False  # Fehler beim Hinzufügen


    # Transaktion anhand der ID abrufen
    def fetch_transaction_by_id(self, transaction_id):
        query = """
        SELECT ID, Transaktion, Name_Transaktion, Kategorie_FK, Ausgabe_Einnahme, Datum
        FROM Haupt
        WHERE ID = ?
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (transaction_id,))
            result = cursor.fetchone()
            if result:
                return {
                    "ID": result[0],
                    "Transaktion": result[1],
                    "Name_Transaktion": result[2],
                    "Kategorie_FK": result[3],
                    "Ausgabe_Einnahme": result[4],
                    "Datum": result[5],
                }
            return None

    # Transaktion in der Datenbank aktualisieren
    def update_transaction(self, transaction_id, data):
        query = """
            UPDATE Haupt
            SET Transaktion = ?, Name_Transaktion = ?, Kategorie_FK = ?, Ausgabe_Einnahme = ?, Datum = ?
            WHERE id = ?
        """
        params = (
            data["Transaktion"],
            data["Name_Transaktion"],
            data["Kategorie_FK"],
            data["Ausgabe_Einnahme"],
            data["Datum"],
            transaction_id,
        )
        self.execute(query, params)

    def close(self):
        self.connection.close()
