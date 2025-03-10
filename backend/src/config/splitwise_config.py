from splitwise import Splitwise
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_splitwise_client():
    """
    Create and return a configured Splitwise client instance
    """
    return Splitwise(
        consumer_key=os.getenv("SPLITWISE_CONSUMER_KEY"),
        consumer_secret=os.getenv("SPLITWISE_CONSUMER_SECRET"),
        api_key=os.getenv("SPLITWISE_API_KEY")
    )
