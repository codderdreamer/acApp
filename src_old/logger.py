import logging
import os
from logging.handlers import RotatingFileHandler

class CustomLogger:
    def __init__(self, name, log_file, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Ensure log directory exists
        log_directory = os.path.dirname(log_file)
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        # Remove any existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Rotating file handler
        file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024*3, backupCount=3)
        file_file_formatter = logging.Formatter(fmt='%(levelname)s %(asctime)s [%(pathname)s:%(lineno)d]: %(message)s')
        file_handler.setFormatter(file_file_formatter)

        # Add handlers
        self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

# Initialize loggers
CHARGE_POINT_LOGGER_NAME = 'charge_point'
CENTRAL_SYSTEM_LOGGER_NAME = 'central_system'
CENTRAL_SYSTEM_LOGGER_PATH = '/tmp/acApp/logs/central_system.log'
CHARGE_POINT_LOGGER_PATH = '/tmp/acApp/logs/charge_point.log'
AC_APP_LOGGER_NAME = 'ac_app'
AC_APP_LOGGER_PATH = '/tmp/acApp/logs/ac_app.log'

LOGGER_CENTRAL_SYSTEM = CustomLogger(CENTRAL_SYSTEM_LOGGER_NAME, CENTRAL_SYSTEM_LOGGER_PATH).get_logger()
LOGGER_CHARGE_POINT = CustomLogger(CHARGE_POINT_LOGGER_NAME, CHARGE_POINT_LOGGER_PATH).get_logger()
ac_app_logger = CustomLogger(AC_APP_LOGGER_NAME, AC_APP_LOGGER_PATH).get_logger()
