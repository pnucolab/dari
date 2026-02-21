import logging
import backend.settings as settings

logger = logging.getLogger(__name__)

formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s", "%Y-%m-%d %H:%M:%S")

stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(settings.LOG_FILE)

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)