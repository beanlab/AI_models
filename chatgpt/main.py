from openai import OpenAI
import config
openAiClient = OpenAI(
    api_key = config.OPENAI_API_KEY,
    organization = config.OPENAI_ORGID
)
def main():
    Context =""
    while True:
        user_input = input("Enter your prompt: ")
        if user_input == "quit":
            print("Quitting now")
            break
        print(f'User: {user_input}')
        Context += f'User: {user_input}'
        AI_reponse = openAiClient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content":Context },
                  {"role": "user", "content":user_input}],
        max_tokens=150)
        print(f"AI: {AI_reponse.choices[0].message.content}")
        Context += f"GPT: {AI_reponse.choices[0].message.content}"
if __name__ == "__main__":
    main()
