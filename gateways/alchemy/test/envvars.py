class EnvVars:
    test_type = "TEST_TYPE"
    connection_string: str = "CONNECTION_STRING"


class Defaults:
    test_type = "unit"  # or "integration"
    connection_string: str = "sqlite+pysqlite:///:memory:"
