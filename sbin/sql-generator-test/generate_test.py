from asyncio import run
from datetime import datetime
from sbilifeco.cp.query_flow.http_client import QueryFlowHttpClient
from itertools import islice
import pandas as pd
from os import getenv
from dotenv import load_dotenv


class QueryGeneratorTester:
    async def start(self) -> None:
        client = QueryFlowHttpClient()
        (client.set_proto("http").set_host("localhost").set_port(11200))

        session_response = await client.start_session()
        if not session_response.is_success:
            print(session_response.message)
            return

        session_id = session_response.payload
        if not session_id:
            print("Session ID is inexplicably empty")
            return

        metric = ""
        max_queries = int(getenv("MAX_QUERIES", "10"))

        qa_list = []
        with open(
            f".local/questions{f"_{metric}" if metric else ""}.txt"
        ) as file_of_questions:
            time_tag = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            with open(
                f".local/answers{f"_{metric}" if metric else ""}_{time_tag}.md", "w"
            ) as md_file:
                # sequence_tag = 1
                questions = islice(file_of_questions, max_queries)

                for i, question in enumerate(questions, 1):
                    print(f"Question {i}: {question}".strip())

                    query_response = await client.query(
                        getenv("DB_ID", ""),
                        session_id,
                        question.strip(),
                        with_thoughts=False,
                    )
                    if not query_response.is_success:
                        print(query_response.message)
                        continue
                    if not query_response.payload:
                        print("Query response payload is inexplicably empty")
                        continue

                    md_file.write(f"### Q{i}: {question.strip()}\n\n")
                    md_file.write(f"**A{i}:**\n\n{query_response.payload.strip()}\n\n")
                    md_file.flush()

                    qa_list.append(
                        {
                            "#": i,
                            "Question": question.strip(),
                            "Answer": query_response.payload.strip(),
                        }
                    )
                    print("Answer received and saved")

                    await client.reset_session(session_id)

        pd.DataFrame(qa_list).to_excel(
            # f"answers_{time_tag}_{sequence_tag}.xlsx", index=False
            f".local/answers{f"_{metric}" if metric else ""}_{time_tag}.xlsx",
            index=False,
        )


if __name__ == "__main__":
    load_dotenv()
    run(QueryGeneratorTester().start())
