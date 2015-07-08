import os

base_dir = os.path.dirname(__file__) + '/'
DB_PATH = base_dir + "data.sqlite"
URLS_PATH = base_dir + "urls"
OUTPUT_DIR = base_dir + "www"
SOCKET_TIMEOUT = 30
NUMBER_OF_PROCESSES = 10
GROUP_INTERVAL = 60 * 60
GENERATE_PERIOD = "7 days"
