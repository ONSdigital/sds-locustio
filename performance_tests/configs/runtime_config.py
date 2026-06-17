from preprocess.preprocess_base import PreProcessBase
from preprocess.preprocess_sds_dataset import PreProcessSDSDataset
from preprocess.preprocess_sds_schema import PreProcessSDSSchema


class RuntimeConfig:
    DATASET_ID = "UNASSIGNED"  # To be set during initiation
    SCHEMA_GUID = "UNASSIGNED"  # To be set during initiation
    HEADER = {}  # To be set during initiation

    def set_config_from_preprocessors(self, preprocessors: list[PreProcessBase]):
        for preprocessor in preprocessors:
            if isinstance(preprocessor, PreProcessSDSDataset):
                self.DATASET_ID = preprocessor.get_dataset_id()
            elif isinstance(preprocessor, PreProcessSDSSchema):
                self.SCHEMA_GUID = preprocessor.get_schema_guid()
