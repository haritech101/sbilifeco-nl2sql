class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    staging_host = "STAGING_HOST"
    kafka_url = "KAFKA_URL"
    max_items = "MAX_ITEMS"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port = "80"
    staging_host = "localhost"
    kafka_url = "localhost:9092"
    max_items = "25"
