class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    staging_host = "STAGING_HOST"
    prompt_file = "PROMPT_FILE"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port = "80"
    staging_host = "localhost"
