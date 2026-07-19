from typing import Any, List, Dict, Optional
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from medrxiv_web_search import search_key_words, search_advanced, doi_get_medrxiv_metadata

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize FastMCP server
mcp = FastMCP("medrxiv")

@mcp.tool()
async def search_medrxiv_key_words(key_words: str, num_results: int = 10) -> List[Dict[str, Any]]:
    logging.info(f"Searching for articles with key words: {key_words}, num_results: {num_results}")
    """
    Search for articles on medRxiv using key words.

    Args:
        key_words: Search query string
        num_results: Number of results to return (default: 10)

    Returns:
        List of dictionaries containing article information
    """
    try:
        results = await asyncio.to_thread(search_key_words, key_words, num_results)
        return results
    except Exception as e:
        return [{"error": f"An error occurred while searching: {str(e)}"}]

@mcp.tool()
async def search_medrxiv_advanced(
    term: Optional[str] = None,
    title: Optional[str] = None,
    author1: Optional[str] = None,
    author2: Optional[str] = None,
    abstract_title: Optional[str] = None,
    text_abstract_title: Optional[str] = None,
    section: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    num_results: int = 10
) -> List[Dict[str, Any]]:
    logging.info(f"Performing advanced search with parameters: {locals()}")
    """
    Perform an advanced search for articles on medRxiv.

    Args:
        term: General search term
        title: Search in title
        author1: First author
        author2: Second author
        abstract_title: Search in abstract and title
        text_abstract_title: Search in full text, abstract, and title
        section: Section of medRxiv
        start_date: Start date for search range (format: YYYY-MM-DD)
        end_date: End date for search range (format: YYYY-MM-DD)
        num_results: Number of results to return (default: 10)

    Returns:
        List of dictionaries containing article information
    """
    try:
        results = await asyncio.to_thread(
            search_advanced,
            term, title, author1, author2, abstract_title, text_abstract_title,
            section, start_date, end_date, num_results
        )
        return results
    except Exception as e:
        return [{"error": f"An error occurred while performing advanced search: {str(e)}"}]

@mcp.tool()
async def get_medrxiv_metadata(doi: str) -> Dict[str, Any]:
    logging.info(f"Fetching metadata for DOI: {doi}")
    """
    Fetch metadata for a medRxiv article using its DOI.

    Args:
        doi: DOI of the article

    Returns:
        Dictionary containing article metadata
    """
    try:
        metadata = await asyncio.to_thread(doi_get_medrxiv_metadata, doi)
        return metadata if metadata else {"error": f"No metadata found for DOI: {doi}"}
    except Exception as e:
        return {"error": f"An error occurred while fetching metadata: {str(e)}"}

if __name__ == "__main__":
    import os
    logging.info("Starting medRxiv MCP server")
    # Native transport switch (fork addition): MCP_TRANSPORT=http runs a single
    # long-lived streamable-HTTP server (one process, no per-session supergateway
    # child spawn) on MCP_HOST:MCP_PORT at /mcp; default stdio for per-worker use.
    _transport = os.getenv("MCP_TRANSPORT", "stdio")
    if _transport in ("http", "streamable-http"):
        mcp.settings.host = os.getenv("MCP_HOST", "127.0.0.1")
        mcp.settings.port = int(os.getenv("MCP_PORT", "8000"))
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
