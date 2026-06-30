from locust.env import Environment

from performance_tests.configs.config import App, config
from performance_tests.preprocess.preprocess_base import PreProcessBase
from performance_tests.preprocess.preprocess_cir_schema import PreProcessCIRSchema
from performance_tests.preprocess.preprocess_sds_dataset import PreProcessSDSDataset
from performance_tests.preprocess.preprocess_sds_schema import PreProcessSDSSchema


class PreprocessMapper:
    preprocessors: list[PreProcessBase] | None = None

    def __init__(self):
        self.mapping_app = config.APP

    def initiate_preprocessors(self, header: dict, environment: Environment) -> list[PreProcessBase]:
        if self.mapping_app == App.SDS:
            # For SDS, we need to preprocess both Schema and Dataset
            preprocessors_list = [PreProcessSDSSchema, PreProcessSDSDataset]

        else:
            # For CIR, we only need to preprocess the CIR Schema
            preprocessors_list = [PreProcessCIRSchema]

        self.preprocessors = [preprocessor(header, environment) for preprocessor in preprocessors_list]

        return self.preprocessors

    def get_preprocessors(self) -> list[PreProcessBase]:
        return self.preprocessors
