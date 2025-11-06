"""
Archon Knowledge Base Integration Service

This service provides integration with Archon's knowledge base API for
RAG-powered content analysis and enhancement in Journal Craft Crew.
"""

import httpx
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os

logger = logging.getLogger(__name__)

class ArchonServiceClient:
    """Service client for Archon knowledge base integration"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("ARCHON_BASE_URL", "http://localhost:8181")
        self.client = httpx.AsyncClient(timeout=30.0)
        self.project_id = os.getenv("ARCHON_PROJECT_ID")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def search_knowledge_base(self, query: str, match_count: int = 5, project_id: str = None) -> Dict[str, Any]:
        """
        Search Archon knowledge base using RAG

        Args:
            query: Search query for knowledge base
            match_count: Number of results to return
            project_id: Specific project to search in (optional)

        Returns:
            Dictionary containing search results or error
        """
        try:
            # Use the RAG search endpoint
            search_data = {
                "query": query,
                "match_count": match_count
            }

            if project_id or self.project_id:
                search_data["project_id"] = project_id or self.project_id

            response = await self.client.post(
                f"{self.base_url}/api/rag/search",
                json=search_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Successfully searched knowledge base for query: {query}")
            return {
                "success": True,
                "results": result.get("results", []),
                "query": query,
                "match_count": len(result.get("results", []))
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching knowledge base: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "results": []
            }
        except Exception as e:
            logger.error(f"Failed to search knowledge base: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    async def add_journal_to_knowledge_base(self, title: str, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Add journal content to Archon knowledge base

        Args:
            title: Journal title or topic
            content: Journal content to index
            metadata: Additional metadata (theme, date, author_style, etc.)

        Returns:
            Dictionary containing result or error
        """
        try:
            journal_data = {
                "title": title,
                "content": content,
                "knowledge_type": "journal",
                "tags": ["journal", "crewai-generated"]
            }

            if metadata:
                journal_data.update(metadata)

            if self.project_id:
                journal_data["project_id"] = self.project_id

            response = await self.client.post(
                f"{self.base_url}/api/knowledge-items",
                json=journal_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Successfully added journal to knowledge base: {title}")
            return {
                "success": True,
                "result": result,
                "title": title
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error adding journal to knowledge base: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "title": title
            }
        except Exception as e:
            logger.error(f"Failed to add journal to knowledge base: {e}")
            return {
                "success": False,
                "error": str(e),
                "title": title
            }

    async def get_project_status(self, project_id: str = None) -> Dict[str, Any]:
        """
        Get Archon project status and information

        Args:
            project_id: Project ID to check (optional)

        Returns:
            Dictionary containing project information
        """
        try:
            project_to_check = project_id or self.project_id
            if not project_to_check:
                return {
                    "success": False,
                    "error": "No project ID available"
                }

            response = await self.client.get(
                f"{self.base_url}/api/projects/{project_to_check}",
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json()
            return {
                "success": True,
                "project": result
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting project status: {e.response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            logger.error(f"Failed to get project status: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def analyze_content_with_knowledge(self, content: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """
        Analyze content using Archon's knowledge base for insights

        Args:
            content: Content to analyze
            focus_areas: Specific areas to focus analysis on (e.g., ["goal-setting", "productivity"])

        Returns:
            Dictionary containing analysis results
        """
        try:
            # Search for relevant knowledge based on content themes
            analysis_queries = focus_areas or []

            # If no focus areas provided, extract them from content
            if not analysis_queries:
                # Simple keyword extraction for common journal themes
                common_themes = ["goal setting", "productivity", "mindfulness", "reflection", "growth", "motivation"]
                analysis_queries = [theme for theme in common_themes if theme.lower() in content.lower()]

            if not analysis_queries:
                analysis_queries = ["personal development", "self improvement"]

            # Search knowledge base for each focus area
            all_results = []
            for query in analysis_queries:
                search_result = await self.search_knowledge_base(query, match_count=3)
                if search_result.get("success"):
                    all_results.extend(search_result.get("results", []))

            return {
                "success": True,
                "content_analysis": {
                    "focus_areas": analysis_queries,
                    "knowledge_insights": all_results,
                    "insights_count": len(all_results),
                    "recommendations": self._generate_recommendations(content, all_results)
                }
            }

        except Exception as e:
            logger.error(f"Failed to analyze content with knowledge: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_analysis": {}
            }

    def _generate_recommendations(self, content: str, knowledge_insights: List[Dict]) -> List[str]:
        """Generate recommendations based on content and knowledge insights"""
        recommendations = []

        if knowledge_insights:
            recommendations.append("Research-backed insights are available from the knowledge base")
            recommendations.append(f"Found {len(knowledge_insights)} relevant knowledge items")

            # Extract key themes from insights
            themes = set()
            for insight in knowledge_insights:
                if "content" in insight:
                    # Simple keyword extraction
                    content_lower = insight["content"].lower()
                    if "goal" in content_lower:
                        themes.add("goal-setting")
                    if "productivity" in content_lower:
                        themes.add("productivity")
                    if "mindful" in content_lower or "reflection" in content_lower:
                        themes.add("mindfulness")

            if themes:
                recommendations.append(f"Key themes identified: {', '.join(themes)}")

        return recommendations

# Singleton instance for easy access
archon_client = ArchonServiceClient()

# Convenience functions for CrewAI agents
async def search_knowledge_for_theme(theme: str, match_count: int = 3) -> List[Dict]:
    """Search Archon knowledge base for a specific theme"""
    result = await archon_client.search_knowledge_base(theme, match_count)
    return result.get("results", []) if result.get("success") else []

async def enhance_journal_with_knowledge(title: str, content: str, metadata: Dict = None) -> Dict:
    """Enhance journal content with knowledge base insights"""
    # First add to knowledge base
    add_result = await archon_client.add_journal_to_knowledge_base(title, content, metadata)

    # Then analyze for insights
    analysis_result = await archon_client.analyze_content_with_knowledge(content)

    return {
        "added_to_kb": add_result.get("success", False),
        "analysis": analysis_result.get("content_analysis", {}),
        "errors": [
            add_result.get("error") if not add_result.get("success") else None,
            analysis_result.get("error") if not analysis_result.get("success") else None
        ]
    }