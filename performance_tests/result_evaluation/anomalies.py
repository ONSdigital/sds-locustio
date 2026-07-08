from typing import Final, TypedDict

REQUEST_COUNT_ANOMALY: Final[str] = "request_count_anomaly"
FAIL_RATIO_EXCEEDED_ANOMALY: Final[str] = "fail_ratio_exceeded_anomaly"
AVG_RESPONSE_TIME_EXCEEDED_ANOMALY: Final[str] = "avg_response_time_exceeded_anomaly"


class Anomaly(TypedDict):
    """
    A TypedDict to represent the anomaly logs.
    """
    name: str
    logging: str


ANOMALIES: Final[dict[str, Anomaly]] = {
    REQUEST_COUNT_ANOMALY: {
        "name": REQUEST_COUNT_ANOMALY,
        "logging": "Performance Test request count is abnormal."
    },
    FAIL_RATIO_EXCEEDED_ANOMALY: {
        "name": FAIL_RATIO_EXCEEDED_ANOMALY,
        "logging": "Performance Test failure count exceeded threshold."
    },
    AVG_RESPONSE_TIME_EXCEEDED_ANOMALY: {
        "name": AVG_RESPONSE_TIME_EXCEEDED_ANOMALY,
        "logging": "Performance Test average response time exceeded threshold."
    }
}
