# import logging
# from datetime import datetime
# import os

# LOG_FILE= f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
# logs_path=os.path.join(os.getcwd(), 'logs', LOG_FILE)
# os.makedirs(logs_path,exist_ok=True)

# LOG_FILE_PATH=os.path.join(logs_path, LOG_FILE)

# logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, 
                    
#         format='[%(asctime)s] %(lineno)d %(name)s - %(levelname)s:%(message)s')


import logging
import os

# Use a fixed log file name
LOG_FILE = "application.log"

# Create the logs directory if it doesn't exist
logs_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Full path to the log file
LOG_FILE_PATH = os.path.join(logs_dir, LOG_FILE)

# Set up logging
logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format='[%(asctime)s] %(lineno)d %(name)s - %(levelname)s: %(message)s'
)
