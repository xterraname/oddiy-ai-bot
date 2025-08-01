from typing import List
from together import Client
from together.types import ChatCompletionResponse


def get_answer(client: Client, messages: List[dict]):

    answer: ChatCompletionResponse = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", messages=messages
    )

    content = answer.choices[0].message.content

    return content
