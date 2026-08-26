import asyncio
import json
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from dotenv import load_dotenv

load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent

SERVERS = {
    "local_demo": {
        "transport": "stdio",
         "command": "uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            str(PROJECT_DIR / "mcp_server_local_demo.py")
        ]
    },
    "expense_tracker": {
            "transport": "stdio",
            "command": "uv",
            "args": [
                "run",
                "fastmcp",
                "run",
                str(PROJECT_DIR / "mcp_expense_tracker_remote_server.py")
            ]
        }
}

async def main():

    client = MultiServerMCPClient(SERVERS)

    tools = await client.get_tools()

    named_tool = {} 

    for tool in tools :
        named_tool[tool.name] = tool
    
    llm = ChatOpenAI()

    llm_with_tools = llm.bind_tools(tools=tools)

    # query = '''
    #         What is the capital of India ? and 
    #         What is the addition of 324 and 615 ? and
    #         roll 8 6-sided dice randomly and give me the result.
    #     '''
    query = '''add an expense of 10000 for campusx insider membership for the month of July 2026 which will help me learn new skills.'''

    response = await llm_with_tools.ainvoke(query)

    if not getattr(response,'tool_calls',None):
        print('LLM Reply : ',response.content)
        return

    # ************************************TOOLS*************************************
    tool_messages = []

    for tool in response.tool_calls :
        selected_tool = tool['name']

        selected_tool_args = tool['args'] or {}

        selected_tool_id = tool['id']

        # ******************************Invoke Tools **************************************
        tool_result = await named_tool[selected_tool].ainvoke(selected_tool_args)

        tool_message = ToolMessage(content=json.dumps(tool_result),tool_call_id = selected_tool_id)

        tool_messages.append(tool_message)

    final_response = await llm_with_tools.ainvoke(
        [HumanMessage(content=query), response, *tool_messages]
    )

    print("Final Response : ",final_response.content)

if __name__ == "__main__":
    asyncio.run(main())