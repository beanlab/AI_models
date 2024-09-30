import json
from pathlib import Path
from typing import TypedDict
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

client = OpenAI()


Message = ChatCompletionMessageParam


class TestCase(TypedDict):
    messages: list[Message]
    good: list[str]
    bad: list[str]


class TestInput(TypedDict):
    model: str
    prompt: list[Message]


def main(test_input_file: Path, test_directory: Path):
    test_input: TestInput = json.loads(test_input_file.read_text())

    # Read test cases
    for test_case_file in test_directory.glob('*.json'):
        test_case: TestCase = json.loads(test_case_file.read_text())

        # Get the completion
        resp = client.chat.completions.create(
            model=test_input['model'],
            messages=test_input['prompt'] + test_case['messages']
        )

        # Embed response
        response_content = resp.choices[0].message.content
        embedding = embed(response_content)

        # Score
        score = score_response(embedding, test_case['good'], test_case['bad'])

        # Report
        report(test_case, score)
