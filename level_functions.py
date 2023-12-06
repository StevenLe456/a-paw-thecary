import db_helper as dbh

def lvl_1():
    dbh.clear_db("assets/db/game.db")
    dbh.create_table("assets/csv/inventory.csv", {"ID": int, "NAME": str, "NUM": int}, "assets/db/game.db", "INVENTORY")