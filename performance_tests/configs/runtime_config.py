from performance_tests.preprocess.preprocess_base import PreProcessBase
from performance_tests.preprocess.preprocess_cir_schema import PreProcessCIRSchema
from performance_tests.preprocess.preprocess_sds_dataset import PreProcessSDSDataset
from performance_tests.preprocess.preprocess_sds_schema import PreProcessSDSSchema


class RuntimeConfig:
    """
    Class to cache the runtime configuration values that are needed across different test methods and processes.
    """
    DATASET_ID: str = "UNASSIGNED"  # To be set during initiation
    SCHEMA_GUID: str = "UNASSIGNED"  # To be set during initiation
    CI_SCHEMA_GUIDS: list[str] = "UNASSIGNED"  # To be set during initiation
    HEADER: dict[str,str] | None = None  # To be set during initiation

    def set_config_from_preprocessors(self, preprocessors: list[PreProcessBase]):
        for preprocessor in preprocessors:
            if isinstance(preprocessor, PreProcessSDSDataset):
                self.DATASET_ID = preprocessor.get_dataset_id()
            elif isinstance(preprocessor, PreProcessSDSSchema):
                self.SCHEMA_GUID = preprocessor.get_schema_guid()
            elif isinstance(preprocessor, PreProcessCIRSchema):
                self.CI_SCHEMA_GUIDS = preprocessor.get_ci_schema_guids()
