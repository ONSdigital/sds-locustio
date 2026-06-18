from performance_tests.configs.endpoints_config import ALL_ENDPOINTS
from performance_tests.locust_helper import LocustHelper
from performance_tests.postprocess.postprocess_base import PostProcessBase
from performance_tests.result_evaluation.result_evaluator import EvaluationResult, ResultEvaluator
from performance_tests.result_evaluation.thresholds import THRESHOLDS_AVG_RESPONSE_TIME, THRESHOLDS_FAIL_RATIO


class PostProcessResultEvaluator(PostProcessBase):
    def __init__(self, header:dict, environment):
        self.header = header
        self.environment = environment
        self.locust_helper = LocustHelper()
        self.result_evaluator = ResultEvaluator(
            logger=self.logger,
            fail_ratio_thresholds=THRESHOLDS_FAIL_RATIO,
            avg_response_time_thresholds=THRESHOLDS_AVG_RESPONSE_TIME
        )
        self.endpoint_configs = ALL_ENDPOINTS

    def postprocess_master(self) -> int:

        self.logger.info("Begin test result evaluation...")

        # Evaluate average response time for each endpoint
        for (name, method), stats in self.environment.stats.entries.items():
            endpoint_key = self.map_endpoint_key_from_environment_name_and_method(name, method)
            if endpoint_key is None:
                self.logger.warning(f"Endpoint {name} with method {method} not found in endpoint configs.")

            threshold = self.result_evaluator.get_avg_response_time_threshold(endpoint_key)
            evaluation_result: EvaluationResult = self.result_evaluator.evaluate_avg_response_time(
                endpoint=endpoint_key,
                avg_response_time=stats.avg_response_time
            )

            if not evaluation_result["result"]:
                self.result_evaluator.prompt_anomaly(evaluation_result)
                self.logger.error(f"Endpoint {name} with method {method} failed average response time evaluation. "
                                  f"Average response time: {stats.avg_response_time} ms, "
                                  f"Threshold: {threshold} ms")
                self.environment.process_exit_code = 1

        self.logger.info("Average response time evaluation completed.")

        # Evaluate total fail ratio
        total_fail_ratio = self.environment.stats.total.fail_ratio

        evaluation_result: EvaluationResult = self.result_evaluator.evaluate_fail_ratio(fail_ratio=total_fail_ratio)

        if not evaluation_result["result"]:
            self.result_evaluator.prompt_anomaly(evaluation_result)
            self.logger.error(f"Test failed due to failure ratio {total_fail_ratio} > {self.result_evaluator.get_fail_ratio_threshold()}")
            self.environment.process_exit_code = 1

        self.logger.info("Fail ratio evaluation completed.")

        return self.success("Successfully analysed test result.")

    def postprocess_worker(self) -> int:
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
            if value["name"] in endpoint_name and value["method"].upper() == endpoint_method.upper():
                return key

        return None
