class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    staging_host = "STAGING_HOST"
    kafka_url = "KAFKA_URL"
    query_flow_port = "QUERY_FLOW_PORT"
    max_items = "MAX_ITEMS"
    non_sql_answer_repo_proto = "NON_SQL_ANSWER_REPO_PROTO"
    non_sql_answer_repo_host = "NON_SQL_ANSWER_REPO_HOST"
    non_sql_answer_repo_port = "NON_SQL_ANSWER_REPO_PORT"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port = "80"
    staging_host = "localhost"
    kafka_url = "localhost:9092"
    query_flow_port = "80"
    max_items = "25"
    non_sql_answer_repo_proto = "http"
    non_sql_answer_repo_host = "localhost"
    non_sql_answer_repo_port = "80"
