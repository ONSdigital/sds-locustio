import logging
from abc import ABC, abstractmethod
from typing import Any

from performance_tests.configs.config import config
from locust.runners import WorkerRunner


class PostProcessBase(ABC):
    environment: Any
    logger = logging.getLogger(__name__)

    @abstractmethod
    def postprocess_master(self) -> int:
        """Post-process the data for the test for master node"""
        pass

    @abstractmethod
    def postprocess_worker(self) -> int:
        """Post-process the data for the test for worker nodes"""
        pass

    def postprocess(self) -> None:
        """Post-process the data for the test"""
        if config.HEADLESS_MODE:
            # Headless mode
            if isinstance(self.environment.runner, WorkerRunner):
                # Worker Node operation
                self.postprocess_worker()
            else:
                # Master Node operation
                self.postprocess_master()
        else:
            # Non-headless mode - run both master and worker operations in the same process
            # Run post-processing for worker first, then master
            self.postprocess_worker()
            self.postprocess_master()

    def success(self, message: str) -> int:
        """Handle successful post-processing

        Args:
            message (str): the success message to log

        Returns:
            integer: 1 for success
        """
        self.logger.info(message)

        return 1

    def skip(self, message: str) -> int:
        """Handle skipped post-processing

        Args:
            message (str): the skip message to log

        Returns:
            integer: 0 for skipped pre-processing
        """
        self.logger.info(message)

        return 0

    def error(self, message: str) -> int:
        """Handle errors during post-processing

        Args:
            message (str): the error message to log

        Returns:
            integer: -1 for failed pre-processing
        """
        self.logger.error(message)
        self.logger.error("Post-process has failed. Program is shutting down.")

        self.environment.process_exit_code = 1

        self.environment.runner.quit()

        return -1
