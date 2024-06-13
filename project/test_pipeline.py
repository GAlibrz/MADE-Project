import os
import sqlite3

def test_pipeline():
    db_path = "../data/stocks_temp.db"

    os.system("python3 csv2db.py")

    # Test1: Check if the SQLite database file was created
    print("test1: Check if the SQLite database file was created")
    assert os.path.exists(db_path), "Database file not found."
    print('Passed')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Test2: Check if the expected tables are in the database
    print("Test2: Check if the expected tables are in the database")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    expected_tables = [('stocks',), ('tempreture',)]
    for table in expected_tables:
        assert table in tables, f"Table {table[0]} not found in the database."
    print('Passed')

    # Test3: Check if the stocks table has data
    print("Test3: Check if the stocks table has data")
    cursor.execute("SELECT COUNT(*) FROM stocks;")
    stocks_count = cursor.fetchone()[0]
    assert stocks_count > 0, "No data found in the stocks table."
    print('Passed')

    # Test4: Check if the tempreture table has data
    print("Test4: Check if the tempreture table has data")
    cursor.execute("SELECT COUNT(*) FROM tempreture;")
    tempreture_count = cursor.fetchone()[0]
    assert tempreture_count > 0, "No data found in the tempreture table."
    print("Passed")

    # Test5: Check if the number of the rows in both tables match
    print("Test5: Check if the number of the rows in both tables match")
    assert stocks_count == tempreture_count, "Number of rows in stocks and temprature don't match"
    print("Passed")

    conn.close()
    print("All tests passed successfully.")

if __name__ == "__main__":
    test_pipeline()
