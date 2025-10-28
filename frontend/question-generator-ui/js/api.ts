export class Api {
    static BASE_URL = "http://localhost:11216";

    public async fetchQuestions(numQuestions: number): Promise<string> {
        console.log("Fetching questions from API...");

        const httpResponse = await fetch(
            `${Api.BASE_URL}/generate-requests?num_questions=${numQuestions}`
        );

        console.log("HTTP response received from API.");

        if (!httpResponse.ok) {
            return httpResponse.text();
        }

        const apiResponse = await httpResponse.json();

        if (apiResponse.is_success !== true) {
            return apiResponse.message;
        }

        return apiResponse.payload;
    }
}
