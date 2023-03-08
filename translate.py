import time

import openai
import openai.error as openai_error
sk = "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"
openai.api_key = sk


# @policy A: 逐段翻译 风险度高 GPT极有可能返回错误的分段
def translate(segment):
    message = f"请帮我把下面的句子翻译成中文，请一句一句的翻译，并且不要修改任何句子之间的‘#’。\n{segment}"
    while True:
        try:
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are English-Chinese translator."
                                " You should translate sentence by sentence."
                                " Don't remove any '#' between sentences"},
                    {"role": "user", "content": message}
                ]
            )
            break
        except openai_error as e:
            print(e)

    return result["choices"][0]["message"]["content"]

# @policy B: 逐句翻译 无风险，但可能会丢失上下文信息，浪费 tokens，可能超出并发请求上限
def translate_by_sentence(sentence):
    message = f"把下面的句子翻译成中文:\n{sentence}"
    while True:
        try:
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": message}
                ],
                temperature=0.2
            )
            break
        except Exception as e:
            print(e)

    time.sleep(3)
    print(f"消耗 tokens: {result['usage']['total_tokens']}")
    print(result["choices"][0]["message"]["content"])

    return result["choices"][0]["message"]["content"]