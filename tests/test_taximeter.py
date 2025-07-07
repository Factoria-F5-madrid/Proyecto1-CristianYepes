import logging
import importlib

tax = importlib.import_module("tax5")


class DummyView:
	def ask_command(self, _): ...
	def show_error(self, _): ...
	def show_message(self, _): ...
	def print_welcome(self): ...
	def show_state(self, _): ...
	def show_total(self, *_): ...


class DummyHistory:
	def save(self, *_): ...
	def clear(self): ...


def _create_taximeter():
	logger = logging.getLogger("test_tm")
	logger.console_handler = None
	return tax.Taximeter(DummyView(), DummyHistory(), logger, "test_user")


def test_valid_price():
	tm = _create_taximeter()
	assert tm.price_mgr._valid("0.09") == 0.09
	assert tm.price_mgr._valid("0.3") == 0.3
	assert tm.price_mgr._valid("12.50") == 12.5
	assert tm.price_mgr._valid("0,09") is None
	assert tm.price_mgr._valid("0.009") is None
	assert tm.price_mgr._valid("1.234") is None
	assert tm.price_mgr._valid("-0.10") is None


def test_change_prices_updates_and_validates(monkeypatch):
	logger = logging.getLogger("test_change")
	logger.console_handler = None
	tm = tax.Taximeter(DummyView(), DummyHistory(), logger, "test_user")

	seq = iter(["0.10", "0.15"])
	monkeypatch.setattr(tm.view, "ask_command", lambda *_: next(seq))
	tm.price_mgr.prompt_and_update()
	assert tm.price_mgr.stop_rate == 0.10
	assert tm.price_mgr.move_rate == 0.15

	seq = iter(["0.001", "0.2"])
	monkeypatch.setattr(tm.view, "ask_command", lambda *_: next(seq))
	tm.price_mgr.prompt_and_update()
	assert tm.price_mgr.stop_rate == 0.10
	assert tm.price_mgr.move_rate == 0.15


def test_trip_time_and_total(monkeypatch):
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
