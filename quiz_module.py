import json
import re

from gemini_client import generate_text


def generate_quiz(topic: str, num_questions: int = 5) -> list:

    prompt = f"""
Create exactly {num_questions} multiple-choice questions about "{topic}"
for a college computer science student.

Return ONLY valid JSON.
Do not use markdown.
Do not add ```json or ```.

The JSON must be an array.

Each object must contain exactly these fields:

{{
  "question": "Question text",
  "options": [
    "Option 1",
    "Option 2",
    "Option 3",
    "Option 4"
  ],
  "answer": "The exact correct option text",
  "explanation": "Short explanation of the correct answer"
}}

Important:
- Exactly 4 options for every question.
- The answer must exactly match one of the 4 options.
- Do not reveal the answer outside the JSON.
- Create different questions.
"""


    try:

        result = generate_text(
            prompt,
            temperature=0.4,
            max_output_tokens=3000
        )


        if not result:
            raise ValueError(
                "Empty response from Gemini"
            )


        result = result.strip()


        # Remove markdown code fences if Gemini adds them
        result = re.sub(
            r"^```json\s*",
            "",
            result,
            flags=re.IGNORECASE
        )

        result = re.sub(
            r"^```\s*",
            "",
            result
        )

        result = re.sub(
            r"\s*```$",
            "",
            result
        )

        result = result.strip()


        quiz = json.loads(result)


        if not isinstance(quiz, list):
            raise ValueError(
                "Gemini response is not a list"
            )


        cleaned_quiz = []


        for item in quiz:

            if not isinstance(item, dict):
                continue


            question = item.get("question")
            options = item.get("options")
            answer = item.get("answer")
            explanation = item.get(
                "explanation",
                ""
            )


            if not question:
                continue


            if (
                not isinstance(options, list)
                or len(options) != 4
            ):
                continue


            options = [
                str(option)
                for option in options
            ]


            answer = str(answer)


            if answer not in options:
                continue


            cleaned_quiz.append({

                "question": str(question),

                "options": options,

                "answer": answer,

                "explanation": str(
                    explanation
                )

            })


        if len(cleaned_quiz) >= num_questions:

            return cleaned_quiz[:num_questions]


        if cleaned_quiz:

            return cleaned_quiz


    except Exception as exc:

        print(
            "Quiz generation error:",
            exc
        )


    # Safe fallback
    return [

        {
            "question": f"What is {topic}?",

            "options": [
                "A programming concept",
                "A type of hardware",
                "A computer virus",
                "A network cable"
            ],

            "answer": "A programming concept",

            "explanation":
                f"{topic} is an important "
                "computer science topic."
        }

        for _ in range(num_questions)

    ]