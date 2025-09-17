import psycopg2
from abc import ABC, abstractmethod

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = psycopg2.connect(
                dbname='postgres',
                user='postgres',
                password='qwe123',
                host='localhost',
                port='5432'
            )
        return cls._instance

    def get_connection(self):
        return self.connection

class AbstractDatabase(ABC):
    def __init__(self):
        self.conn = DatabaseConnection().get_connection()
        self.cursor = self.conn.cursor()

    @abstractmethod
    def fetch_all(self):
        pass

    @abstractmethod
    def insert(self, *args):
        pass

    def close(self):
        self.cursor.close()
        self.conn.close()


class IdojarasDatabase(AbstractDatabase):
    def fetch_all(self):
        self.cursor.execute("SELECT * FROM idojaras")
        return self.cursor.fetchall()

    def insert(self, varos, homerseklet, paratartalom, szelsebesseg):
        self.cursor.execute(
            "INSERT INTO idojaras"
            "(varos, homerseklet, paratartalom, szelsebesseg)"
            " VALUES (%s, %s, %s, %s)",
            (varos, homerseklet, paratartalom, szelsebesseg)
        )
        self.conn.commit()

    def fetch_by_varos(self, varos):
        self.cursor.execute("SELECT * FROM idojaras WHERE varos = %s", (varos,))
        return self.cursor.fetchall()

    def delete(self, id):
        self.cursor.execute("DELETE FROM idojaras WHERE id = %s", (id,))
        self.conn.commit()

    def update_temperature(self, id, new_temp):
        self.cursor.execute(
            "UPDATE idojaras SET homerseklet = %s WHERE id = %s",
            (new_temp, id)
        )
        self.conn.commit()

    def fetch_by_temperature_range(self, min_temp, max_temp):
        self.cursor.execute(
            "SELECT * FROM idojaras WHERE homerseklet BETWEEN %s AND %s",
            (min_temp, max_temp)
        )
        return self.cursor.fetchall()

    def fetch_by_wind_speed(self, min_speed):
        self.cursor.execute("SELECT * FROM idojaras WHERE szelsebesseg >= %s", (min_speed,))
        return self.cursor.fetchall()

    def fetch_ordered_by_date(self, descending=True):
        order = 'DESC' if descending else 'ASC'
        self.cursor.execute(f"SELECT * FROM idojaras ORDER BY datum {order}")
        return self.cursor.fetchall()

    def count_records(self):
        self.cursor.execute("SELECT COUNT(*) FROM idojaras")
        return self.cursor.fetchone()[0]

    def average_temperature(self):
        self.cursor.execute("SELECT AVG(homerseklet) FROM idojaras")
        return self.cursor.fetchone()[0]

    def max_humidity(self):
        self.cursor.execute("SELECT MAX(paratartalom) FROM idojaras")
        return self.cursor.fetchone()[0]


class SearchStrategy(ABC):
    @abstractmethod
    def search(self, cursor, param):
        pass


class SearchByTemperature(SearchStrategy):
    def search(self, cursor, min_temp):
        cursor.execute(
            "SELECT * FROM idojaras"
            " WHERE homerseklet >= %s", (min_temp,)
        )
        return cursor.fetchall()


class SearchByHumidity(SearchStrategy):
    def search(self, cursor, max_humidity):
        cursor.execute(
            "SELECT * FROM idojaras"
            " WHERE paratartalom <= %s", (max_humidity,)
        )
        return cursor.fetchall()


def main():
    db = IdojarasDatabase()

    db.insert('Miskolc', 12.5, 80, 5.2)

    print("Összes adat:", db.fetch_all())

    print("Debrecen adatai:", db.fetch_by_varos('Debrecen'))

    db.update_temperature(2, 18.0)
    print("Frissített adatok (ID=2):", db.fetch_by_varos('Debrecen'))

    print("16-19°C közötti adatok:", db.fetch_by_temperature_range(16.0, 19.0))

    print("Legalább 9.0 m/s szélsebesség:", db.fetch_by_wind_speed(9.0))

    print("Dátum szerint csökkenő sorrendben:", db.fetch_ordered_by_date(descending=True))

    print("Rekordok száma:", db.count_records())

    print("Átlag hőmérséklet:", db.average_temperature())

    print("Legnagyobb páratartalom:", db.max_humidity())

    search_strategy = SearchByTemperature()
    print("Stratégia: Legalább 16.0°C:", search_strategy.search(db.cursor, 16.0))

    search_strategy = SearchByHumidity()
    print("Stratégia: Legfeljebb 60% páratartalom:", search_strategy.search(db.cursor, 60))

    db.delete(1)
    print("Adatok rekord törlése után:", db.fetch_all())

    db.close()


main()
