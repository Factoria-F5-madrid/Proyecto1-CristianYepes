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
	return tax.Taximeter(DummyView(), DummyHistory(), logger)


def test_valid_price():
	tm = _create_taximeter()
	assert tm._valid_price("0.09") == 0.09
	assert tm._valid_price("0.3") == 0.3
	assert tm._valid_price("12.50") == 12.5
	assert tm._valid_price("0,09") is None
	assert tm._valid_price("0.009") is None
	assert tm._valid_price("1.234") is None
	assert tm._valid_price("-0.10") is None


def test_change_prices_updates_and_validates(monkeypatch):
	logger = logging.getLogger("test_change")
	logger.console_handler = None
	tm = tax.Taximeter(DummyView(), DummyHistory(), logger)

	seq = iter(["0.10", "0.15"])
	monkeypatch.setattr(tm.view, "ask_command", lambda *_: next(seq))
	tm.change_prices()
	assert tm.stop_rate == 0.10
	assert tm.move_rate == 0.15

	seq = iter(["0.001", "0.2"])
	monkeypatch.setattr(tm.view, "ask_command", lambda *_: next(seq))
	tm.change_prices()
	assert tm.stop_rate == 0.10
	assert tm.move_rate == 0.15
