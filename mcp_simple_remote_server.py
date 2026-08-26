from fastmcp import FastMCP
import random
import json

mcp = FastMCP(name="Remote-Calculator")

@mcp.tool
def add_num(a:int , b:int) -> int:
    '''Add the 2 numbers'''
    return a + b

@mcp.tool
def generate_num(min_val:int , max_val :int):
    '''generate a random number between min_val and max_val'''
    return random.randint(min_val,max_val)

@mcp.resource("info://server")
def server_info() -> str:
    '''Get the Server info'''
    info = {
        'name' : 'Simple Calculator Server',
        'version' : '1.0.0',
        'description' : 'A simple MCP server to perfrom basic calculations',
        'tools' : ['add_num','generate_num'],
        'author' : 'Avanindra' 
    }

    return json.dumps(info,indent=2)

if __name__ == "__main__":
    mcp.run(transport='http', host = "0.0.0.0" , port = 8000)


# Commands to interact with the remote server
# To start the server: uv run python mcp_simple_remote_server.py (fastmcp run does not execute the __main__ block)
# to validate with inspector : npx -y @modelcontextprotocol/inspector@2.1.0 --server-url http://127.0.0.1:8000/mcp --transport http (make sure to provide the exact port)
# If using fastmcp run, explicitly specify the transport and port: fastmcp run mcp_simple_remote_server.py --transport http --port 8000