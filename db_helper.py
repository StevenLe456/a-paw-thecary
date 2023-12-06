import pandas as pd
from sqlalchemy import create_engine
import sqlglot
import sqlite3

def create_table(csv_path, schema, db_path, table_name):
    df = pd.read_csv(csv_path, index_col=0, dtype=schema)
    engine = create_engine(f"sqlite:///{db_path}")
    df.to_sql(table_name, con=engine)

def clear_db(db_path):
    TABLE_PARAMETER = "{TABLE_PARAMETER}"
    DROP_TABLE_SQL = f"DROP TABLE {TABLE_PARAMETER};"
    GET_TABLES_SQL = "SELECT name FROM sqlite_schema WHERE type='table';"
    con = sqlite3.connect(db_path)
    def get_tables(con):
        cur = con.cursor()
        cur.execute(GET_TABLES_SQL)
        tables = cur.fetchall()
        cur.close()
        return tables
    def delete_tables(con, tables):
        cur = con.cursor()
        for table, in tables:
            sql = DROP_TABLE_SQL.replace(TABLE_PARAMETER, table)
            cur.execute(sql)
        cur.close()
    tables = get_tables(con)
    delete_tables(con, tables)

#TODO: add commit functionality, error handling, and SQL scrubbing
def run_sql(db_path, tsql):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    sql = sqlglot.transpile(tsql, read="tsql", write="sqlite")[0]
    return cur.execute(sql).fetchall(), [description[0] for description in cur.description]