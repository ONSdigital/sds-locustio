from logging import Logger
from typing import NotRequired, TypedDict

from performance_tests.result_evaluation.anomalies import (
    ANOMALIES, AVG_RESPONSE_TIME_EXCEEDED_ANOMALY, FAIL_RATIO_EXCEEDED_ANOMALY, Anomaly)


class EvaluationResult(TypedDict):
    """
    A TypedDict to represent the evaluation result.
    """
    result: bool
    anomaly: NotRequired[Anomaly]


class ResultEvaluator:
    def __init__(
            self,
            logger: Logger,
            fail_ratio_thresholds: float,
            avg_response_time_thresholds: dict[str, int],
    ):
        self.logger = logger
        self.fail_ratio_thresholds = fail_ratio_thresholds
        self.avg_response_time_thresholds = avg_response_time_thresholds

    def evaluate_fail_ratio(self, fail_ratio: float) -> EvaluationResult:
        """
        Evaluate the fail ratio against the threshold.

        Parameters:
        fail_ratio (float): The fail ratio to evaluate.

        Returns:
        bool: True if the fail ratio is within the threshold, Anomaly otherwise.
        """
        if fail_ratio > self.get_fail_ratio_threshold():
            return EvaluationResult(result=False, anomaly=ANOMALIES.get(FAIL_RATIO_EXCEEDED_ANOMALY))

        return EvaluationResult(result=True, anomaly=None)

    def evaluate_avg_response_time(self, endpoint: str, avg_response_time: float) -> EvaluationResult:
        """
        Evaluate the average response time against the threshold for a specific endpoint.
        If the endpoint is not found in the thresholds, it will use the default threshold.

        Parameters:
        endpoint (str): The endpoint to evaluate.
        avg_response_time (float): The average response time to evaluate.

        Returns:
        bool: True if the average response time is within the threshold, Anomaly otherwise.
        """
        threshold = self.get_avg_response_time_threshold(endpoint)
        if avg_response_time > threshold:
            return EvaluationResult(result=False, anomaly=ANOMALIES.get(AVG_RESPONSE_TIME_EXCEEDED_ANOMALY))

        return EvaluationResult(result=True, anomaly=None)

    def get_avg_response_time_threshold(self, endpoint: str) -> int:
        """
        Get the average response time threshold for a specific endpoint.
        If the endpoint is not found in the thresholds, it will return the default threshold.

        Parameters:
        endpoint (str): The endpoint to get the threshold for.

        Returns:
        int: The average response time threshold for the endpoint.
        """
        return self.avg_response_time_thresholds.get(endpoint, self.avg_response_time_thresholds.get("default"))

    def get_fail_ratio_threshold(self) -> float:
        """
        Get the fail ratio threshold.

        Returns:
        float: The fail ratio threshold.
        """
        return self.fail_ratio_thresholds

    def prompt_anomaly(self, evaluation_result: EvaluationResult) -> None:
        """
        Prompt the logging of an anomaly if the evaluation result indicates an anomaly.

        Parameters:
        evaluation_result (EvaluationResult): The evaluation result to check for anomalies.
        """
        if evaluation_result["anomaly"]:
            anomaly: Anomaly = evaluation_result["anomaly"]
            self.logger.error(anomaly["logging"])
