import os

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), '')
DB_PATH = SCRIPT_DIR + "data.sqlite"
URLS_PATH = SCRIPT_DIR + "urls"
OUTPUT_DIR = SCRIPT_DIR + "www"
SOCKET_TIMEOUT = 30
NUMBER_OF_PROCESSES = 10
GROUP_INTERVAL = 60 * 60 * 2
RETENTION_PERIOD = "7 days"
