"""
AI Crew Service for Journal Content Generation

This service integrates CrewAI to generate high-quality journal content
using specialized AI agents for different aspects of journal creation.
"""

import asyncio
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from crewai import Agent, Task, Crew, Process
from crewai_tools import (
    SerperDevTool,
    ScrapeWebsiteTool,
    DirectoryReadTool,
    DirectorySearchTool,
    TXTSearchTool,
    MDXSearchTool
)

logger = logging.getLogger(__name__)

class AICrewService:
    """AI Crew service for generating journal content with multiple specialized agents"""

    def __init__(self):
        # Initialize tools
        self.search_tool = SerperDevTool()
        self.scrape_tool = ScrapeWebsiteTool()
        self.directory_read_tool = DirectoryReadTool()
        self.directory_search_tool = DirectorySearchTool()
        self.txt_search_tool = TXTSearchTool()
        self.mdx_search_tool = MDXSearchTool()

        # Available themes for journal generation
        self.available_themes = [
            "personal_growth", "mindfulness", "travel_adventure", "technology_innovation",
            "creative_writing", "career_development", "health_wellness", "relationships",
            "learning_education", "philosophy_reflection", "nature_environment", "art_culture"
        ]

        # Check for OpenAI API key
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("⚠️ OPENAI_API_KEY not found. AI generation will be in demo mode.")

    async def generate_journal_content(
        self,
        user_id: int,
        theme: str,
        title_style: str,
        author_style: str,
        research_depth: str = "basic",
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate journal content using AI Crew

        Args:
            user_id: User ID for personalization
            theme: Theme for content generation
            title_style: Style preference for title
            author_style: Writing style preference
            research_depth: Depth of research (basic/medium/deep)
            custom_prompt: Optional custom instruction

        Returns:
            Dictionary containing generated content and metadata
        """
        try:
            start_time = datetime.now()

            # Validate theme
            if theme not in self.available_themes:
                raise ValueError(f"Theme '{theme}' not available. Choose from: {self.available_themes}")

            # Check for demo mode (no OpenAI API key)
            if not self.openai_api_key:
                logger.info("🎭 Running in demo mode - generating sample content")
                return await self._generate_demo_content(user_id, theme, title_style, author_style, research_depth, custom_prompt, start_time)

            # Create specialized agents
            researcher = self._create_research_agent(theme, research_depth)
            title_generator = self._create_title_agent(title_style, theme)
            content_creator = self._create_content_agent(author_style, theme, custom_prompt)
            reviewer = self._create_reviewer_agent(theme)

            # Define tasks
            research_task = Task(
                description=f"""
                Research the theme of '{theme}' to gather interesting facts, insights, and inspiration.
                {"Perform deep research with multiple sources and detailed analysis." if research_depth == "deep" else
                 "Perform moderate research with some source variety." if research_depth == "medium" else
                 "Perform basic research to get fundamental understanding."}

                Focus on finding:
                - Key concepts and ideas related to {theme}
                - Interesting facts or statistics
                - Thought-provoking questions
                - Inspirational content for journal writing
                """,
                agent=researcher,
                expected_output="Comprehensive research notes with key insights about the theme"
            )

            title_task = Task(
                description=f"""
                Based on the research and the '{theme}' theme, create an engaging journal title.
                Style: {title_style}

                The title should be:
                - Creative and memorable
                - Appropriate for the {title_style} style
                - Between 5-15 words
                - Thought-provoking or intriguing
                """,
                agent=title_generator,
                expected_output="A compelling journal title that captures the essence of the theme",
                context=[research_task]
            )

            content_task = Task(
                description=f"""
                Write a meaningful journal entry based on the research and title.
                Theme: {theme}
                Author Style: {author_style}
                Custom Instructions: {custom_prompt or "None"}

                The content should:
                - Be 500-1000 words
                - Follow the {author_style} writing style
                - Incorporate insights from the research
                - Be personal and reflective
                - Have a clear beginning, middle, and end
                - Include thoughtful questions or reflections
                - Feel authentic and meaningful
                """,
                agent=content_creator,
                expected_output="A well-written, engaging journal entry that feels personal and meaningful",
                context=[research_task, title_task]
            )

            review_task = Task(
                description=f"""
                Review the generated journal content for quality and coherence.
                Theme: {theme}

                Check for:
                - Content quality and engagement
                - Appropriate tone and style
                - Coherence and flow
                - Emotional impact
                - Personalization and authenticity

                Provide feedback and improvements if needed.
                """,
                agent=reviewer,
                expected_output="Review feedback and final quality assessment of the journal content",
                context=[research_task, title_task, content_task]
            )

            # Create and run crew
            crew = Crew(
                agents=[researcher, title_generator, content_creator, reviewer],
                tasks=[research_task, title_task, content_task, review_task],
                process=Process.sequential,
                verbose=True
            )

            # Run the crew
            result = await asyncio.to_thread(crew.kickoff)

            # Process results
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()

            # Extract content from crew results
            generated_title = self._extract_title_from_result(result)
            generated_content = self._extract_content_from_result(result)

            # Generate metadata
            word_count = len(generated_content.split())
            mood = self._analyze_mood(generated_content, theme)
            tags = self._generate_tags(theme, generated_content)

            return {
                "title": generated_title,
                "content": generated_content,
                "raw_ai_content": str(result),
                "theme": theme,
                "generated_at": end_time.isoformat(),
                "generation_time": generation_time,
                "word_count": word_count,
                "mood": mood,
                "tags": tags,
                "agents_used": ["researcher", "title_generator", "content_creator", "reviewer"],
                "research_depth": research_depth,
                "prompt": custom_prompt
            }

        except Exception as e:
            logger.error(f"AI crew generation failed: {e}")
            raise RuntimeError(f"Failed to generate journal content: {str(e)}")

    def _create_research_agent(self, theme: str, research_depth: str) -> Agent:
        """Create a research agent specialized in the theme"""
        return Agent(
            role="Research Specialist",
            goal=f"Conduct thorough research on {theme} to provide valuable insights and inspiration",
            backstory=f"""You are a skilled researcher with expertise in {theme}.
            You have a talent for finding interesting facts, deep insights, and thought-provoking information
            that serves as excellent foundation for creative journal writing. Your research is always accurate,
            relevant, and inspiring.""",
            tools=[self.search_tool, self.scrape_tool, self.directory_search_tool],
            allow_delegation=False,
            verbose=True
        )

    def _create_title_agent(self, title_style: str, theme: str) -> Agent:
        """Create a title generation agent"""
        return Agent(
            role="Creative Title Writer",
            goal=f"Create compelling, engaging journal titles in {title_style} style for {theme} content",
            backstory=f"""You are a creative writer specialized in crafting captivating titles.
            You understand how to create titles that draw readers in and set the perfect tone.
            Your titles in {title_style} style are always memorable, intriguing, and perfectly match the content.""",
            allow_delegation=False,
            verbose=True
        )

    def _create_content_agent(self, author_style: str, theme: str, custom_prompt: Optional[str]) -> Agent:
        """Create a content creation agent"""
        backstory = f"""You are a talented journal writer with expertise in {theme}.
        You write in the {author_style} style with authenticity and emotional depth.
        Your journal entries feel personal, thoughtful, and engaging."""

        if custom_prompt:
            backstory += f" You have a special instruction for this piece: {custom_prompt}"

        return Agent(
            role="Journal Content Creator",
            goal=f"Write meaningful, engaging journal entries about {theme} in {author_style} style",
            backstory=backstory,
            allow_delegation=False,
            verbose=True
        )

    def _create_reviewer_agent(self, theme: str) -> Agent:
        """Create a content reviewer agent"""
        return Agent(
            role="Content Quality Reviewer",
            goal=f"Ensure journal content about {theme} meets high quality standards and feels authentic",
            backstory="""You are an experienced editor with excellent judgment for content quality.
            You have a keen eye for detail, emotional impact, and authenticity in writing.
            Your feedback always helps improve content while maintaining the author's voice.""",
            allow_delegation=False,
            verbose=True
        )

    def _extract_title_from_result(self, result) -> str:
        """Extract title from crew result"""
        result_str = str(result)
        # Look for title patterns in the result
        lines = result_str.split('\n')
        for line in lines:
            if 'title:' in line.lower() or len(line.strip()) < 100 and line.strip():
                return line.strip().replace('Title:', '').replace('title:', '').strip()

        # Fallback: use the first line that looks like a title
        for line in lines:
            if len(line.strip()) > 5 and len(line.strip()) < 100:
                return line.strip()

        return "AI Generated Journal Entry"

    def _extract_content_from_result(self, result) -> str:
        """Extract main content from crew result"""
        result_str = str(result)
        # Remove title and metadata, keep the main content
        lines = result_str.split('\n')
        content_lines = []

        for line in lines:
            line = line.strip()
            # Skip obvious metadata lines
            if (not line.startswith('#') and
                not line.startswith('Agent:') and
                not line.startswith('Task:') and
                len(line) > 20):
                content_lines.append(line)

        # Join and clean up content
        content = '\n'.join(content_lines)

        # If content is too short, use more of the result
        if len(content.split()) < 200:
            content = result_str

        return content.strip()

    def _analyze_mood(self, content: str, theme: str) -> str:
        """Analyze the mood of the generated content"""
        # Simple mood analysis based on keywords
        positive_words = ['joy', 'happy', 'grateful', 'excited', 'hopeful', 'inspired', 'peaceful']
        reflective_words = ['think', 'wonder', 'consider', 'reflect', 'ponder', 'question']
        emotional_words = ['feel', 'heart', 'soul', 'deep', 'emotion', 'passion']

        content_lower = content.lower()

        if any(word in content_lower for word in positive_words):
            return "uplifting"
        elif any(word in content_lower for word in reflective_words):
            return "reflective"
        elif any(word in content_lower for word in emotional_words):
            return "emotional"
        else:
            return "thoughtful"

    def _generate_tags(self, theme: str, content: str) -> List[str]:
        """Generate relevant tags for the content"""
        tags = [theme]

        # Add some basic tags based on theme and content length
        content_lower = content.lower()

        if 'personal' in content_lower or 'i' in content_lower:
            tags.append('personal')

        if 'growth' in content_lower or 'learn' in content_lower:
            tags.append('growth')

        if 'future' in content_lower or 'goal' in content_lower:
            tags.append('aspiration')

        return tags[:5]  # Limit to 5 tags

    async def get_available_themes(self) -> List[str]:
        """Get list of available themes for AI generation"""
        return self.available_themes.copy()

    async def get_user_theme_usage(self, user_id: int) -> Dict[str, int]:
        """Get statistics about user's theme usage (placeholder for future implementation)"""
        # This would typically query a database
        return {
            "personal_growth": 5,
            "mindfulness": 3,
            "travel_adventure": 2,
            "technology_innovation": 4
        }

    async def _generate_demo_content(
        self,
        user_id: int,
        theme: str,
        title_style: str,
        author_style: str,
        research_depth: str,
        custom_prompt: Optional[str],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Generate demo content when OpenAI API key is not available"""

        # Demo content templates for different themes
        demo_content = {
            "personal_growth": {
                "title": "Reflecting on My Journey of Personal Growth",
                "content": """Today I find myself contemplating the beautiful journey of personal growth that has unfolded over these past months. Each step forward, no matter how small, has contributed to the person I'm becoming.

I've learned that growth isn't always linear. There are days when I feel unstoppable, making progress in leaps and bounds. Other days, I'm reminded that patience and self-compassion are essential companions on this path.

The practice of journaling has become my anchor, providing clarity and perspective. Through these pages, I've discovered patterns in my thinking, celebrated victories I might have otherwise overlooked, and found the courage to face areas that need attention.

As I continue this journey, I'm grateful for the reminder that every experience—whether challenging or joyful—contains an opportunity for growth. Today, I choose to embrace both the process and the progress, knowing that each moment contributes to my ongoing evolution."""
            },
            "mindfulness": {
                "title": "Finding Peace in the Present Moment",
                "content": """In the quiet moments of today, I discovered the profound beauty of simply being present. The world often rushes us forward, but today I chose to pause, breathe, and fully inhabit the now.

Mindfulness has taught me that peace isn't found in the absence of chaos, but in our ability to remain centered amidst it. Today brought its share of challenges, yet by returning to my breath and grounding myself in the present, I found a steady calm that carried me through.

I noticed the way sunlight filters through the leaves outside my window, the warmth of my morning tea cup in my hands, the gentle rhythm of my own heartbeat. These small, present moments became anchors of gratitude and awareness.

This practice of being present isn't always easy—my mind still wanders to tomorrow's worries and yesterday's regrets. But each time I gently guide my attention back to now, I'm strengthening my capacity for peace and clarity.

Today, I'm reminded that the present moment is all we truly have, and within it lies an infinite well of peace and wisdom."""
            },
            "travel_adventure": {
                "title": "Wanderlust: The Call of Distant Horizons",
                "content": """Today my heart is filled with the familiar ache of wanderlust—that beautiful longing for places I've never been and experiences I've yet to discover. There's something magical about the anticipation of adventure that stirs the soul.

I find myself daydreaming about cobblestone streets in ancient cities, the taste of unfamiliar cuisines, the sound of languages I don't yet understand. These dreams aren't just about escape; they're about expansion—expanding my understanding of the world and myself.

Travel has always been my greatest teacher. It has taught me resilience when plans go awry, humility when faced with cultures vastly different from my own, and joy in the simple connections that transcend language barriers.

Even when I can't physically travel, I carry the spirit of adventure within me. Every day offers opportunities to explore—whether it's trying a new recipe, taking a different route home, or striking up a conversation with a stranger.

Today, I celebrate this eternal call to explore, knowing that the world is vast and full of wonders waiting to be discovered."""
            },
            "technology_innovation": {
                "title": "Embracing the Digital Revolution with Mindful Innovation",
                "content": """Today I find myself marveling at the rapid pace of technological change that surrounds us. We're living in an era of unprecedented innovation, where yesterday's science fiction becomes today's reality.

What excites me most isn't just the technology itself, but the potential it holds for solving some of our world's most pressing challenges. From artificial intelligence that can accelerate medical research to sustainable energy solutions that could reshape our future, we're witnessing innovation that could redefine what's possible.

Yet with this incredible progress comes responsibility. I believe in approaching technology with both enthusiasm and thoughtful consideration. How can we harness these tools while staying connected to our humanity? How do we ensure that innovation serves the greater good?

As someone who loves both technology and reflection, I see the importance of balancing forward momentum with mindful intention. Today, I'm grateful to be living in this time of incredible change, and I'm committed to being both an active participant and a thoughtful observer of this digital revolution.

The future is being written now, and we all have a role to play in shaping it with wisdom and vision."""
            }
        }

        # Get demo content for the theme or use a default
        theme_content = demo_content.get(theme, demo_content["personal_growth"])

        # Apply custom prompt modifications if provided
        if custom_prompt:
            theme_content["content"] += f"\n\nSpecial Note: {custom_prompt}"

        # Calculate timing
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()

        # Generate metadata
        word_count = len(theme_content["content"].split())
        mood = self._analyze_mood(theme_content["content"], theme)
        tags = self._generate_tags(theme, theme_content["content"])

        return {
            "title": theme_content["title"],
            "content": theme_content["content"],
            "raw_ai_content": f"[DEMO MODE] Generated sample content for theme: {theme}",
            "theme": theme,
            "generated_at": end_time.isoformat(),
            "generation_time": generation_time,
            "word_count": word_count,
            "mood": mood,
            "tags": tags,
            "agents_used": ["demo_generator"],
            "research_depth": research_depth,
            "prompt": custom_prompt,
            "demo_mode": True
        }