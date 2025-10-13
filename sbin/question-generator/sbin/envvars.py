class EnvVars:
    conn_string = "CONN_STRING"
    llm_proto = "LLM_PROTO"
    llm_host = "LLM_HOST"
    llm_port = "LLM_PORT"
    http_listen_port = "HTTP_LISTEN_PORT"


class Defaults:
    conn_string = "sqlite:///./test.db"
    llm_proto = "http"
    llm_host = "localhost"
    llm_port = "80"
    http_listen_port = "80"
