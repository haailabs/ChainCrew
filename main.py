import os
import requests
import json
import asyncio
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from geckoterminal_py import GeckoTerminalAsyncClient


llm = ChatGroq(
    temperature=0, 
    groq_api_key = "your_key", 
    model_name="mixtral-8x7b-32768"
)

# Fetch the latest price action
async def fetch_ohlcv():
    client = GeckoTerminalAsyncClient()
    data = await client.get_ohlcv("base", "0x7F12d13B34F5F4f0a9449c16Bcd42f0da47AF200", "12h")
    return data

# Fetch the source code of the contract
'''
def fetch_contract_sourcecode():
    key = "your_etherscan_api_key"
    url = "https://api.etherscan.io/api"
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": "0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413",
        "apikey": key
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == '1' and data['message'] == 'OK':
        return data['result'][0]['SourceCode']
    else:
        return "Error: " + data['result']
'''
def fetch_contract_sourcecode():
    import requests

    key = "YourApiKeyToken"
    url = "https://api.basescan.org/api"
    params = {
        "module": "contract",
        "action": "getsourcecode",
        "address": "0x7F12d13B34F5F4f0a9449c16Bcd42f0da47AF200",
        "apikey": "your_key"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == '1' and data['message'] == 'OK':
        return data['result'][0]['SourceCode']
    else:
        return "Error: " + data['result']



# Asynchronous function to get both data
async def get_data():
    price_action = await fetch_ohlcv()
    source_code = fetch_contract_sourcecode()
    return price_action, source_code

# Define your agents with roles and goals
engineer = Agent(
    role='Security Engineer',
    goal='Analyze the smart contract for security issues and potential backdoors.',
    backstory="""You are a highly skilled security engineer specializing in smart contract auditing.""",
    verbose=True,
    llm=llm
)

financial_analyst = Agent(
    role='Financial Analyst',
    goal='Analyze the latest price action data for the token.',
    backstory="""You are an experienced financial analyst with expertise in cryptocurrency markets.""",
    verbose=True,
    llm=llm
)

report_compiler = Agent(
    role='Report Compiler',
    goal='Compile the analyses from the security engineer and financial analyst into a comprehensive report.',
    backstory="""You are a professional report writer skilled at compiling technical and financial analyses into coherent reports.""",
    verbose=True,
    llm=llm
)

# Create tasks for your agents
def create_tasks(price_action, source_code):
    task1 = Task(
        description=f"""Analyze the provided smart contract source code for security issues and potential backdoors:
        {source_code}""",
        expected_output="A detailed security analysis report.",
        agent=engineer
    )

    task2 = Task(
        description=f"""Analyze the provided price action data for the token and provide insights on its financial performance:
        {price_action}""",
        expected_output="A detailed financial analysis report.",
        agent=financial_analyst
    )

    task3 = Task(
        description=f"""Compile the security and financial analyses into a comprehensive report. 
        Security Analysis Findings: {{task1_output}}
        Financial Analysis Findings: {{task2_output}}""",
        expected_output="A comprehensive report combining both the security and financial analyses.",
        agent=report_compiler
    )

    return [task1, task2, task3]

# Fetch data and then kick off the crew tasks
async def main():
    price_action, source_code = await get_data()

    # Create tasks with the fetched data
    tasks = create_tasks(price_action, source_code)

    # Instantiate your crew with a sequential process
    crew = Crew(
        agents=[engineer, financial_analyst, report_compiler],
        tasks=tasks,
        verbose=2, # You can set it to 1 or 2 to different logging levels
    )

    # Start the crew
    result = crew.kickoff()
    print(result)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
