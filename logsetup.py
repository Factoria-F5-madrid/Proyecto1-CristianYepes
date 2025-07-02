import logging
from logging.handlers import RotatingFileHandler


def get_app_logger(path: str = "taximetro.log", *, console_debug: bool = False) -> logging.Logger:
	"""
	Devuelve el logger principal. Siempre escribe en taximetro.log;
	solo muestra en consola si console_debug=True.
	"""
	logger = logging.getLogger("taximeter")
	if logger.handlers:					  # ya configurado
		return logger

	logger.setLevel(logging.INFO)

	fmt = logging.Formatter(
	    "%(asctime)s  %(levelname)-8s  %(name)s | %(message)s",
	    datefmt="%Y-%m-%d %H:%M:%S"
	)

	file_handler = RotatingFileHandler(path, maxBytes=100_000, backupCount=3)
	file_handler.setFormatter(fmt)
	logger.addHandler(file_handler)

	logger.console_handler = None		  # se usará para el modo desarrollador

	if console_debug:
		console = logging.StreamHandler()
		console.setFormatter(fmt)
		logger.addHandler(console)
		logger.console_handler = console

	return logger
