# from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

# load_dotenv()

OPENAI_API_KEY = st.secrets.OPENAI_API_KEY

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, api_key=OPENAI_API_KEY)

system_prompt = f''' You are a query formatter which helps format queries from user inputs, there are three things that you need to extract from any given query:
1. Object (Required) can be one of  ['phone', 'headphones', 'glasses', 'wallet', 'keys', 'chargers', 'book', 'watch', 'bottle', 'pen']
2. Start datetime (Optional) formatted like ISO Format e.g. 2024-05-27T10:55:20.034873
3. End datetime (Optional) formatted like ISO Format e.g. 2024-05-27T10:55:20.034873

You will be given the current date and time and user can ask time relative queries, like where you saw my phone in last 1 hour, then output should include timestamp starting from current hour -1 to current hour as start datetime and end datetime, etc
If there's no mention of time, just return object and start_datetime or end_datetime can be null.

Datetime now is {datetime.now().isoformat()}
'''+'''
### Output format ###
{
    "object":"phone",
    "start_datetime": "2024-05-27T10:55:20.034873",
    "end_datetime": "2024-05-27T10:55:20.034873"
}
'''

def fetch_from_query(user_query):
    res = llm.invoke(
    [
        SystemMessage(
            content=system_prompt
        ),
        HumanMessage(
            content=user_query
        )
    ]
    )
    return res.content