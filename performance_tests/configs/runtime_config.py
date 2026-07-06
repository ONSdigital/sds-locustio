from performance_tests.preprocess.preprocess_base import PreProcessBase
from performance_tests.preprocess.preprocess_sds_dataset import PreProcessSDSDataset
from performance_tests.preprocess.preprocess_sds_schema import PreProcessSDSSchema


class RequestConfig:
    full_url: str = "UNASSIGNED"  # To be set during initiation
    method: str = "UNASSIGNED"  # To be set during initiation
    group_name: str = "UNASSIGNED"  # To be set during initiation
    payload: dict[str, str] | None = None  # To be set during initiation

    def __init__(self, full_url: str, method: str, group_name: str, payload: dict[str, str] | None):
        self.full_url = full_url
        self.method = method
        self.group_name = group_name
        self.payload = payload

class RuntimeConfig:
    """
    Class to cache the runtime configuration values that are needed across different test methods and processes.
    """
    DATASET_ID: str = "UNASSIGNED"  # To be set during initiation
    SCHEMA_GUID: str = "UNASSIGNED"  # To be set during initiation
    HEADER: dict[str,str] | None = None  # To be set during initiation
    REQUEST_CONFIG: RequestConfig | None = None  # To be set during initiation

    def set_config_from_preprocessors(self, preprocessors: list[PreProcessBase]):
        for preprocessor in preprocessors:
            if isinstance(preprocessor, PreProcessSDSDataset):
                self.DATASET_ID = preprocessor.get_dataset_id()
            elif isinstance(preprocessor, PreProcessSDSSchema):
                self.SCHEMA_GUID = preprocessor.get_schema_guid()
