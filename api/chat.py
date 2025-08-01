from typing import List
from together import Client
from together.types import ChatCompletionResponse

import config


def get_answer(client: Client, messages: List[dict]):

    answer: ChatCompletionResponse = client.chat.completions.create(
        model=config.TOGETHER_MODEL, messages=messages, max_tokens=1300
    )

    content = answer.choices[0].message.content

    return content
