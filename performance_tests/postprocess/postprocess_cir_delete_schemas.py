from performance_tests.configs.config import config
from performance_tests.locust_helper import LocustHelper
from performance_tests.postprocess.postprocess_base import PostProcessBase


class PostProcessCirDeleteSchemas(PostProcessBase):
    def __init__(self, header:dict, environment):
        self.header = header
        self.environment = environment
        self.locust_helper = LocustHelper()

    def postprocess_master(self) -> int:
        if self.locust_helper.delete_cir_schema_record_after_test(
                headers=self.header,
                base_url=config.BASE_URL,
                survey_id=config.TEST_SURVEY_ID,
        ) < 0:
            return self.error("Failed to delete CIR schema record after test.")

        return self.success("Successfully deleted CIR schema record after test.")

    def postprocess_worker(self) -> None:
        pass
