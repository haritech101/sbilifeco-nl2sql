class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    http_port_unittest = "HTTP_PORT_UNITTEST"
    vertex_ai_region = "VERTEX_AI_REGION"
    vertex_ai_project_id = "VERTEX_AI_PROJECT_ID"
    vertex_ai_model = "VERTEX_AI_MODEL"


class Defaults:
    test_type = "unit"  # or "integration"
    http_port = "80"
    http_port_unittest = "80"
    vertex_ai_region = "us-central1"
    vertex_ai_model = "claude-sonnet-4"
