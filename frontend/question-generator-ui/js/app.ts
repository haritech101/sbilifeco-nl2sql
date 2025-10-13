import { Api } from "./api.js";

document.addEventListener("submit", async function (event) {
    event.preventDefault();

    const numQuestions = parseInt(
        (document.getElementById("num-questions") as HTMLInputElement)?.value
    );

    document.getElementById("container-generated-questions")!.innerText =
        await new Api().fetchQuestions(numQuestions);
});
