from api.chat import get_answer
from api.connect import get_client


def main():
    messages = [
        {
            "role": "system",
            "content": """Siz umumiy mavzular bo'yicha suhbat quradigan yordamchisiz.
Javobingiz faqat o‘zbek tilida bo‘lishi kerak.""",
        },
        {"role": "user", "content": "Hafta kunlarini sanab ber"},
    ]

    client = get_client()

    answer = get_answer(client, messages)

    print(answer)


main()
