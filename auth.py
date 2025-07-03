import os

class AuthSystem:
	def __init__(self, filename="usuarios.txt"):
		self.filename = filename
		self.users = {}
		self.load_users()

	def load_users(self):
		if not os.path.exists(self.filename):
			with open(self.filename, "w", encoding="utf-8") as f:
				pass  # crea el archivo vacío
		with open(self.filename, "r", encoding="utf-8") as f:
			for line in f:
				if ":" in line:
					user, pwd = line.strip().split(":", 1)
					self.users[user] = pwd

	def save_users(self):
		with open(self.filename, "w", encoding="utf-8") as f:
			for user, pwd in self.users.items():
				f.write(f"{user}:{pwd}\n")

	def register(self):
		print("\n=== Registro de nuevo usuario ===")
		while True:
			username = input("Nombre de usuario: ").strip()
			if username in self.users:
				print("⚠️  Ese usuario ya existe. Prueba con otro.")
			elif ":" in username or username == "":
				print("⚠️  Nombre inválido. No puede contener ':' ni estar vacío.")
			else:
				break
		while True:
			password = input("Contraseña: ").strip()
			if ":" in password or password == "":
				print("⚠️  Contraseña inválida. No puede contener ':' ni estar vacía.")
			else:
				break
		self.users[username] = password
		self.save_users()
		print(f"✅ Usuario '{username}' registrado con éxito.")
		return username

	def login(self):
		print("\n=== Inicio de sesión ===")
		for _ in range(3):
			username = input("Usuario: ").strip()
			password = input("Contraseña: ").strip()
			if self.users.get(username) == password:
				print(f"✅ Bienvenido, {username}.")
				return username
			else:
				print("❌ Usuario o contraseña incorrectos.")
		print("🚫 Demasiados intentos fallidos.")
		return None

	def login_menu(self):
		print("\n🚖 Bienvenido al sistema Taxímetro.")
		while True:
			option = input("¿Quieres [l]ogin, [r]egistrarte o [q]uit? ").lower()
			if option == "l":
				user = self.login()
				if user:
					return user
			elif option == "r":
				user = self.register()
				return user
			elif option == "q":
				print("👋 Hasta luego.")
				exit()
			else:
				print("Opción no reconocida. Usa l / r / q.")
