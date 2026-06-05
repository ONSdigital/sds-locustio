from configs.config import config, App

from preprocess.preprocess_base import PreProcessBase

from preprocess.preprocess_sds_dataset import PreProcessSDSDataset
from preprocess.preprocess_sds_schema import PreProcessSDSSchema


class PreprocessMapper:
    preprocessors: list[PreProcessBase] = []

    def __init__(self):
        self.mapping_app = config.APP

    def initiate_preprocessors(self, header: dict, environment) -> list[PreProcessBase]:
        preprocessors_list = []
        if self.mapping_app == App.SDS:
            preprocessors_list = [PreProcessSDSSchema, PreProcessSDSDataset]

            self.preprocessors = [preprocessor(header, environment) for preprocessor in preprocessors_list]

            return self.preprocessors

        else:
            return []

    def get_preprocessors(self) -> list[PreProcessBase]:
        return self.preprocessors
