class EnvVars:
    test_type = "TEST_TYPE"
    query_flow_proto = "QUERY_FLOW_PROTO"
    query_flow_host = "QUERY_FLOW_HOST"
    query_flow_port = "QUERY_FLOW_PORT"
    staging_host = "STAGING_HOST"
    questions_file = "QUESTIONS_FILE"
    db_id = "DB_ID"
    answers_file = "ANSWERS_FILE"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    query_flow_proto = "http"
    query_flow_host = "localhost"
    query_flow_port = "80"
    staging_host = "localhost"
    questions_file = "./questions.yaml"
    db_id = "nb"
    answers_file = "./answers.pdf"
