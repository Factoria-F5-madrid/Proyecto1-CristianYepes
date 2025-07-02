import logging
import importlib

# Importar el módulo con el nombre que uses (tax5.py)
tax = importlib.import_module("tax5")


def test_trip_time_and_total(monkeypatch):
	"""
	Simula:
	0 s  → creación del Trip   (estado stop)
	5 s  → toggle → pasa a move
	10 s → finish
	Esperado:
	    stop_time = 5
	    move_time = 5
	    total = 5*0.02 + 5*0.05 = 0.35 €
	"""
	times = [0, 5, 10]

	def fake_perf_counter():
		return times.pop(0)

	monkeypatch.setattr(tax.time, "perf_counter", fake_perf_counter)

	logger = logging.getLogger("test_trip")
	logger.console_handler = None
	trip = tax.Trip(logger, stop_rate=0.02, move_rate=0.05)

	trip.toggle_state()
	stop, move, total = trip.finish()

	assert round(stop, 1) == 5.0
	assert round(move, 1) == 5.0
	assert round(total, 2) == 0.35
