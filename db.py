import sqlite3
import logging
from datetime import datetime

class Database:
	def __init__(self, file="taximetro.db"):
		self.conn = sqlite3.connect(file, check_same_thread=False)
		self.create_tables()

	def create_tables(self):
		with self.conn:
			self.conn.execute(
				"CREATE TABLE IF NOT EXISTS users ("
				"id INTEGER PRIMARY KEY AUTOINCREMENT,"
				"username TEXT UNIQUE NOT NULL,"
				"password TEXT NOT NULL)"
			)
			self.conn.execute(
				"CREATE TABLE IF NOT EXISTS trips ("
				"id INTEGER PRIMARY KEY AUTOINCREMENT,"
				"user_id INTEGER NOT NULL,"
				"date TEXT,"
				"stop_time REAL,"
				"move_time REAL,"
				"total REAL,"
				"FOREIGN KEY(user_id) REFERENCES users(id))"
			)
			self.conn.execute(
				"CREATE TABLE IF NOT EXISTS logs ("
				"id INTEGER PRIMARY KEY AUTOINCREMENT,"
				"timestamp TEXT,"
				"level TEXT,"
				"message TEXT)"
			)

class DBLogHandler(logging.Handler):
	def __init__(self, db: "Database"):
		super().__init__()
		self.db = db

	def emit(self, record):
		ts = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
		with self.db.conn:
			self.db.conn.execute(
				"INSERT INTO logs(timestamp, level, message) VALUES (?, ?, ?)",
				(ts, record.levelname, record.getMessage())
			)
