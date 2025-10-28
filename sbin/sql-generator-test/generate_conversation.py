from asyncio import run
from datetime import datetime
from sbilifeco.cp.query_flow.http_client import QueryFlowHttpClient


class QueryGeneratorTester:
    async def start(self) -> None:
        client = QueryFlowHttpClient()
        (client.set_proto("http").set_host("localhost").set_port(11204))

        session_response = await client.start_session()
        if not session_response.is_success:
            print(session_response.message)
            return

        session_id = session_response.payload
        if not session_id:
            print("Session ID is inexplicably empty")
            return

        qa_list = []
        with open("conversation.txt") as file_of_questions:
            time_tag = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            with open(f"answers_conversation_{time_tag}.md", "w") as md_file:
                for i, question in enumerate(file_of_questions, 1):
                    print(f"Question {i}: {question}".strip())

                    query_response = await client.query(
                        "ed0d5b22-2d57-41df-a98d-a5f9ddf92a38",
                        session_id,
                        question.strip(),
                        with_thoughts=True,
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


if __name__ == "__main__":
    run(QueryGeneratorTester().start())
