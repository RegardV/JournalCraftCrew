"""
Journal Content Analyzer Service
Intelligent analysis of existing journal content for CrewAI enhancement recommendations
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from ..models.project import Project
from ..models.user import User
from ..core.database import get_db

# CrewAI agents for analysis
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../agents"))

class JournalContentAnalyzer:
    """Analyzes journal content and provides enhancement recommendations"""

    def __init__(self):
        self.cache_timeout = 3600  # 1 hour cache
        self.analysis_cache = {}

    async def analyze_project_state(self, project_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        Analyze existing journal project and return comprehensive state analysis

        Returns:
            Dict with:
            - completion_map: agent -> completion_percentage
            - quality_scores: content_aspect -> score (0-100)
            - missing_components: list of missing/incomplete elements
            - enhancement_potential: overall enhancement opportunity score
            - recommendations: list of specific enhancement recommendations
        """
        # Check cache first
        cache_key = f"project_analysis_{project_id}"
        if cache_key in self.analysis_cache:
            cached_data, timestamp = self.analysis_cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_timeout):
                return cached_data

        # Get project details
        project_query = select(Project).where(Project.id == project_id)
        project_result = await db.execute(project_query)
        project = project_result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found")

        # Analyze project files and structure
        analysis = await self._analyze_project_structure(project)

        # Generate enhancement recommendations
        analysis["recommendations"] = await self._generate_recommendations(analysis)

        # Cache the results
        self.analysis_cache[cache_key] = (analysis, datetime.now())

        return analysis

    async def _analyze_project_structure(self, project: Project) -> Dict[str, Any]:
        """Analyze project file structure and content"""

        # Determine project directory
        project_dir = await self._get_project_directory(project)

        if not project_dir or not os.path.exists(project_dir):
            return self._get_empty_analysis()

        # Initialize analysis structure
        analysis = {
            "completion_map": {},
            "quality_scores": {},
            "missing_components": [],
            "existing_files": [],
            "project_age_days": self._calculate_project_age(project),
            "content_size": 0
        }

        # Analyze different output directories
        subdirs = ["PDF_output", "media", "Json_output", "LLM_output"]

        for subdir in subdirs:
            subdir_path = os.path.join(project_dir, subdir)
            if os.path.exists(subdir_path):
                await self._analyze_subdirectory(subdir, subdir_path, analysis)

        # Calculate completion percentages for each agent
        analysis["completion_map"] = await self._calculate_agent_completion(analysis)

        # Calculate quality scores
        analysis["quality_scores"] = await self._calculate_quality_scores(analysis)

        # Identify missing components
        analysis["missing_components"] = await self._identify_missing_components(analysis)

        # Calculate overall enhancement potential
        analysis["enhancement_potential"] = self._calculate_enhancement_potential(analysis)

        return analysis

    async def _analyze_subdirectory(self, subdir_name: str, subdir_path: str, analysis: Dict):
        """Analyze a specific subdirectory of the project"""

        try:
            files = os.listdir(subdir_path)

            for file in files:
                file_path = os.path.join(subdir_path, file)

                if os.path.isfile(file_path):
                    file_info = {
                        "name": file,
                        "path": file_path,
                        "size": os.path.getsize(file_path),
                        "type": subdir_name,
                        "extension": os.path.splitext(file)[1].lower()
                    }

                    analysis["existing_files"].append(file_info)
                    analysis["content_size"] += file_info["size"]

                    # Analyze specific file types
                    if subdir_name == "Json_output" and file.endswith('.json'):
                        await self._analyze_json_file(file_path, file_info, analysis)
                    elif subdir_name == "PDF_output" and file.endswith('.pdf'):
                        await self._analyze_pdf_file(file_path, file_info, analysis)
                    elif subdir_name == "media":
                        await self._analyze_media_file(file_path, file_info, analysis)

        except Exception as e:
            print(f"Error analyzing directory {subdir_path}: {e}")

    async def _analyze_json_file(self, file_path: str, file_info: Dict, analysis: Dict):
        """Analyze JSON content files"""

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)

            # Analyze content structure and quality
            if "research_data" in file_path.lower():
                analysis["research_content"] = {
                    "found": True,
                    "entries": len(content) if isinstance(content, list) else 1,
                    "structure": "research_data"
                }
            elif "journal_structure" in file_path.lower() or "content" in file_path.lower():
                analysis["journal_content"] = {
                    "found": True,
                    "has_structure": "journal_structure" in str(content),
                    "days_count": self._count_journal_days(content),
                    "completeness": self._assess_content_completeness(content)
                }

        except Exception as e:
            print(f"Error analyzing JSON file {file_path}: {e}")

    async def _analyze_pdf_file(self, file_path: str, file_info: Dict, analysis: Dict):
        """Analyze PDF output files"""

        # Basic PDF analysis
        analysis["pdf_output"] = {
            "found": True,
            "file_count": analysis.get("pdf_output", {}).get("file_count", 0) + 1,
            "total_size": analysis.get("pdf_output", {}).get("total_size", 0) + file_info["size"]
        }

        # Extract basic PDF info if possible
        try:
            # Simple PDF analysis - could be enhanced with pdfminer
            with open(file_path, 'rb') as f:
                header = f.read(1000)
                if b'%PDF' in header:
                    analysis["pdf_output"]["valid"] = True
                else:
                    analysis["pdf_output"]["valid"] = False
        except Exception as e:
            print(f"Error analyzing PDF file {file_path}: {e}")

    async def _analyze_media_file(self, file_path: str, file_info: Dict, analysis: Dict):
        """Analyze media files"""

        media_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']

        if file_info["extension"] in media_extensions:
            analysis["media_files"] = {
                "found": True,
                "count": analysis.get("media_files", {}).get("count", 0) + 1,
                "total_size": analysis.get("media_files", {}).get("total_size", 0) + file_info["size"]
            }

    async def _calculate_agent_completion(self, analysis: Dict) -> Dict[str, int]:
        """Calculate completion percentage for each CrewAI agent"""

        completion_map = {
            "research_agent": 0,
            "content_curator_agent": 0,
            "editor_agent": 0,
            "media_agent": 0,
            "pdf_builder_agent": 0
        }

        # Research Agent completion
        if analysis.get("research_content", {}).get("found"):
            entries = analysis["research_content"].get("entries", 0)
            if entries >= 5:
                completion_map["research_agent"] = 100
            else:
                completion_map["research_agent"] = int((entries / 5) * 100)

        # Content Curator Agent completion
        if analysis.get("journal_content", {}).get("found"):
            completeness = analysis["journal_content"].get("completeness", 0)
            completion_map["content_curator_agent"] = completeness

        # Editor Agent completion
        # This would need more sophisticated analysis of edited vs original content
        if analysis.get("journal_content", {}).get("found"):
            # Assume content is edited if it exists and has reasonable structure
            completion_map["editor_agent"] = 85  # Assume good editing

        # Media Agent completion
        if analysis.get("media_files", {}).get("count", 0) > 0:
            completion_map["media_agent"] = 100

        # PDF Builder Agent completion
        if analysis.get("pdf_output", {}).get("found"):
            completion_map["pdf_builder_agent"] = 100

        return completion_map

    async def _calculate_quality_scores(self, analysis: Dict) -> Dict[str, int]:
        """Calculate quality scores for different content aspects"""

        quality_scores = {
            "research_depth": 0,
            "content_structure": 0,
            "visual_appeal": 0,
            "presentation_quality": 0,
            "overall_quality": 0
        }

        # Research depth score
        research_entries = analysis.get("research_content", {}).get("entries", 0)
        if research_entries >= 25:
            quality_scores["research_depth"] = 100
        elif research_entries >= 15:
            quality_scores["research_depth"] = 80
        elif research_entries >= 5:
            quality_scores["research_depth"] = 60
        else:
            quality_scores["research_depth"] = 30

        # Content structure score
        content_completeness = analysis.get("journal_content", {}).get("completeness", 0)
        quality_scores["content_structure"] = content_completeness

        # Visual appeal score
        media_count = analysis.get("media_files", {}).get("count", 0)
        if media_count >= 10:
            quality_scores["visual_appeal"] = 100
        elif media_count >= 5:
            quality_scores["visual_appeal"] = 80
        elif media_count >= 1:
            quality_scores["visual_appeal"] = 60
        else:
            quality_scores["visual_appeal"] = 0

        # Presentation quality score
        if analysis.get("pdf_output", {}).get("found"):
            quality_scores["presentation_quality"] = 90  # Assume good PDF generation

        # Calculate overall quality
        quality_scores["overall_quality"] = int(
            (quality_scores["research_depth"] * 0.3 +
             quality_scores["content_structure"] * 0.3 +
             quality_scores["visual_appeal"] * 0.2 +
             quality_scores["presentation_quality"] * 0.2)
        )

        return quality_scores

    async def _identify_missing_components(self, analysis: Dict) -> List[str]:
        """Identify missing or incomplete components"""

        missing = []

        # Check for research data
        if not analysis.get("research_content", {}).get("found"):
            missing.append("research_findings")

        # Check for journal content
        if not analysis.get("journal_content", {}).get("found"):
            missing.append("journal_content")

        # Check for media files
        if not analysis.get("media_files", {}).get("found"):
            missing.append("visual_assets")

        # Check for PDF output
        if not analysis.get("pdf_output", {}).get("found"):
            missing.append("pdf_generation")

        return missing

    def _calculate_enhancement_potential(self, analysis: Dict) -> int:
        """Calculate overall enhancement potential score (0-100)"""

        # Start with 100% potential, subtract for existing quality
        potential = 100

        # Reduce potential based on current quality scores
        quality_scores = analysis.get("quality_scores", {})
        overall_quality = quality_scores.get("overall_quality", 0)

        # Potential decreases as quality increases
        potential = max(20, potential - overall_quality * 0.7)

        # Increase potential if there are missing components that could be added
        missing_count = len(analysis.get("missing_components", []))
        if missing_count > 0:
            potential = min(100, potential + (missing_count * 15))

        return int(potential)

    async def _generate_recommendations(self, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate specific enhancement recommendations"""

        recommendations = []
        completion_map = analysis.get("completion_map", {})
        quality_scores = analysis.get("quality_scores", {})
        missing = analysis.get("missing_components", [])

        # Recommendations for missing components
        if "research_findings" in missing:
            recommendations.append({
                "type": "missing_research",
                "priority": "high",
                "title": "Add Research Findings",
                "description": "Generate research-backed insights to enhance journal credibility",
                "agents": ["research_agent"],
                "estimated_time": 10,
                "impact_score": 85
            })

        if "journal_content" in missing:
            recommendations.append({
                "type": "missing_content",
                "priority": "high",
                "title": "Create Journal Content",
                "description": "Generate structured journal content with daily entries",
                "agents": ["content_curator_agent"],
                "estimated_time": 15,
                "impact_score": 90
            })

        if "visual_assets" in missing:
            recommendations.append({
                "type": "missing_media",
                "priority": "medium",
                "title": "Add Visual Elements",
                "description": "Generate images and graphics to enhance visual appeal",
                "agents": ["media_agent"],
                "estimated_time": 8,
                "impact_score": 70
            })

        if "pdf_generation" in missing:
            recommendations.append({
                "type": "missing_pdf",
                "priority": "high",
                "title": "Generate PDF Output",
                "description": "Create professional PDF documents for sharing and printing",
                "agents": ["pdf_builder_agent"],
                "estimated_time": 5,
                "impact_score": 95
            })

        # Quality improvement recommendations
        if quality_scores.get("research_depth", 0) < 70:
            recommendations.append({
                "type": "enhance_research",
                "priority": "medium",
                "title": "Deepen Research Content",
                "description": "Add more comprehensive research findings and expert insights",
                "agents": ["research_agent"],
                "estimated_time": 8,
                "impact_score": 60
            })

        if quality_scores.get("content_structure", 0) < 80:
            recommendations.append({
                "type": "enhance_content",
                "priority": "medium",
                "title": "Improve Content Structure",
                "description": "Enhance journal organization and flow for better user experience",
                "agents": ["content_curator_agent", "editor_agent"],
                "estimated_time": 12,
                "impact_score": 65
            })

        if quality_scores.get("visual_appeal", 0) < 60:
            recommendations.append({
                "type": "enhance_visuals",
                "priority": "low",
                "title": "Enhance Visual Appeal",
                "description": "Add more visual elements and improve overall design",
                "agents": ["media_agent"],
                "estimated_time": 10,
                "impact_score": 50
            })

        # Sort recommendations by impact score
        recommendations.sort(key=lambda x: x["impact_score"], reverse=True)

        return recommendations[:10]  # Return top 10 recommendations

    def _get_project_directory(self, project: Project) -> Optional[str]:
        """Get the directory where project files are stored"""

        # This would need to be implemented based on your file storage system
        # For now, return a placeholder
        return f"/tmp/crewai_output/{project.title.replace(' ', '_')}_{project.id}"

    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure for projects with no files"""

        return {
            "completion_map": {
                "research_agent": 0,
                "content_curator_agent": 0,
                "editor_agent": 0,
                "media_agent": 0,
                "pdf_builder_agent": 0
            },
            "quality_scores": {
                "research_depth": 0,
                "content_structure": 0,
                "visual_appeal": 0,
                "presentation_quality": 0,
                "overall_quality": 0
            },
            "missing_components": ["research_findings", "journal_content", "visual_assets", "pdf_generation"],
            "existing_files": [],
            "project_age_days": 0,
            "content_size": 0,
            "enhancement_potential": 100
        }

    def _calculate_project_age(self, project: Project) -> int:
        """Calculate project age in days"""

        if project.created_at:
            return (datetime.now() - project.created_at).days
        return 0

    def _count_journal_days(self, content: Any) -> int:
        """Count the number of days in journal content"""

        if isinstance(content, list):
            return len(content)
        elif isinstance(content, dict):
            # Look for day keys or similar structure
            day_count = 0
            for key in content.keys():
                if "day" in key.lower() and key.replace("day", "").isdigit():
                    day_count += 1
            return day_count
        return 0

    def _assess_content_completeness(self, content: Any) -> int:
        """Assess the completeness of journal content (0-100)"""

        if not content:
            return 0

        # Basic completeness assessment
        score = 0

        # Check for structure elements
        if isinstance(content, dict):
            required_elements = ["title", "introduction", "daily_entries", "conclusion"]
            found_elements = sum(1 for element in required_elements if any(element in str(key).lower() for key in content.keys()))
            score = int((found_elements / len(required_elements)) * 100)

        elif isinstance(content, list):
            # Assume list contains daily entries
            if len(content) >= 30:
                score = 100
            elif len(content) >= 15:
                score = 70
            elif len(content) >= 5:
                score = 40
            else:
                score = 20

        return score

# Global instance
journal_content_analyzer = JournalContentAnalyzer()