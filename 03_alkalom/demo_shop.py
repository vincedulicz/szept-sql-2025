import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import DictCursor
from abc import ABC, abstractmethod


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        """
        env nélküli megközelítés

        dbname="postgres",
        user="postgres",
        password="qwe123",
        host='localhost',
        port=5432
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME", "postgres"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DP_PASSWORD", "qwe123"),
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=os.getenv("DB_PORT", "5432"),
                cursor_factory=DictCursor
            )
        return cls._instance

    def get_cursor(self):
        return self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()
            DatabaseConnection._instance = None


class QueryStrategy(ABC):
    @abstractmethod
    def execute(self, cursor, *args):
        pass


class DatabaseHandler:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cursor = self.db.get_cursor()

    def execute_query(self, strategy: QueryStrategy, *args):
        try:
            result = strategy.execute(self.cursor, *args)
            self.db.conn.commit()
            return result
        except Exception as e:
            self.db.conn.rollback()
            print(f'Hiba: {e}')
            return None

    def __del__(self):
        self.cursor.close()
        self.db.close()


class GetOrdersWithCustomerAndShop(QueryStrategy):
    def execute(self, cursor, *args):
        query = sql.SQL("""
            SELECT o.order_id, o.order_date, c.name AS customer_name, 
                   s.name AS shop_name, o.total_amount
            FROM orders o
            INNER JOIN customer c ON o.customer_id = c.customer_id
            INNER JOIN shop s ON o.shop_id = s.shop_id;
        """)
        cursor.execute(query)
        return cursor.fetchall()


class GetTopCustomer(QueryStrategy):
    def execute(self, cursor, *args):
        query = sql.SQL("""
            SELECT c.name, SUM(o.total_amount) AS total_spent
            FROM customer c
            INNER JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.name
            ORDER BY total_spent DESC
            LIMIT 1;
        """)
        cursor.execute(query)
        return cursor.fetchone()


class GetShopStockSummary(QueryStrategy):
    def execute(self, cursor, *args):
        query = sql.SQL("""
            WITH ProductCount AS (
                SELECT shop_id, SUM(stock) AS total_stock 
                FROM product
                GROUP BY shop_id
            )
            SELECT s.shop_id, s.name AS shop_name, pc.total_stock
            FROM shop s
            LEFT JOIN ProductCount pc ON s.shop_id = pc.shop_id;
        """)
        cursor.execute(query)
        return cursor.fetchall()


class GetOrderServiceReport(QueryStrategy):
    def execute(self, cursor, *args):
        query = sql.SQL("""
            SELECT o.order_id, c.name AS customer_name, s.name AS shop_name, 
                   p.product_name, e.name AS service_employee, 
                   o.order_date, o.total_amount
            FROM orders o
            INNER JOIN customer c ON o.customer_id = c.customer_id
            INNER JOIN shop s ON o.shop_id = s.shop_id
            INNER JOIN orderitem oi ON o.order_id = oi.order_id
            INNER JOIN product p ON oi.product_id = p.product_id
            LEFT JOIN customerserviceticket t ON c.customer_id = t.customer_id
            LEFT JOIN employee e ON t.employee_id = e.employee_id;
        """)
        cursor.execute(query)
        return cursor.fetchall()


def main():
    # TODO: for for for
    handler = DatabaseHandler()

    print("\nRendelések ügyfél és bolt adatokkal\n")
    orders = handler.execute_query(GetOrdersWithCustomerAndShop())
    for row in orders:
        print(dict(row))

    print("\nLegtöbbet költő ügyfél\n")
    top_customer = handler.execute_query(GetTopCustomer())
    print(dict(top_customer))

    print("\nBolt készlet összesítése\n")
    stock = handler.execute_query(GetShopStockSummary())
    for row in stock:
        print(dict(row))

    print("\nKomplex riport\n")
    report = handler.execute_query(GetOrderServiceReport())
    for row in report:
        print(dict(row))


main()
