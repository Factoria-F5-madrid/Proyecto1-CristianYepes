import sqlite3
from db import Database

class AuthSystem:
	def __init__(self, db: Database):
		self.db = db

	def register(self):
		user = input("Usuario nuevo: ").strip()
		pwd  = input("Contraseña: ").strip()
		try:
			with self.db.conn:
				self.db.conn.execute(
					"INSERT INTO users(username, password) VALUES (?, ?)",
					(user, pwd)
				)
			print("✅ Usuario registrado")
			return user
		except sqlite3.IntegrityError:
			print("⚠️  Ese nombre ya existe")
			return None

	def login(self):
		user = input("Usuario: ").strip()
		pwd  = input("Contraseña: ").strip()
		row = self.db.conn.execute(
			"SELECT id FROM users WHERE username=? AND password=?",
			(user, pwd)
		).fetchone()
		if row:
			print(f"✅ Bienvenido, {user}")
			return user
		print("❌ Credenciales incorrectas")
		return None

	def login_menu(self):
		while True:
			opt = input("[l]ogin / [r]egistro / [q]uit: ").lower()
			if opt == "l":
				user = self.login()
				if user:
					return user
			elif opt == "r":
				user = self.register()
				if user:
					return user
			elif opt == "q":
				exit()
			else:
				print("Opción inválida")
