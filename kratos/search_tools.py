from ddgs import DDGS
from langchain.tools import tool

@tool
def search_web(query: str="", max_results: int =5):
    """DDGS text metasearch.

    Args:
        query: text search query.
        max_results: maximum number of results. Defaults to 10.

    Returns:
        List of dictionaries with search results.
    """
    try:

        return DDGS().text(query=query, max_results=max_results)
    except Exception as ex:
        return {"status": "Failed at webserach", "msg": f"try again later {ex}"}


@tool
def search_news(query: str="", max_results: int =5):
    """DDGS news metasearch.

    Args:
        query: text search query.
        max_results: maximum number of results. Defaults to 10.

    Returns:
        List of dictionaries with search results.
    """
    try:
        return DDGS().news(query=query,max_results=max_results)
    except Exception as ex:
        return {"status": "Fail at searching news", "msg": f"try again later {ex}"}

SEARCH_TOOLS = [
    search_news,
    search_web
]