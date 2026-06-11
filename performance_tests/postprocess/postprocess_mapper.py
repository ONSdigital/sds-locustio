from configs.config import config, App
from postprocess.postprocess_base import PostProcessBase

from postprocess.postprocess_cir_delete_schemas import PostProcessCirDeleteSchemas


class PostprocessMapper:
    postprocessors: list[PostProcessBase] = []

    def __init__(self):
        self.mapping_app = config.APP

    def initiate_postprocessors(self, header: dict, environment) -> list[PostProcessBase]:
        if self.mapping_app == App.SDS:
            # For SDS, we do not have any post-processing steps
            postprocessors_list = []

        else:
            # For CIR, we need to delete the CIR Schema record after the test
            postprocessors_list = [PostProcessCirDeleteSchemas]

        self.postprocessors = [postprocessor(header, environment) for postprocessor in postprocessors_list]

        return self.postprocessors

    def get_postprocessors(self) -> list[PostProcessBase]:
        return self.postprocessors