class EnvVars:
    db_id = "DB_ID"
    llm_proto = "LLM_PROTO"
    llm_host = "LLM_HOST"
    llm_port = "LLM_PORT"
    llm_template_file = "LLM_TEMPLATE_FILE"
    metadata_storage_proto = "METADATA_STORAGE_PROTO"
    metadata_storage_host = "METADATA_STORAGE_HOST"
    metadata_storage_port = "METADATA_STORAGE_PORT"
    num_questions = "NUM_QUESTIONS"
    num_variations = "NUM_VARIATIONS"


class Defaults:
    llm_proto = "http"
    llm_host = "localhost"
    llm_port = "80"
    llm_template_file = ".local/.llm-template.txt"
    metadata_storage_proto = "http"
    metadata_storage_host = "localhost"
    metadata_storage_port = "80"
    num_questions = "10"
    num_variations = "1"
