from openai import OpenAI
import config
import yaml
from pathlib import Path
from typing import TypedDict
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

Message = ChatCompletionMessageParam

class testcase:
    def __init__(self, user, bad,good):
        self.user = user
        self.bad = bad
        self.good = good

class TestInput(TypedDict):
    model: str
    prompt: list[Message]

openAiClient = OpenAI(
    api_key = config.OPENAI_API_KEY,
    organization = config.OPENAI_ORGID
)
def main():
    prompt = Path("./chatgpt/prompt/standard-rubber-duck.txt").read_text()
    with open("bad.yaml", "r") as file:
        data = yaml.safe_load(file)
    for convo_key, messages in data.items():  # Iterate over all conversations
        print(f"Conversation ID: {convo_key}")
        for message in messages:  # Iterate over messages in each conversation
            user_message = message.get('user', 'N/A')  # Get user message safely
            assistant_response = message.get('assistant', 'N/A')  # Get assistant response safely
            print(f"User: {user_message}")
            print(f"Assistant: {assistant_response}")
        print('-' * 20)  # Separator between conversations
    while True:
        user_input = input("Enter your prompt: ")
        if user_input == "quit":
            print("Quitting now")
            break
        print(f'User: {user_input}')
        Context += f'User: {user_input}'
        AI_reponse = openAiClient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content":prompt },
                  {"role": "user", "content":user_input}],
        max_tokens=150)
        print(f"AI: {AI_reponse.choices[0].message.content}")
        Context += f"GPT: {AI_reponse.choices[0].message.content}"
if __name__ == "__main__":
    main()
