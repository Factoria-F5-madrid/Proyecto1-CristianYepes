import time
import threading
import datetime


COLOR_CYAN   = "\033[96m"
COLOR_GREEN  = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_PURPLE = "\033[95m"
COLOR_RED    = "\033[91m"
COLOR_RESET  = "\033[0m"


# ────────────────────────────
#  Cronómetro del viaje
# ────────────────────────────
class Trip:
	STOP_RATE = 0.02
	MOVE_RATE = 0.05

	def __init__(self):
		self.total      = 0.0
		self.state      = "stop"
		self.start_time = time.perf_counter()
		self.stop_time  = 0.0
		self.move_time  = 0.0
		self.lock       = threading.Lock()

	def _accumulate_elapsed(self):
		now     = time.perf_counter()
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

	def finish(self):
		with self.lock:
			self._accumulate_elapsed()
			self.total = (
				self.stop_time * self.STOP_RATE +
				self.move_time * self.MOVE_RATE
			)
			return self.stop_time, self.move_time, self.total


# ────────────────────────────
#  Persistencia de historial
# ────────────────────────────
class FileTripHistory:
	def __init__(self, filename: str = "historial_viajes.txt"):
		self.filename = filename

	def save(self, stop_time: float, move_time: float, total: float) -> None:
		with open(self.filename, "a", encoding="utf-8") as f:
			print("----- Viaje finalizado -----", file=f)
			print(f"Fecha y hora: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}", file=f)
			print(f"Tiempo detenido: {stop_time:.2f} segundos", file=f)
			print(f"Tiempo en marcha : {move_time:.2f} segundos", file=f)
			print(f"Total a pagar   : €{total:.2f}", file=f)
			print("------------------------------\n", file=f)


# ────────────────────────────
#  Presentación por consola
# ────────────────────────────
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
			" finish - Finalizar viaje actual\n"
			" exit   - Finalizar viaje y salir / Salir"
		)

	@staticmethod
	def ask_command(msg):
		return input(msg).strip().lower()

	@staticmethod
	def show_state(state):
		print(f"{COLOR_GREEN}El taxi ahora está {state}.{COLOR_RESET}")

	@staticmethod
	def show_total(stop_time, move_time, total):
		print(
			f"{COLOR_PURPLE}\nViaje finalizado.\n"
			f"Tiempo detenido   : {stop_time:.2f}s\n"
			f"Tiempo en movimiento: {move_time:.2f}s\n"
			f"Total a pagar     : €{total:.2f}{COLOR_RESET}\n"
		)

	@staticmethod
	def show_error(msg):
		print(COLOR_RED + msg + COLOR_RESET)

	@staticmethod
	def show_message(msg):
		print(msg)


# ────────────────────────────
#  Controlador principal
# ────────────────────────────
class Taximeter:
	def __init__(self, view: ConsoleView, history: FileTripHistory):
		self.view    = view
		self.history = history
		self.current_trip = None

	def start_new_trip(self):
		self.current_trip = Trip()
		self.view.show_message("\nViaje iniciado (estado: stop).")

	def start(self):
		self.view.print_welcome()
		while True:
			cmd = self.view.ask_command("\n> ")

			if cmd == "start":
				if self.current_trip:
					self.view.show_error("Ya hay un viaje en curso. Usa 'finish' primero.")
				else:
					self.start_new_trip()

			elif cmd == "m":
				if not self.current_trip:
					self.view.show_error("Viaje no iniciado. Pulsa 'start' para comenzar.")
				else:
					self.current_trip.toggle_state()
					self.view.show_state(self.current_trip.state)

			elif cmd == "finish":
				if not self.current_trip:
					self.view.show_error("Viaje no iniciado. Pulsa 'start' para comenzar.")
				else:
					stop_time, move_time, total = self.current_trip.finish()
					self.view.show_total(stop_time, move_time, total)
					self.history.save(stop_time, move_time, total)
					self.current_trip = None
					self.view.print_welcome()

			elif cmd == "exit":
				if self.current_trip:
					stop_time, move_time, total = self.current_trip.finish()
					self.view.show_total(stop_time, move_time, total)
					self.history.save(stop_time, move_time, total)
				self.view.show_message("Hasta luego")
				break

			else:
				self.view.show_error("Comando inválido. Usa 'start' para iniciar un viaje.")


# ────────────────────────────
#  Entrada del programa
# ────────────────────────────
if __name__ == "__main__":
	view     = ConsoleView()
	history  = FileTripHistory()
	Taximeter(view, history).start()
