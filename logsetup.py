import logging
from db import Database, DBLogHandler

def get_app_logger(*, console_debug: bool = False) -> logging.Logger:
	logger = logging.getLogger("taximeter")
	if logger.handlers:
		return logger

	logger.setLevel(logging.INFO)
	logger.propagate = False

	# ⬇️  Handler que escribe en la tabla logs de SQLite
	db = Database()
	logger.addHandler(DBLogHandler(db))

	logger.console_handler = None

	if console_debug:
		console = logging.StreamHandler()
		fmt = logging.Formatter(
			"%(asctime)s  %(levelname)-8s  %(name)s | %(message)s",
			datefmt="%Y-%m-%d %H:%M:%S",
		)
		console.setFormatter(fmt)
		logger.addHandler(console)
		logger.console_handler = console

	return logger
