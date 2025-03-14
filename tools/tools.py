#tools/tools.py
from crewai.tools import BaseTool
from config.settings import TESTING_MODE
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from typing import Dict, List
import os
from fpdf import FPDF

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

def duckdb_tool(query: str) -> str:
    """Execute a DuckDB query (placeholder implementation)."""
    return f"DuckDB result for {query}"

def analyze_sentiment(text: str) -> Dict[str, float]:
    """Analyze sentiment of text using NLTK VADER."""
    try:
        sid = SentimentIntensityAnalyzer()
        return sid.polarity_scores(text)
    except Exception as e:
        print(f"Error in analyze_sentiment: {e}")
        return {"neg": 0.0, "neu": 1.0, "pos": 0.0, "compound": 0.0}

def mock_image_references(topic: str) -> List[str]:
    """Generate mock image references for a topic."""
    if TESTING_MODE:
        return [f"Image of {topic} in a calm setting", f"Infographic about {topic}"]
    return [f"Detailed image of {topic} with annotations", f"Professional chart on {topic} benefits"]

def create_pdf(content: Dict[str, any], output_path: str) -> str:
    """Generate a PDF from content and save it to output_path."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=content.get("title", "Untitled Course"), ln=True, align="C")
    pdf.multi_cell(0, 10, txt=content.get("intro", ""))
    for day in content.get("days", []):
        pdf.add_page()
        pdf.multi_cell(0, 10, txt=day.get("pre_writeup", ""))
        pdf.add_page()
        pdf.cell(0, 10, txt=day.get("prompt", ""), ln=True)
        for _ in range(day.get("lines", 25)):
            pdf.cell(0, 5, txt="____________________", ln=True)
    pdf.output(output_path)
    return output_path

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

class ImageReferencesTool(BaseTool):
    name: str = "mock_image_references"
    description: str = "Generate relevant image references for course content"
    def _run(self, topic: str) -> List[str]:
        return mock_image_references(topic)

class PDFCreatorTool(BaseTool):
    name: str = "create_pdf"
    description: str = "Generate professionally formatted PDF documents from course content"
    def _run(self, content: Dict[str, any], output_path: str = "output/course.pdf") -> str:
        return create_pdf(content, output_path)

class BlogSummarySearchTool(BaseTool):
    name: str = "blog_summary_search"
    description: str = "Find and reformulate blog post summaries for a 4-week themed guide with two-page spreads"
    def _run(self, query: str) -> str:
        if TESTING_MODE:
            full_data = [
                {"original": f"Blog says {query} books suggest starting anytime builds habit", 
                 "reformulated": "Kicking off {query} journaling anytime sets the pace, blogs note"},
                {"original": f"Blog notes {query} guides use weekday prompts for stress", 
                 "reformulated": "Weekday {query} writing lightens your load, per blogs"},
                {"original": f"Blog highlights {query} weekend reflection for calm", 
                 "reformulated": "Weekend {query} prompts bring peace, blogs suggest"},
                {"original": f"Blog emphasizes {query} commitment boosts success", 
                 "reformulated": "Committing to {query} journaling fuels growth, per blogs"}
            ]
        else:
            full_data = [
                {"original": f"Blog X on {query}", "reformulated": f"Start {query} anytime for focus"},
                {"original": f"Blog Y on {query}", "reformulated": f"Weekday {query} eases tension"},
                {"original": f"Blog Z on {query}", "reformulated": f"Weekend {query} refreshes"},
                {"original": f"Blog W on {query}", "reformulated": f"Commitment to {query} empowers"}
            ]
        # Save full data outside tool (agent responsibility)
        return "Summary: " + "; ".join([item["reformulated"] for item in full_data[:3]])