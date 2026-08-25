import random
from fastmcp import FastMCP

mcp = FastMCP(name = "local demo server")

@mcp.tool
def roll_dice(n_dice : int = 1) -> list[int]:
    '''Roll n_dice 6 sided and return the results'''
    return [random.randint(1,6) for _ in range(n_dice)]

@mcp.tool
def add_num(a:int,b:int) -> int:
    '''Add two numbers'''
    return a+b

if __name__ == "__main__":
    mcp.run()

# uv run fastmcp dev inspector mcp_server_local_demo.py --inspector-version 2.1.0 -> use this command to run the mcp inspector (test the server)

#  Command to run the server :  uv run fastmcp run mcp_server_local_demo.py