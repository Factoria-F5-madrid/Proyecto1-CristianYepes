import datetime
import logging
import threading
import time
import pytest
import os

from auth import AuthSystem
from logsetup import get_app_logger

COLOR_CYAN = "\033[96m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_PURPLE = "\033[95m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"


class Trip:
	def __init__(self, logger: logging.Logger, stop_rate: float, move_rate: float):
		self.log = logger
		self.stop_rate = stop_rate
		self.move_rate = move_rate
		self.total = 0.0
		self.state = "stop"
		self.start_time = time.perf_counter()
		self.stop_time = 0.0
		self.move_time = 0.0
		self.lock = threading.Lock()

	def _accumulate_elapsed(self):
		now = time.perf_counter()
		elapsed = now - self.start_time
		if self.state == "stop":
			self.stop_time += elapsed
		else:
			self.move_time += elapsed
		self.start_time = now

	def toggle_state(self):
		with self.lock:
			self._accumulate_elapsed()
			self.state = "move" if self.state == "stop" else "stop"
			self.log.info(f"Estado cambiado a {self.state}")

	def finish(self):
		with self.lock:
			self._accumulate_elapsed()
			self.total = self.stop_time * self.stop_rate + self.move_time * self.move_rate
			self.log.info(
				f"Viaje cerrado | stop={self.stop_time:.2f}s move={self.move_time:.2f}s total=€{self.total:.2f}"
			)
			self.log.info("------------------------------")
			return self.stop_time, self.move_time, self.total

class FileTripHistory:
	def __init__(self, logger: logging.Logger, username, filename="historial_viajes.txt"):
		self.filename = filename
		self.username = username
		self.log = logger
		self.next_id = self._get_next_id()

	def _get_next_id(self):
		if not os.path.exists(self.filename):
			return 1
		with open(self.filename, "r", encoding="utf-8") as f:
			ids = [int(line.strip().split(":")[1])
				   for line in f if line.startswith("ID:")]
			return max(ids, default=0) + 1

	def save(self, stop_time, move_time, total):
		with open(self.filename, "a", encoding="utf-8") as f:
			print("----- Viaje finalizado -----", file=f)
			print(f"ID: {self.next_id}", file=f)
			print(f"Usuario: {self.username}", file=f)
			print(f"Fecha y hora: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}", file=f)
			print(f"Tiempo detenido: {stop_time:.2f} segundos", file=f)
			print(f"Tiempo en marcha : {move_time:.2f} segundos", file=f)
			print(f"Total a pagar   : €{total:.2f}", file=f)
			print("------------------------------\n", file=f)
		self.log.debug(f"Trayecto guardado en historial con ID {self.next_id}")
		self.next_id += 1

	def clear(self):
		open(self.filename, "w", encoding="utf-8").close()
		self.log.debug("Historial de viajes vaciado")


class ConsoleView:
	@staticmethod
	def print_welcome():
		print(COLOR_CYAN + "*" * 50)
		print(COLOR_CYAN + "{:^50}".format("Bienvenido a Taximetro F5") + COLOR_RESET)
		print(COLOR_CYAN + "*" * 50 + COLOR_RESET)
		print(
			"Comandos:\n"
			" start  - Iniciar nuevo viaje\n"
			" m      - Alternar stop/move\n"
			" p      - Cambiar precios\n"
			" d      - Modo desarrollador on/off\n"
			" finish - Finalizar viaje actual\n"
			" clear  - Vaciar historial y log\n"
			" test   - Ejecutar tests unitarios\n"
			" exit   - Finalizar viaje y salir/Salir"
		)

	@staticmethod
	def ask_command(msg):
		return input(msg).strip().lower()

	@staticmethod
	def show_state(state):
		print(f"{COLOR_GREEN}El taxi ahora está {state}.{COLOR_RESET}")

	@staticmethod
	def show_total(st, mt, total):
		print(
			f"{COLOR_PURPLE}\nViaje finalizado.\n"
			f"Tiempo detenido   : {st:.2f}s\n"
			f"Tiempo en movimiento: {mt:.2f}s\n"
			f"Total a pagar     : €{total:.2f}{COLOR_RESET}\n"
		)

	@staticmethod
	def show_error(msg):
		print(COLOR_RED + msg + COLOR_RESET)

	@staticmethod
	def show_message(msg):
		print(msg)


class Taximeter:
	def __init__(self, view, history, logger):
		self.view = view
		self.history = history
		self.log = logger
		self.current_trip = None
		self.dev_mode = bool(logger.console_handler)
		self.stop_rate = 0.02
		self.move_rate = 0.05

	def start_new_trip(self):
		self.current_trip = Trip(self.log, self.stop_rate, self.move_rate)
		self.view.show_message(
			f"\nViaje iniciado (stop={self.stop_rate:.2f}€/s, move={self.move_rate:.2f}€/s)."
		)

	def _valid_price(self, raw: str):
		if raw.count(".") != 1:
			return None
		ent, dec = raw.split(".")
		if not (ent.isdigit() and dec.isdigit() and 1 <= len(dec) <= 2):
			return None
		val = float(raw)
		return val if val > 0 else None

	def change_prices(self):
		raw_stop = self.view.ask_command("Nuevo precio STOP (€/s): ")
		raw_move = self.view.ask_command("Nuevo precio MOVE (€/s): ")
		new_stop = self._valid_price(raw_stop)
		new_move = self._valid_price(raw_move)
		if new_stop is None or new_move is None:
			self.view.show_error(
				"Formato inválido. Usa punto y uno o dos decimales, ej. 0.3 o 0.09"
			)
			return
		self.stop_rate, self.move_rate = new_stop, new_move
		self.view.show_message(
			f"Tarifas actualizadas: stop={new_stop:.2f}€/s, move={new_move:.2f}€/s"
		)
		self.log.info(f"Tarifas cambiadas (stop={new_stop}, move={new_move})")

	def toggle_dev_mode(self):
		if self.dev_mode:
			if self.log.console_handler:
				self.log.removeHandler(self.log.console_handler)
			self.dev_mode = False
			self.view.show_message("Modo desarrollador DESACTIVADO")
			self.log.info("Modo desarrollador OFF")
		else:
			console = logging.StreamHandler()
			fmt = logging.Formatter(
				"%(asctime)s  %(levelname)-8s  %(name)s | %(message)s",
				datefmt="%Y-%m-%d %H:%M:%S",
			)
			console.setFormatter(fmt)
			self.log.addHandler(console)
			self.log.console_handler = console
			self.dev_mode = True
			self.view.show_message("Modo desarrollador ACTIVADO")
			self.log.info("Modo desarrollador ON")

	def clear_logs(self):
		open("taximetro.log", "w", encoding="utf-8").close()
		self.history.clear()
		self.view.show_message("Historial y log vaciados.")
		self.log.info("Historial y log vaciados por el operador")

	def run_tests(self):
		self.view.show_message("Ejecutando tests…")
		exit_code = pytest.main(["-q"])
		if exit_code == 0:
			self.view.show_message("✔ Todos los tests pasaron correctamente.")
			self.log.info("Tests unitarios: PASADOS")
		else:
			self.view.show_error("✖ Algunos tests fallaron. Revisa la salida.")
			self.log.error("Tests unitarios: FALLIDOS")

	def start(self):
		self.log.info("========== INICIO SESIÓN ==========")
		self.view.print_welcome()
		self.log.info("Aplicación iniciada")

		while True:
			cmd = self.view.ask_command("\n> ")

			if cmd == "start":
				if self.current_trip:
					self.view.show_error("Ya hay un viaje en curso. Usa 'finish' primero.")
					self.log.warning("start ignorado: viaje ya en curso")
				else:
					self.start_new_trip()

			elif cmd == "m":
				if not self.current_trip:
					self.view.show_error(
						"Comando no reconocido o viaje no iniciado. Si aún no has iniciado un viaje pulsa 'start'."
					)
					self.log.warning("m rechazado: no hay viaje")
				else:
					self.current_trip.toggle_state()
					self.view.show_state(self.current_trip.state)

			elif cmd == "p":
				self.change_prices()

			elif cmd == "d":
				self.toggle_dev_mode()

			elif cmd == "finish":
				if not self.current_trip:
					self.view.show_error(
						"Comando no reconocido o viaje no iniciado. Si aún no has iniciado un viaje pulsa 'start'."
					)
					self.log.warning("finish rechazado: no hay viaje")
				else:
					st, mt, total = self.current_trip.finish()
					self.view.show_total(st, mt, total)
					self.history.save(st, mt, total)
					self.current_trip = None
					self.view.print_welcome()

			elif cmd == "clear":
				self.clear_logs()

			elif cmd == "test":
				self.run_tests()

			elif cmd == "exit":
				if self.current_trip:
					st, mt, total = self.current_trip.finish()
					self.view.show_total(st, mt, total)
					self.history.save(st, mt, total)
				self.log.info("Aplicación finalizada por usuario")
				self.log.info("------------------------------")
				self.log.info("=========== FIN SESIÓN ============\n")
				self.view.show_message("Hasta luego")
				break

			else:
				self.view.show_error(
					"Comando no reconocido o viaje no iniciado. Si aún no has iniciado un viaje pulsa 'start'."
				)
				self.log.warning(f"Comando inválido: {cmd}")


if __name__ == "__main__":
	auth = AuthSystem()
	user = auth.login_menu()
	print(f"\n🔐 Sesión iniciada como: {user}")

	logger = get_app_logger()
	view = ConsoleView()
	history = FileTripHistory(logger, user)
	Taximeter(view, history, logger).start()
