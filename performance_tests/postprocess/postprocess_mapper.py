from locust.env import Environment

from performance_tests.configs.config import App, config
from performance_tests.postprocess.postprocess_base import PostProcessBase
from performance_tests.postprocess.postprocess_cir_delete_schemas import PostProcessCirDeleteSchemas
from performance_tests.postprocess.postprocess_result_evaluator import PostProcessResultEvaluator


class PostprocessMapper:
    postprocessors: list[PostProcessBase] | None = None

    def __init__(self):
        self.mapping_app = config.APP

    def initiate_postprocessors(self, header: dict, environment: Environment) -> list[PostProcessBase]:
        if self.mapping_app == App.SDS:
            postprocessors_list = [PostProcessResultEvaluator]

        else:
            postprocessors_list = [PostProcessCirDeleteSchemas, PostProcessResultEvaluator]

        self.postprocessors = [postprocessor(header, environment) for postprocessor in postprocessors_list]

        return self.postprocessors

    def get_postprocessors(self) -> list[PostProcessBase]:
        return self.postprocessors
