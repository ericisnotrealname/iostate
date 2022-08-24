import logging
import os, time

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
FMT = "%(asctime)s - %(levelname)s - %(filename)s: %(funcName)s: line %(lineno)s - %(message)s"

root_path = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
log_file = os.path.join(root_path, "log", "script", "iostate"+ \
    time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))+".log")

formatter = logging.Formatter(FMT)
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)