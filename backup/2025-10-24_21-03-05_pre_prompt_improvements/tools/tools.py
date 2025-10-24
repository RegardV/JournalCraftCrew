from crewai.tools import BaseTool
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from typing import Dict
from utils import log_debug

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

def duckdb_tool(query: str) -> str:
    """Execute a DuckDB query (placeholder implementation)."""
    result = f"DuckDB result for {query}"
    log_debug(f"DuckDB query executed: {query}, result: {result}")
    return result

def analyze_sentiment(text: str) -> Dict[str, float]:
    """Analyze sentiment of text using NLTK VADER."""
    try:
        sid = SentimentIntensityAnalyzer()
        result = sid.polarity_scores(text)
        log_debug(f"Sentiment analyzed for text: {text[:50]}..., result: {result}")
        return result
    except Exception as e:
        log_debug(f"Error in analyze_sentiment: {e}")
        return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}

class DuckDBTool(BaseTool):
    name: str = "duckdb_tool"
    description: str = "Execute DuckDB queries for data coordination and management"
    def _run(self, query: str) -> str:
        return duckdb_tool(query)

class SentimentAnalysisTool(BaseTool):
    name: str = "analyze_sentiment"
    description: str = "Analyze the sentiment of text to ensure a positive and supportive tone"
    def _run(self, text: str) -> Dict[str, float]:
        return analyze_sentiment(text)

class BlogSummarySearchTool(BaseTool):
    name: str = "blog_summary_search"
    description: str = "Find and reformulate blog post summaries for a themed guide"
    def _run(self, query: str) -> str:
        full_data = [
            {"original": f"Blog X on {query}", "reformulated": f"Start {query.split(' for ')[1] if ' for ' in query else query} anytime for focus"},
            {"original": f"Blog Y on {query}", "reformulated": f"Weekday {query.split(' for ')[1] if ' for ' in query else query} eases tension"},
            {"original": f"Blog Z on {query}", "reformulated": f"Weekend {query.split(' for ')[1] if ' for ' in query else query} refreshes"}
        ]
        result = "Summary: " + "; ".join([item["reformulated"] for item in full_data[:3]])
        log_debug(f"Blog summary search for {query}: {result}")
        return result