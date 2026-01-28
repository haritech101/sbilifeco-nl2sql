class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    staging_host = "STAGING_HOST"
    kafka_url = "KAFKA_URL"
    consumer_name = "CONSUMER_NAME"
    answer_timeout = "ANSWER_TIMEOUT"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port = "80"
    staging_host = "localhost"
    kafka_url = "localhost:9092"
    consumer_name = "non-sql-answers-consumer"
    answer_timeout = "2"
