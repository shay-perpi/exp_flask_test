import logging
import os
from datetime import datetime
from .config_file import path_log, logger_name

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}
today_date = datetime.now().strftime("%Y-%m-%d")
name_file = f"{logger_name}-{today_date}"


class LoggerSingleton:
    _instance = None
    _initialized = False
    today_date = datetime.now().strftime("%Y-%m-%d")
    name_file = f"{logger_name}-{today_date}"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
            cls._instance.initialize_logger()
        return cls._instance

    def initialize_logger(self):
        if not self._initialized:
            self.logger = logging.getLogger()
            self.level = "default"
            self.log_file = path_log + f"/{name_file}-log.log"
            self.err_file = path_log + f"/{name_file}-err.log"
            self.logger.setLevel(LEVELS.get(self.level, logging.NOTSET))
            self.create_file(self.log_file)
            self.create_file(self.err_file)

            self.handler = logging.FileHandler(self.log_file, encoding="utf-8", mode="w")
            self.err_handler = logging.FileHandler(self.err_file, encoding="utf-8", mode="w")

            self._initialized = True

    def create_file(self, filename):
        path = filename[0: filename.rfind("/")]
        if not os.path.isdir(path):
            os.makedirs(path)
        if not os.path.isfile(filename):
            with open(filename, mode="w", encoding="utf-8"):
                pass

    def set_handler(self, levels):
        if levels == "error":
            self.logger.addHandler(self.err_handler)
        self.logger.addHandler(self.handler)

    def remove_handler(self, levels):
        if levels == "error":
            self.logger.removeHandler(self.err_handler)
        self.logger.removeHandler(self.handler)

    def debug(self, log_msg):
        self.set_handler("debug")
        self.logger.debug("[DEBUG] " + log_msg)
        self.remove_handler("debug")

    def info(self, log_msg):
        self.set_handler("info")
        self.logger.info("[INFO] " + log_msg)
        self.remove_handler("info")

    def warning(self, log_msg):
        self.set_handler("warning")
        self.logger.warning("[WARNING] " + log_msg)
        self.remove_handler("warning")

    def error(self, log_msg):
        self.set_handler("error")
        self.logger.error("[ERROR] " + log_msg)
        self.remove_handler("error")

    def critical(self, log_msg):
        self.set_handler("critical")
        self.logger.error("[CRITICAL] " + log_msg)
        self.remove_handler("critical")
