from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SawftLaunch Identity")


@mcp.tool()
def get_design_identity() -> str:
    """Fetch a design identity (fonts + color palette) from SawftLaunch."""
    return "test identity: it works."


if __name__ == "__main__":
    mcp.run()
