import json
import os
from pathlib import Path
from typing import TypedDict
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import argparse
import numpy as np
import yaml
client = OpenAI()


Message = ChatCompletionMessageParam


class TestCase(TypedDict):
    name : str
    messages: list[Message]
    good: list[str]
    bad: list[str]


class TestInput(TypedDict):
    name : str
    model: str
    prompt: list[Message]

class reportType(TypedDict):
    test_case:TestCase
    test_input : TestInput
    good_list: list[float]
    bad_list: list[float]
    response_content: str

def report(report_list):
    detail_list = []

    for report_item in report_list:
        details = {
            "Test case": report_item["test_case"]['messages'],
            "Test input": report_item["test_input"],
            "Good examples input": report_item["test_case"]['good'],
            "Score good": report_item['good_list'],
            "Bad examples input": report_item["test_case"]['bad'],  # Fix: Changed key to 'Bad examples input'
            "Score bad": report_item["bad_list"],
            "Response": report_item["response_content"],
            "Mean difference": round(mean(report_item["good_list"]) - mean(report_item["bad_list"]), 3),
            "Max good": max(report_item["good_list"]),
            "Max bad": max(report_item["bad_list"])
        }
        detail_list.append(details)

        # Create the directory if it doesn't exist
    new_dir = Path("report/")
    new_dir.mkdir(exist_ok=True)

    # Write each report to a separate JSON file
    filename = f"report/{report_item['test_input']['name']}_details.json"
    with open(filename, "w") as f:
        json.dump(detail_list, f, indent=4)




def mean(numbers):
    return round(sum(numbers) / len(numbers),3)   

def main(test_input_file: Path, test_directory: Path):

    for test_input_file in test_input_file.glob("*"):
        if test_input_file.suffix == ('.yaml'):
            test_input: TestInput = yaml.safe_load(test_input_file.read_text())
        else:
            test_input: TestInput = json.loads(test_input_file.read_text())
    # Read test cases
        report_list=[]
        for test_case_file in test_directory.glob('*.json'):
            good_list=[]
            bad_list=[]
            if test_case_file.suffix == ('.yaml'):
                test_case: TestCase = yaml.safe_load(test_case_file.read_text())
            else:
                test_case: TestCase = json.loads(test_case_file.read_text())

            # Get the completion
            resp = client.chat.completions.create(
                model=test_input['model'],
                messages=test_input['prompt'] + test_case['messages']
            )

            # Embed response
            response_content = resp.choices[0].message.content
            embedding = client.embeddings.create(input=response_content,model='text-embedding-3-small')
            for good in test_case['good']:
                goodscore= client.embeddings.create(input=good,model='text-embedding-3-small')
                good_list.append(round(float(np.dot(embedding.data[0].embedding, goodscore.data[0].embedding)),3))
            for bad in test_case['bad']:
                badscore=client.embeddings.create(input=bad,model='text-embedding-3-small')
                bad_list.append(round(float(np.dot(embedding.data[0].embedding, badscore.data[0].embedding)),3))
            # Report
            report_item = reportType(
                test_case=test_case,
                test_input=test_input,
                good_list=good_list,
                bad_list=bad_list,
                response_content=response_content)
            report_list.append(report_item)
        report(report_list)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("test_input", type=Path,nargs='?', default=Path('test_input'))
    parser.add_argument("test_directory", type=Path,nargs='?', default=Path('test_directory'))
    args = parser.parse_args()
    main(args.test_input, args.test_directory)
