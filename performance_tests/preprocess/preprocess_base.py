import logging
from abc import ABC, abstractmethod
from typing import Any

from locust.runners import WorkerRunner

from configs.config import config


class PreProcessBase(ABC):
    environment: Any
    worker_index: int | None
    logger = logging.getLogger(__name__)

    @abstractmethod
    def preprocess_master(self) -> None:
        """Pre-process the data for the test for master node"""
        pass

    @abstractmethod
    def preprocess_worker(self) -> None:
        """Pre-process the data for the test for worker nodes"""
        pass

    def preprocess(self) -> None:
        """Pre-process the data for the test"""
        if config.HEADLESS_MODE:
            # Headless mode
            if isinstance(self.environment.runner, WorkerRunner):
                # Worker Node operation
                self.preprocess_worker()
            else:
                # Master Node operation
                self.preprocess_master()
        else:
            # Non-headless mode - run both master and worker operations in the same process
            self.preprocess_master()
            self.preprocess_worker()

    def success(self, message: str) -> int:
        """Handle successful pre-processing

        Args:
            message (str): the success message to log

        Returns:
            integer: 1 for success
        """
        self.logger.info(message)

        return 1

    def skip(self, message: str) -> int:
        """Handle skipped pre-processing

        Args:
            message (str): the skip message to log

        Returns:
            integer: 0 for skipped pre-processing
        """
        self.logger.info(message)

        return 0

    def error(self, message: str) -> int:
        """Handle errors during pre-processing

        Args:
            message (str): the error message to log

        Returns:
            integer: -1 for failed pre-processing
        """
        self.logger.error(message)
        self.logger.error("Pre-process has failed. Program is shutting down.")

        self.environment.process_exit_code = 1

        self.environment.runner.quit()

        return -1
