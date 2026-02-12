from __future__ import annotations
from typing import Optional
from pprint import pprint, pformat
from os import getenv
from asyncio import run, create_task, as_completed
from dotenv import load_dotenv
from pydantic import BaseModel
from sbilifeco.models.base import Response

# Import other required contracts/modules here
import re
import json as json_module
from uuid import uuid4
from envvars import Defaults, EnvVars
from yaml import safe_load
from sbilifeco.cp.query_flow.http_client import QueryFlowHttpClient
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Preformatted,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


class QueryFlowBatchTest:
    def __init__(self):
        self.http_client: QueryFlowHttpClient
        self.query_flow_proto = getenv(
            EnvVars.query_flow_proto, Defaults.query_flow_proto
        )
        self.query_flow_host = getenv(EnvVars.query_flow_host, Defaults.query_flow_host)
        self.query_flow_port = int(
            getenv(EnvVars.query_flow_port, Defaults.query_flow_port)
        )
        self.questions_file = getenv(EnvVars.questions_file, Defaults.questions_file)
        self.db_id = getenv(EnvVars.db_id, Defaults.db_id)
        self.answers_file = getenv(EnvVars.answers_file, Defaults.answers_file)

    async def async_init(self, **kwargs) -> None:
        self.http_client = QueryFlowHttpClient()
        (
            self.http_client.set_proto(self.query_flow_proto)
            .set_host(self.query_flow_host)
            .set_port(self.query_flow_port)
        )

        self.doc = SimpleDocTemplate(
            self.answers_file,
            pagesize=A4,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Create custom styles for table content
        self.question_style = ParagraphStyle(
            "QuestionStyle",
            parent=styles["Normal"],
            fontSize=10,
            fontName="Helvetica",
            textColor=colors.black,
            leftIndent=8,
            rightIndent=8,
            spaceBefore=8,
            spaceAfter=8,
            leading=12,  # Line spacing
        )

        self.answer_style = ParagraphStyle(
            "AnswerStyle",
            parent=styles["Normal"],
            fontSize=9,
            fontName="Helvetica",
            textColor=colors.black,
            leftIndent=8,
            rightIndent=8,
            spaceBefore=8,
            spaceAfter=8,
            leading=11,  # Line spacing
            bulletIndent=12,  # Indent for bullet points
        )

        # Create table data
        self.table_data = [
            [
                Paragraph("<b>Question</b>", styles["Heading2"]),
                Paragraph("<b>Answer</b>", styles["Heading2"]),
            ]
        ]

    async def async_shutdown(self, **kwargs) -> None: ...

    async def run(self) -> None:
        with open(self.answers_file, "w") as f:
            f.write("# Answers\n\n")
            f.flush()

        with open(self.questions_file, "r") as f:
            _yaml = safe_load(f)

        questions = _yaml.get("questions", [])

        for i, question in enumerate(questions):
            print(f"Processing question {i+1}/{len(questions)}...")

            response = await self.http_client.query(self.db_id, uuid4().hex, question)
            answer = response.payload or response.message
            correctness = (
                "✅" if (response.payload and "```sql" in response.payload) else "❌"
            )
            print(f"Able to generate SQL: {correctness}")

            q_para = Paragraph(f"{i+1}. {question}", self.question_style)
            a_para = Paragraph(self.format_answer_text(answer), self.answer_style)

            self.table_data.append([q_para, a_para])

            table = Table(self.table_data, colWidths=[2.5 * inch, 5.0 * inch])

            table.setStyle(
                TableStyle(
                    [
                        # Header row styling
                        ("BACKGROUND", (0, 0), (-1, 0), colors.white),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 12),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        # Data rows styling
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                        ("FONTSIZE", (0, 1), (-1, -1), 9),
                        ("LEFTPADDING", (0, 1), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 1), (-1, -1), 8),
                        ("TOPPADDING", (0, 1), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 1), (-1, -1), 10),
                        # Grid and borders
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("LINEBELOW", (0, 0), (-1, 0), 2, colors.black),
                        # Alternating row colors
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.white],
                        ),
                    ]
                )
            )

            # Build the PDF
            elements = [table]
            self.doc.build(elements)

            print(
                f"Finished processing question {i+1}/{len(questions)}. Updated PDF report with latest results of question {i+1}.\n"
            )

    def format_answer_text(self, answer):
        """
        Format answer text preserving markdown structure exactly for PDF.
        """
        # First, let's preserve code blocks by replacing them with placeholders
        code_blocks = {}
        block_counter = 0

        # Extract and format SQL code blocks
        def extract_sql_block(match):
            nonlocal block_counter
            sql_content = match.group(1).strip()
            # Clean up SQL but preserve structure
            sql_lines = []
            for line in sql_content.split("\n"):
                cleaned_line = line.strip()
                if cleaned_line:
                    sql_lines.append(cleaned_line)

            # Join with spaces but break at major SQL keywords for readability
            sql_formatted = " ".join(sql_lines)

            # Smart truncation at SQL clause boundaries
            if len(sql_formatted) > 1000:
                break_points = [
                    " WHERE ",
                    " FROM ",
                    " JOIN ",
                    " ORDER BY ",
                    " GROUP BY ",
                    " LIMIT ",
                ]
                best_break = 1000
                for bp in break_points:
                    pos = sql_formatted.rfind(bp, 0, 1200)
                    if pos > 800:
                        best_break = pos + len(bp)
                        break
                sql_formatted = sql_formatted[:best_break] + "... [query continues]"

            placeholder = f"__SQL_BLOCK_{block_counter}__"
            code_blocks[placeholder] = (
                f'<br/><br/><b>SQL Query:</b><br/><font name="Courier" size="8">{sql_formatted}</font><br/><br/>'
            )
            block_counter += 1
            return placeholder

        # Extract and format JSON code blocks
        def extract_json_block(match):
            nonlocal block_counter
            json_content = match.group(1).strip()

            # Try to parse and re-format JSON for better readability
            try:
                parsed_json = json_module.loads(json_content)
                json_formatted = json_module.dumps(parsed_json, indent=2)
            except:
                # If not valid JSON, just clean up the formatting
                json_lines = []
                for line in json_content.split("\n"):
                    cleaned_line = line.strip()
                    if cleaned_line:
                        json_lines.append(cleaned_line)
                json_formatted = "\n".join(json_lines)

            placeholder = f"__JSON_BLOCK_{block_counter}__"
            code_blocks[placeholder] = (
                f'<br/><br/><b>JSON Data:</b><br/><font name="Courier" size="8">{json_formatted}</font><br/><br/>'
            )
            block_counter += 1
            return placeholder

        # Extract code blocks
        answer = re.sub(
            r"```sql\s*\n(.*?)\n```", extract_sql_block, answer, flags=re.DOTALL
        )
        answer = re.sub(
            r"```json\s*\n(.*?)\n```", extract_json_block, answer, flags=re.DOTALL
        )

        # Handle other markdown formatting
        # Convert bullet points (preserve hierarchy)
        answer = re.sub(r"^\* ", "• ", answer, flags=re.MULTILINE)
        answer = re.sub(r"^  \* ", "  • ", answer, flags=re.MULTILINE)
        answer = re.sub(r"^    \* ", "    • ", answer, flags=re.MULTILINE)

        # Convert bold text
        answer = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", answer)
        answer = re.sub(
            r"\*(.*?)\*(?!\*)", r"<i>\1</i>", answer
        )  # Italic, but not if it's part of **

        # Handle line breaks - preserve markdown structure
        # Convert double newlines to paragraph breaks
        answer = re.sub(r"\n\s*\n", "<br/><br/>", answer)
        # Convert single newlines to line breaks
        answer = re.sub(r"\n", "<br/>", answer)

        # Restore code blocks
        for placeholder, formatted_block in code_blocks.items():
            answer = answer.replace(placeholder, formatted_block)

        # Clean up extra whitespace
        answer = re.sub(r"<br/>(\s*<br/>)+", "<br/><br/>", answer)
        answer = re.sub(r"\s+", " ", answer)

        return answer.strip()


if __name__ == "__main__":
    load_dotenv()
    test = QueryFlowBatchTest()
    run(test.async_init())
    try:
        run(test.run())
    finally:
        run(test.async_shutdown())
