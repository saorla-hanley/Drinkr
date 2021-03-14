
import sqlite3
from flask import g
from datetime import datetime

DATABASE = 'rooms.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def add_room(key, password=""):
    print("Try to add room to database " + key)
    print(f"INSERT INTO rooms ([key],dateModified,password) VALUES ('{key}', '{datetime.today()}', '{password}'); ")
    query_db(f"INSERT INTO rooms ([key],dateModified,password) VALUES ('{key}', '{datetime.today()}', '{password}'); ")
    