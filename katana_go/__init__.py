from logging import Formatter, Logger, DEBUG, StreamHandler

LOGGER = Logger(__name__, DEBUG)

console_handler = StreamHandler()

formatter = Formatter(
    "%(asctime)s - %(name)s - %(lineno)d - %(levelname)-8s - %(message)s"
)
console_handler.setFormatter(formatter)

LOGGER.addHandler(console_handler)
