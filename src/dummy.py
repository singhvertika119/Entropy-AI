import time
import random
import logging
import os

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)
log_file_path = "logs/dummy.log"

# Configure the logger
logging.basicConfig(
    filename=log_file_path, 
    level=logging.DEBUG,
    format="%(asctime)s - [SERVER] - %(levelname)s - %(message)s"
)

# A list of simulated errors to randomly trigger
ERRORS = [
    "psycopg2.OperationalError: FATAL: too many connections for role 'app_user'",
    "TimeoutError: Request to external payment gateway API timed out after 30000ms",
    "KeyError: 'user_auth_token' missing in request payload",
    "MemoryError: Unable to allocate 2.4GiB for array shape (10000, 10000)"
]

print(f"Starting simulated application. Writing logs to {log_file_path}...")

while True:
    # 90% of the time, the app behaves normally
    if random.random() > 0.1:
        logging.info(f"Handled GET request for /api/v1/users/{random.randint(100, 999)} gracefully.")
        time.sleep(random.uniform(0.1, 1.0))
    else:
        # 10% of the time, it throws a critical error
        error_msg = random.choice(ERRORS)
        logging.error(f"Traceback (most recent call last): {error_msg}")
        time.sleep(2) # Pause briefly after an error