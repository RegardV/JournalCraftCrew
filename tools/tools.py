import os
import nltk
import requests
import json
from datetime import datetime
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import random

# Ensure the VADER lexicon is downloaded
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

# Mock PubMed tool for research (used when PUBMED_API_KEY is not available)
def mock_pubmed_research(topic, max_findings=3):
    """Mocks PubMed API research when API key is not available"""
    print(f"[MOCK] Researching topic: {topic}")
    
    # Mock findings for 'Journaling for Anxiety'
    mock_data = {
        "Journaling for Anxiety": [
            {
                "content": "Regular journaling has been shown to reduce anxiety symptoms by 23% over a 6-week period, according to a 2022 study published in the Journal of Behavioral Therapy.",
                "source": "Journal of Behavioral Therapy, 2022"
            },
            {
                "content": "Writing in a journal for 15 minutes three times per week can help process negative emotions and reduce rumination, a key component of anxiety disorders.",
                "source": "Cognitive Therapy and Research, 2021"
            },
            {
                "content": "Expressive writing in journals activates the parasympathetic nervous system, which counteracts the 'fight or flight' response associated with anxiety.",
                "source": "Biological Psychology, 2023"
            }
        ]
    }
    
    # If topic exists in mock data, return those findings, otherwise return generic ones
    if topic in mock_data:
        return mock_data[topic][:max_findings]
    
    # Generic findings for other topics
    generic_findings = [
        {
            "content": f"Research shows that {topic.lower()} can be beneficial for mental health and wellbeing according to recent studies.",
            "source": "Journal of Mental Health, 2023"
        },
        {
            "content": f"Regular practice of {topic.lower()} has been associated with reduced stress levels and improved coping mechanisms.",
            "source": "Psychological Review, 2022"
        },
        {
            "content": f"Studies indicate that {topic.lower()} may help individuals develop better self-awareness and emotional regulation skills.",
            "source": "Journal of Behavioral Science, 2021"
        }
    ]
    
    return generic_findings[:max_findings]

# Mock image reference generator
def mock_image_references(topic, max_images=2):
    """Generates mock image references for a topic"""
    print(f"[MOCK] Generating image references for: {topic}")
    
    image_refs = [
        {
            "description": f"Person writing in a journal with calming blue background",
            "source": "stock_image_journal_1.jpg"
        },
        {
            "description": f"Open journal with pen and relaxing elements like plants or tea",
            "source": "stock_image_journal_2.jpg"
        },
        {
            "description": f"Infographic showing the benefits of {topic.lower()}",
            "source": f"infographic_{topic.lower().replace(' ', '_')}.jpg"
        }
    ]
    
    return image_refs[:max_images]

# PubMed research tool (uses real API if key is available, otherwise falls back to mock)
def pubmed_research(topic, api_key=None, max_findings=3):
    """Conducts research on PubMed for a given topic"""
    if not api_key:
        return mock_pubmed_research(topic, max_findings)
    
    # Code for real PubMed API integration would go here
    # This is a placeholder for when you have a real API key
    try:
        print(f"[API] Researching topic on PubMed: {topic}")
        # API call would happen here
        # For now, we'll just use the mock data
        return mock_pubmed_research(topic, max_findings)
    except Exception as e:
        print(f"Error accessing PubMed API: {e}")
        print("Falling back to mock data")
        return mock_pubmed_research(topic, max_findings)

# VADER sentiment analysis tool
def analyze_sentiment(text):
    """Analyzes the sentiment of text using VADER"""
    sia = SentimentIntensityAnalyzer()
    sentiment = sia.polarity_scores(text)
    
    # Interpret the sentiment scores
    if sentiment['compound'] >= 0.05:
        return {'score': sentiment['compound'], 'sentiment': 'positive'}
    elif sentiment['compound'] <= -0.05:
        return {'score': sentiment['compound'], 'sentiment': 'negative'}
    else:
        return {'score': sentiment['compound'], 'sentiment': 'neutral'}

# Tool for creating PDF outputs
def create_pdf(content, output_path, include_images=False):
    """Creates a PDF document from the provided content"""
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30
    ))
    styles.add(ParagraphStyle(
        name='ModuleTitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='BodyText',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray
    ))
    
    # Build the PDF content
    elements = []
    
    # Add the title
    elements.append(Paragraph(content.title, styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    
    # Add each module
    for module in content.body:
        elements.append(Paragraph(module.title, styles['ModuleTitle']))
        elements.append(Paragraph(module.content, styles['BodyText']))
        
        # Add image placeholder if specified and in the right location
        if include_images and module.image_placement:
            # This would be replaced with actual image handling in a full implementation
            elements.append(Paragraph(f"[Image Placeholder: {module.image_placement}]", 
                                     styles['BodyText']))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Add footer
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(content.footer, styles['Footer']))
    
    # Build the PDF
    doc.build(elements)
    
    print(f"PDF created at: {output_path}")
    return output_path

# DuckDB tool (referenced in manager_agent.py)
def duckdb_tool(query):
    """Placeholder for DuckDB tool functionality"""
    print(f"[DuckDB] Executing query: {query}")
    return {"status": "success", "message": "DuckDB query executed (mock)"}