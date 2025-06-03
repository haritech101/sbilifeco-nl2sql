from pyexpat import model


class EnvVars:
    http_port = "HTTP_PORT"
    llm_model = "LLM_MODEL"
    api_key = "API_KEY"


class Defaults:
    http_port = "80"
    llm_model = "codellama"
