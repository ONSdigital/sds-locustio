import logging
from abc import ABC, abstractmethod
from typing import Any


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

    def success(self, message: str) -> int:
        """Handle successful pre-processing

        Args:
            message (str): the success message to log

        Returns:
            None
        """
        self.logger.info(message)

        return 1

    def skip(self, message: str) -> int:
        """Handle skipped pre-processing

        Args:
            message (str): the skip message to log

        Returns:
            None
        """
        self.logger.info(message)

        return 0

    def error(self, message: str) -> int:
        """Handle errors during pre-processing

        Args:
            message (str): the error message to log

        Returns:
            None
        """
        self.logger.error(message)
        self.logger.error("Pre-process has failed. Program is shutting down.")

        self.environment.process_exit_code = 1

        self.environment.runner.quit()

        return -1