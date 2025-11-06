"""
Knowledge Base Query Service

This service provides a high-level interface for CrewAI agents to query the Archon knowledge base
and integrate research-backed insights into journal content creation.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import Archon client
try:
    from app.services.archon_client import ArchonServiceClient
    ARCHON_AVAILABLE = True
except ImportError:
    ARCHON_AVAILABLE = False
    logging.warning("Archon client not available - knowledge base features will be disabled")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeQueryService:
    """
    High-level service for CrewAI agents to access knowledge base functionality.

    This service abstracts the complexity of Archon API interactions and provides
    simple, agent-friendly methods for knowledge retrieval and content enhancement.
    """

    def __init__(self):
        """Initialize the knowledge query service."""
        self.archon_client = None
        self.enabled = False

        if ARCHON_AVAILABLE:
            try:
                self.archon_client = ArchonServiceClient()
                self.enabled = True
                logger.info("Knowledge query service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Archon client: {e}")
                self.enabled = False
        else:
            logger.warning("Knowledge query service disabled - Archon not available")

    def is_enabled(self) -> bool:
        """Check if knowledge base functionality is available."""
        return self.enabled and self.archon_client is not None

    async def search_knowledge_for_theme(self, theme: str, match_count: int = 5) -> Dict[str, Any]:
        """
        Search knowledge base for relevant content based on journal theme.

        Args:
            theme: The journal theme (e.g., "Journaling for Anxiety", "Productivity")
            match_count: Number of results to return

        Returns:
            Dictionary containing search results and metadata
        """
        if not self.is_enabled():
            return self._get_fallback_response(theme, "knowledge search")

        try:
            # Create search query based on theme
            search_query = self._create_theme_search_query(theme)

            # Search knowledge base
            results = await self.archon_client.search_knowledge_base(
                query=search_query,
                match_count=match_count
            )

            # Process and format results for agents
            processed_results = self._process_search_results(results, theme)

            logger.info(f"Knowledge search completed for theme: {theme}")
            return processed_results

        except Exception as e:
            logger.error(f"Error searching knowledge base for theme '{theme}': {e}")
            return self._get_fallback_response(theme, "knowledge search")

    async def enhance_journal_with_knowledge(self, title: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance journal content with relevant knowledge base insights.

        Args:
            title: Journal title
            content: Existing journal content
            metadata: Journal metadata (theme, style, etc.)

        Returns:
            Enhanced content with knowledge insights
        """
        if not self.is_enabled():
            return self._get_fallback_enhancement(title, content, metadata)

        try:
            # Extract focus areas from content and metadata
            focus_areas = self._extract_focus_areas(content, metadata)

            # Search for relevant knowledge
            knowledge_results = await self.archon_client.analyze_content_with_knowledge(
                content=content,
                focus_areas=focus_areas
            )

            # Enhance content with knowledge insights
            enhanced_content = self._enhance_content_with_insights(
                content, knowledge_results, metadata
            )

            # Index the journal for future reference
            await self._index_journal(title, enhanced_content, metadata)

            logger.info(f"Journal enhancement completed for: {title}")
            return {
                'success': True,
                'original_content': content,
                'enhanced_content': enhanced_content,
                'knowledge_insights': knowledge_results,
                'focus_areas': focus_areas,
                'indexed': True
            }

        except Exception as e:
            logger.error(f"Error enhancing journal with knowledge: {e}")
            return self._get_fallback_enhancement(title, content, metadata)

    async def get_research_insights(self, topic: str, depth: str = "medium") -> Dict[str, Any]:
        """
        Get research-backed insights for specific topics.

        Args:
            topic: Research topic (e.g., "mindfulness", "productivity", "anxiety")
            depth: Research depth (light, medium, deep)

        Returns:
            Research insights and sources
        """
        if not self.is_enabled():
            return self._get_fallback_research(topic, depth)

        try:
            # Adjust match count based on depth
            match_count = {"light": 3, "medium": 5, "deep": 8}.get(depth, 5)

            # Create research query
            research_query = f"research studies findings {topic} psychology therapy"

            # Search knowledge base
            results = await self.archon_client.search_knowledge_base(
                query=research_query,
                match_count=match_count
            )

            # Process research results
            research_insights = self._process_research_results(results, topic, depth)

            logger.info(f"Research insights retrieved for topic: {topic}")
            return research_insights

        except Exception as e:
            logger.error(f"Error getting research insights for '{topic}': {e}")
            return self._get_fallback_research(topic, depth)

    async def _index_journal(self, title: str, content: str, metadata: Dict[str, Any]):
        """Index journal content in knowledge base for future reference."""
        try:
            # Prepare metadata for indexing
            index_metadata = {
                **metadata,
                'content_type': 'journal',
                'created_at': datetime.now().isoformat(),
                'title': title
            }

            # Add to knowledge base
            await self.archon_client.add_journal_to_knowledge_base(
                title=title,
                content=content,
                metadata=index_metadata
            )

            logger.info(f"Journal indexed successfully: {title}")

        except Exception as e:
            logger.error(f"Error indexing journal '{title}': {e}")

    def _create_theme_search_query(self, theme: str) -> str:
        """Create an effective search query based on journal theme."""
        # Extract key concepts from theme
        theme_lower = theme.lower()

        # Theme-specific query enhancement
        if 'anxiety' in theme_lower or 'stress' in theme_lower:
            return f"anxiety stress management coping techniques mindfulness cognitive behavioral therapy"
        elif 'productivity' in theme_lower or 'goal' in theme_lower:
            return f"productivity goal setting time management habit formation motivation efficiency"
        elif 'creativity' in theme_lower or 'artistic' in theme_lower:
            return f"creativity artistic expression innovation inspiration creative thinking brainstorming"
        elif 'mindfulness' in theme_lower or 'meditation' in theme_lower:
            return f"mindfulness meditation awareness present moment breathing exercises relaxation"
        elif 'gratitude' in theme_lower or 'thankfulness' in theme_lower:
            return f"gratitude thankfulness positive psychology appreciation happiness wellbeing"
        else:
            # Generic query for personal growth themes
            return f"personal growth self improvement journaling reflection habits wellbeing {theme}"

    def _extract_focus_areas(self, content: str, metadata: Dict[str, Any]) -> List[str]:
        """Extract key focus areas from content and metadata."""
        focus_areas = []

        # Extract from theme
        theme = metadata.get('theme', '').lower()
        if 'anxiety' in theme:
            focus_areas.append('anxiety-management')
        if 'productivity' in theme:
            focus_areas.append('productivity-techniques')
        if 'mindfulness' in theme:
            focus_areas.append('mindfulness-practices')
        if 'creativity' in theme:
            focus_areas.append('creative-expression')

        # Extract from author style
        style = metadata.get('authorStyle', '').lower()
        if 'research' in style or 'evidence' in style:
            focus_areas.append('evidence-based')
        if 'empathetic' in style or 'compassionate' in style:
            focus_areas.append('emotional-intelligence')

        # Extract keywords from content
        content_lower = content.lower()
        keywords = ['habits', 'routine', 'self-care', 'reflection', 'growth', 'wellbeing']
        for keyword in keywords:
            if keyword in content_lower and keyword not in focus_areas:
                focus_areas.append(keyword)

        return focus_areas[:5]  # Limit to top 5 focus areas

    def _process_search_results(self, results: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Process and format search results for agent consumption."""
        if not results.get('success', False):
            return self._get_fallback_response(theme, "knowledge search")

        items = results.get('data', {}).get('items', [])

        # Extract relevant information
        processed_items = []
        for item in items:
            processed_item = {
                'id': item.get('id'),
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'relevance_score': item.get('metadata', {}).get('relevance_score', 0.0),
                'source': item.get('metadata', {}).get('source', 'knowledge_base'),
                'category': item.get('metadata', {}).get('category', 'general'),
                'key_insights': self._extract_key_insights(item.get('content', ''))
            }
            processed_items.append(processed_item)

        # Sort by relevance score
        processed_items.sort(key=lambda x: x['relevance_score'], reverse=True)

        return {
            'success': True,
            'theme': theme,
            'results': processed_items,
            'total_results': len(processed_items),
            'query_metadata': {
                'theme': theme,
                'search_timestamp': datetime.now().isoformat(),
                'source': 'archon_knowledge_base'
            }
        }

    def _process_research_results(self, results: Dict[str, Any], topic: str, depth: str) -> Dict[str, Any]:
        """Process research results with academic focus."""
        if not results.get('success', False):
            return self._get_fallback_research(topic, depth)

        items = results.get('data', {}).get('items', [])

        # Group by research type
        research_items = []
        practical_items = []

        for item in items:
            processed_item = {
                'title': item.get('title', ''),
                'content': item.get('content', ''),
                'source': item.get('metadata', {}).get('source', 'research'),
                'category': item.get('metadata', {}).get('category', 'general'),
                'key_findings': self._extract_key_findings(item.get('content', ''))
            }

            # Categorize as research or practical
            if 'study' in item.get('title', '').lower() or 'research' in item.get('content', '').lower():
                research_items.append(processed_item)
            else:
                practical_items.append(processed_item)

        return {
            'success': True,
            'topic': topic,
            'depth': depth,
            'research_findings': research_items,
            'practical_applications': practical_items,
            'total_sources': len(items),
            'research_metadata': {
                'topic': topic,
                'depth': depth,
                'search_timestamp': datetime.now().isoformat(),
                'source': 'archon_knowledge_base'
            }
        }

    def _enhance_content_with_insights(self, content: str, insights: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """Enhance content with knowledge insights while maintaining original voice."""
        if not insights.get('success', False):
            return content

        # Extract relevant insights
        relevant_insights = insights.get('relevant_knowledge', [])

        # Build enhanced content
        enhanced_sections = []

        # Add knowledge-enhanced section
        if relevant_insights:
            insight_bullets = []
            for insight in relevant_insights[:3]:  # Limit to top 3 insights
                insight_bullets.append(f"• {insight.get('content', '')}")

            if insight_bullets:
                enhanced_sections.append("\n### Research-Backed Insights\n")
                enhanced_sections.append("\n".join(insight_bullets))

        # Add citations if available
        sources = insights.get('sources', [])
        if sources:
            enhanced_sections.append("\n### Key Sources\n")
            for source in sources[:3]:  # Limit to top 3 sources
                enhanced_sections.append(f"• {source}")

        # Combine original content with enhancements
        if enhanced_sections:
            enhanced_content = content + "\n" + "".join(enhanced_sections)
            return enhanced_content

        return content

    def _extract_key_insights(self, content: str) -> List[str]:
        """Extract key insights from content."""
        # Simple extraction - in production, this could use NLP
        sentences = content.split('.')
        insights = []

        for sentence in sentences[:5]:  # Take first 5 sentences
            sentence = sentence.strip()
            if len(sentence) > 20 and any(keyword in sentence.lower()
                                        for keyword in ['research', 'study', 'finding', 'evidence', 'shows']):
                insights.append(sentence)

        return insights

    def _extract_key_findings(self, content: str) -> List[str]:
        """Extract key research findings."""
        # Similar to insights but with research focus
        sentences = content.split('.')
        findings = []

        for sentence in sentences[:5]:
            sentence = sentence.strip()
            if len(sentence) > 30 and any(keyword in sentence.lower()
                                       for keyword in ['found', 'concluded', 'demonstrated', 'showed', 'revealed']):
                findings.append(sentence)

        return findings

    def _get_fallback_response(self, theme: str, operation: str) -> Dict[str, Any]:
        """Get fallback response when knowledge base is unavailable."""
        return {
            'success': False,
            'theme': theme,
            'results': [],
            'total_results': 0,
            'fallback_used': True,
            'message': f"Knowledge base temporarily unavailable for {operation}",
            'fallback_metadata': {
                'timestamp': datetime.now().isoformat(),
                'reason': 'archon_unavailable'
            }
        }

    def _get_fallback_enhancement(self, title: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback enhancement when knowledge base is unavailable."""
        return {
            'success': False,
            'original_content': content,
            'enhanced_content': content,
            'knowledge_insights': {},
            'focus_areas': [],
            'indexed': False,
            'fallback_used': True,
            'message': "Knowledge enhancement temporarily unavailable",
            'fallback_metadata': {
                'timestamp': datetime.now().isoformat(),
                'reason': 'archon_unavailable'
            }
        }

    def _get_fallback_research(self, topic: str, depth: str) -> Dict[str, Any]:
        """Get fallback research when knowledge base is unavailable."""
        return {
            'success': False,
            'topic': topic,
            'depth': depth,
            'research_findings': [],
            'practical_applications': [],
            'total_sources': 0,
            'fallback_used': True,
            'message': "Research insights temporarily unavailable",
            'fallback_metadata': {
                'timestamp': datetime.now().isoformat(),
                'reason': 'archon_unavailable'
            }
        }

# Singleton instance for use throughout the application
knowledge_query_service = KnowledgeQueryService()

# Convenience functions for CrewAI agents
async def search_knowledge_for_theme(theme: str, match_count: int = 5) -> Dict[str, Any]:
    """Convenience function for agents to search knowledge base by theme."""
    return await knowledge_query_service.search_knowledge_for_theme(theme, match_count)

async def enhance_journal_with_knowledge(title: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for agents to enhance journal content."""
    return await knowledge_query_service.enhance_journal_with_knowledge(title, content, metadata)

async def get_research_insights(topic: str, depth: str = "medium") -> Dict[str, Any]:
    """Convenience function for agents to get research insights."""
    return await knowledge_query_service.get_research_insights(topic, depth)