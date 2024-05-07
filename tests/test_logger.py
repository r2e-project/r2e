import logging
import os
import unittest
from r2e.logger import setup_logging


@unittest.skip("Skip to keep outputs clean.")
class TestLogger(unittest.TestCase):
    log_file = "test_r2e.log"

    def setUp(self):
        # Ensure the log file does not exist before each test
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

        # Reset the logger by closing and removing all handlers
        logger = logging.getLogger("r2e")
        for handler in logger.handlers[:]:  # Iterate over a copy of the list
            handler.close()  # Properly close the handler
            logger.removeHandler(handler)  # Remove the handler from the logger

    def test_file_logging(self):
        # Set up the logger with a test log file
        logger = setup_logging(level=logging.DEBUG, log_file=self.log_file)

        # Log a test message
        test_message = "This is a test log message"
        logger.debug(test_message)

        # Check that the log file exists
        file_exists = os.path.exists(self.log_file)
        self.assertTrue(file_exists, f"Log file '{self.log_file}' should exist.")

        # Read the log file and check that the test message is in there
        with open(self.log_file, "r") as f:
            log_contents = f.read()
            self.assertIn(test_message, log_contents)

    def tearDown(self):
        # Clean up the log file after each test
        if os.path.exists(self.log_file):
            os.remove(self.log_file)


if __name__ == "__main__":
    unittest.main()
