class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    connection_string = "CONNECTION_STRING"
    server_name = "SERVER_NAME"
    server_instructions = "SERVER_INSTRUCTIONS"


class Defaults:
    test_type = "unit"
    http_port = "80"
    connection_string = "sqlite:///./.local/alchemy.db"
    server_name = "Relational Database Server"
    server_instructions = "This MCP server points to a relational database. It will be used to access the database, mainly to run SQL queries"
