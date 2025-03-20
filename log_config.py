import logging
import os
from config import BASE_DIR

# Log file path
LOG_FILE = os.path.join(BASE_DIR, 'app.log')

# Basic logging configuration
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Logger instance
logger = logging.getLogger(__name__)
