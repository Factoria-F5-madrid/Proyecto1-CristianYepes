import sqlite3
from datetime import datetime
from db import Database

class TripRepository:
	def __init__(self, db: Database, user: str):
		self.db   = db
		self.user = user

	def _user_id(self):
		row = self.db.conn.execute(
			"SELECT id FROM users WHERE username=?", (self.user,)
		).fetchone()
		return row[0]

	def save(self, stop_time: float, move_time: float, total: float):
		with self.db.conn:
			self.db.conn.execute(
				"INSERT INTO trips(user_id, date, stop_time, move_time, total) "
				"VALUES (?, ?, ?, ?, ?)",
				(self._user_id(),
				 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
				 stop_time, move_time, total)
			)

	def clear(self):
		with self.db.conn:
			self.db.conn.execute("DELETE FROM trips")
