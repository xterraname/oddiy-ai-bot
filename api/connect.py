from together import Together
from config import TOGETHER_API_KEY


def get_client():
    client = Together(api_key=TOGETHER_API_KEY)
    
    return client
