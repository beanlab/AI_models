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

def report(testcase,test_input,score_good,score_bad,response_content):
    details = {
    "Test case": testcase['messages'],
    "Test input": test_input,
    "Good examples input": testcase['good'],
    "Score good": score_good,
    "Bad examples input": testcase['bad'],  # Fix: Changed key to 'Bad examples input'
    "Score bad": score_bad,
    "Response": response_content
}

# Write the dictionary to the file using json.dump
    with open(f"report/{testcase['name']}{test_input['name']}_details.txt", "a") as f:
        json.dump(details, f, indent=4)  # `indent=4` makes the JSON output more readable
        f.write("\n")

    data = {
        "Test case": testcase['messages'],
        "Mean difference": mean(score_good) - mean(score_bad)
    }

    # Write the dictionary to the file using json.dump
    with open(f"report/{testcase['name']}{test_input['name']}_simple.txt", "a") as f:
        json.dump(data, f)
        f.write("\n")



def mean(numbers):
    return sum(numbers) / len(numbers)   

def main(test_input_file: Path, test_directory: Path):

    for test_input_file in test_input_file.glob(''):
        if test_input_file.endswith('.yaml'):
            test_input: TestInput = yaml.safe_load(test_input_file.read_text())
        test_input: TestInput = json.loads(test_input_file.read_text())
    # Read test cases
        for test_case_file in test_directory.glob('*.json'):
            good_list=[]
            bad_list=[]
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
                good_list.append(float(np.dot(embedding.data[0].embedding, goodscore.data[0].embedding)))
            for bad in test_case['bad']:
                badscore=client.embeddings.create(input=bad,model='text-embedding-3-small')
                bad_list.append(float(np.dot(embedding.data[0].embedding, badscore.data[0].embedding)))
            # Report
            report(test_case, test_input, good_list, bad_list,response_content)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("test_input", type=Path,nargs='?', default=Path('test_input'))
    parser.add_argument("test_directory", type=Path,nargs='?', default=Path('test_directory'))
    args = parser.parse_args()
    main(args.test_input, args.test_directory)
