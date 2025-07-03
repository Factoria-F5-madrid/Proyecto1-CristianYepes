import logging
from logging.handlers import RotatingFileHandler
from db import Database, DBLogHandler

def get_app_logger(path: str = "taximetro.log", *, console_debug: bool = False) -> logging.Logger:
	logger = logging.getLogger("taximeter")
	if logger.handlers:
		return logger

	logger.setLevel(logging.INFO)
	logger.propagate = False

	fmt = logging.Formatter(
		"%(asctime)s  %(levelname)-8s  %(name)s | %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S"
	)

	file_handler = RotatingFileHandler(path, maxBytes=100_000, backupCount=3)
	file_handler.setFormatter(fmt)
	logger.addHandler(file_handler)

	db = Database()
	db_handler = DBLogHandler(db)
	logger.addHandler(db_handler)

	logger.console_handler = None

	if console_debug:
		console = logging.StreamHandler()
		console.setFormatter(fmt)
		logger.addHandler(console)
		logger.console_handler = console

	return logger
