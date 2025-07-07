import sqlite3
from datetime import datetime
from db import Database

class TripRepository:
	def __init__(self, db: Database, user: str):
		self.db = db
		self.user = user

	def _user_id(self):
		row = self.db.conn.execute(
			"SELECT id FROM users WHERE username=?", (self.user,)
		).fetchone()
		if not row:
			raise ValueError(f"Usuario '{self.user}' no existe en la base de datos")
		return row[0]

	def save(self, stop_time: float, move_time: float, total: float):
		with self.db.conn:
			self.db.conn.execute(
				"INSERT INTO trips(user_id, date, stop_time, move_time, total) "
				"VALUES (?, ?, ?, ?, ?)",
				(
					self._user_id(),
					datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
					stop_time,
					move_time,
					total
				)
			)

	def clear(self):
		with self.db.conn:
			self.db.conn.execute("DELETE FROM trips")

	def list_all(self):
		uid = self._user_id()
		cur = self.db.conn.execute(
			"SELECT id, date, stop_time, move_time, total FROM trips "
			"WHERE user_id=? ORDER BY id DESC",
			(uid,)
		)
		rows = cur.fetchall()
		return [
			{
				"id": row[0],
				"date": row[1],
				"stop_time": row[2],
				"move_time": row[3],
				"total": row[4]
			}
			for row in rows
		]
