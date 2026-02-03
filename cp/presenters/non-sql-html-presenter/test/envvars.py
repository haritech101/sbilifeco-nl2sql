class EnvVars:
    test_type = "TEST_TYPE"
    http_port = "HTTP_PORT"
    staging_host = "STAGING_HOST"
    web_page_path = "WEB_PAGE_PATH"
    template_path = "TEMPLATE_PATH"


class Defaults:
    test_type = "unit"  # or "integration" or "staging"
    http_port = "80"
    staging_host = "localhost"
    web_page_path = "/tmp/sbilifeco/html_pages/non-sql-answers.html"
    template_path = "/tmp/sbilifeco/templates/non-sql-answers-template.html"
