from __future__ import annotations

from pathlib import Path
from pprint import pprint
from typing import Sequence

# Import other required contracts/modules here
from jinja2 import Environment, FileSystemLoader, Template
from sbilifeco.boundaries.non_sql_notify_flow import INonSqlPresenter
from sbilifeco.boundaries.query_flow import NonSqlAnswer


class NonSqlHtmlPresenter(INonSqlPresenter):
    def __init__(self):
        self.web_page_path: str
        self.template_path: str
        self.jinja_env: Environment
        self.jinja_template: Template

    def set_web_page_path(self, path: str) -> NonSqlHtmlPresenter:
        self.web_page_path = path
        return self

    def set_template_path(self, path: str) -> NonSqlHtmlPresenter:
        self.template_path = path
        return self

    async def async_init(self) -> None:
        full_path = Path(self.template_path)
        folder = full_path.parent
        file = full_path.name

        self.jinja_env = Environment(loader=FileSystemLoader(folder), autoescape=True)
        self.jinja_template = self.jinja_env.get_template(file)

    async def async_shutdown(self) -> None: ...

    async def present(self, answers: Sequence[NonSqlAnswer]) -> None:
        try:
            print("Creating HTML from template", flush=True)
            html = self.jinja_template.render(answers=answers)
            print(
                f"Writing generated HTML of {len(html)} characters to {self.web_page_path}",
                flush=True,
            )
            with open(self.web_page_path, "w") as html_file:
                html_file.write(html)
                html_file.flush()
            print(
                f"{self.web_page_path} now has the latest non-SQL answers.", flush=True
            )
        except Exception as e:
            pprint(f"Error while presenting non SQL answers in a web page: {e}")
