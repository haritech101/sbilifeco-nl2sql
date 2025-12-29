class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    staging_host = "STAGING_HOST"
    mcp_url = "MCP_URL"
    population_counter_proto = "POPULATION_COUNTER_PROTO"
    population_counter_host = "POPULATION_COUNTER_HOST"
    population_counter_port = "POPULATION_COUNTER_PORT"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port = "80"
    staging_host = "localhost"
    mcp_url = "http://localhost"
    population_counter_proto = "http"
    population_counter_host = "localhost"
    population_counter_port = "80"
