from postprocess.postprocess_base import PostProcessBase

from locust_helper import LocustHelper

from configs.config import config

from result_evaluation.result_evaluator import ResultEvaluator, EvaluationResult

from result_evaluation.thresholds import THRESHOLDS_FAIL_RATIO, THRESHOLDS_AVG_RESPONSE_TIME

from configs.endpoints_config import ALL_ENDPOINTS


class PostProcessResultEvaluator(PostProcessBase):
    def __init__(self, header:dict, environment):
        self.header = header
        self.environment = environment
        self.locust_helper = LocustHelper()
        self.result_evaluator = ResultEvaluator(
            fail_ratio_thresholds=THRESHOLDS_FAIL_RATIO,
            avg_response_time_thresholds=THRESHOLDS_AVG_RESPONSE_TIME
        )
        self.endpoint_configs = ALL_ENDPOINTS

    def postprocess_master(self) -> None:

        self.logger.info("Begin test result evaluation...")

        # Evaluate average response time for each endpoint
        for (name, method), stats in self.environment.stats.entries.items():
            endpoint_key = self.map_endpoint_key_from_environment_name_and_method(name, method)
            if endpoint_key is None:
                self.logger.warning(f"Endpoint {name} with method {method} not found in endpoint configs.")

            threshold = self.result_evaluator.get_avg_response_time_threshold(endpoint_key)
            evaluation_result: EvaluationResult = self.result_evaluator.evaluate_avg_response_time(endpoint_key, stats.avg_response_time)

            if not evaluation_result["result"]:
                self.result_evaluator.prompt_anomaly(evaluation_result)
                self.logger.error(f"Endpoint {name} with method {method} failed average response time evaluation. "
                                  f"Average response time: {stats.avg_response_time} ms, "
                                  f"Threshold: {threshold} ms")
                self.environment.process_exit_code = 1

        self.logger.into("Average response time evaluation completed.")

        # Evaluate total fail ratio
        total_fail_ratio = self.environment.stats.total.fail_ratio

        evaluation_result: EvaluationResult = self.result_evaluator.evaluate_fail_ratio(total_fail_ratio)

        if not evaluation_result["result"]:
            self.result_evaluator.prompt_anomaly(evaluation_result)
            self.logger.error(f"Test failed due to failure ratio {total_fail_ratio} > {self.result_evaluator.get_fail_ratio_threshold()}")
            self.environment.process_exit_code = 1

        self.logger.into("Fail ratio evaluation completed.")

        return self.success("Successfully analysed test result.")

    def postprocess_worker(self) -> None:
        pass

    def map_endpoint_key_from_environment_name_and_method(self, endpoint_name: str, endpoint_method: str) -> str | None:
        """
        Function to get the endpoint key from the environment.

        Args:
            endpoint_name (str): The name of the endpoint.
            endpoint_method (str): The method of the endpoint.

        Returns:
            str: The endpoint key
        """
        for key, value in self.endpoint_configs.items():
            if value["name"] == endpoint_name and value["method"].upper() == endpoint_method.upper():
                return key

        return None
