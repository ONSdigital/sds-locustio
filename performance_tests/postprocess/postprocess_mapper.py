from configs.config import App, config
from postprocess.postprocess_base import PostProcessBase
from postprocess.postprocess_cir_delete_schemas import PostProcessCirDeleteSchemas
from postprocess.postprocess_result_evaluator import PostProcessResultEvaluator


class PostprocessMapper:
    postprocessors: list[PostProcessBase] | None = None

    def __init__(self):
        self.mapping_app = config.APP

    def initiate_postprocessors(self, header: dict, environment) -> list[PostProcessBase]:
        if self.mapping_app == App.SDS:
            postprocessors_list = [PostProcessResultEvaluator]

        else:
            postprocessors_list = [PostProcessCirDeleteSchemas, PostProcessResultEvaluator]

        self.postprocessors = [postprocessor(header, environment) for postprocessor in postprocessors_list]

        return self.postprocessors

    def get_postprocessors(self) -> list[PostProcessBase]:
        return self.postprocessors
