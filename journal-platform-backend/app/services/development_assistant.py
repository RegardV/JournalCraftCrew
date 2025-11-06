"""
Development Assistant Service

This service provides intelligent development assistance using Archon's knowledge base
to help developers make informed technical decisions, research implementation patterns,
and get best practices guidance for building the Journal Craft Crew platform.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import Archon client
try:
    from app.services.archon_client import ArchonServiceClient
    ARCHON_AVAILABLE = True
except ImportError:
    ARCHON_AVAILABLE = False
    logging.warning("Archon client not available - development assistant features will be disabled")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevelopmentAssistant:
    """
    Development assistant that uses Archon knowledge base for technical guidance.

    This service helps developers with:
    - Technical research and architecture decisions
    - Implementation pattern recommendations
    - Best practices guidance
    - File storage solution research
    - Authentication pattern research
    - Deployment strategy guidance
    """

    def __init__(self):
        """Initialize the development assistant."""
        self.archon_client = None
        self.enabled = False

        if ARCHON_AVAILABLE:
            try:
                self.archon_client = ArchonServiceClient()
                self.enabled = True
                logger.info("Development assistant initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Archon client: {e}")
                self.enabled = False
        else:
            logger.warning("Development assistant disabled - Archon not available")

    def is_enabled(self) -> bool:
        """Check if development assistant functionality is available."""
        return self.enabled and self.archon_client is not None

    async def research_file_storage_solutions(self) -> Dict[str, Any]:
        """
        Research file storage solutions for journal outputs.

        Returns:
            Research on Google Drive, Dropbox, AWS S3, and other storage options
        """
        if not self.is_enabled():
            return self._get_fallback_research("file storage solutions")

        try:
            # Create comprehensive search query for file storage
            search_query = """
            file storage solutions comparison Google Drive Dropbox AWS S3
            VPS hosting automated file upload API integration
            journal output storage user file management cloud storage
            pricing limitations authentication security best practices
            """

            # Search Archon knowledge base
            results = await self.archon_client.search_knowledge_base(
                query=search_query,
                match_count=10
            )

            # Process and categorize results
            processed_results = self._process_storage_research(results)

            logger.info("File storage solutions research completed")
            return processed_results

        except Exception as e:
            logger.error(f"Error researching file storage solutions: {e}")
            return self._get_fallback_research("file storage solutions")

    async def research_authentication_patterns(self) -> Dict[str, Any]:
        """
        Research authentication patterns for the platform.

        Returns:
            Research on Firebase, OAuth, JWT, and other authentication options
        """
        if not self.is_enabled():
            return self._get_fallback_research("authentication patterns")

        try:
            # Create comprehensive search query for authentication
            search_query = """
            authentication patterns comparison Firebase OAuth JWT
            React TypeScript frontend authentication FastAPI backend
            third-party login Google Apple GitHub social authentication
            session management security best practices token refresh
            user registration email verification password reset flows
            """

            # Search Archon knowledge base
            results = await self.archon_client.search_knowledge_base(
                query=search_query,
                match_count=8
            )

            # Process authentication research
            processed_results = self._process_authentication_research(results)

            logger.info("Authentication patterns research completed")
            return processed_results

        except Exception as e:
            logger.error(f"Error researching authentication patterns: {e}")
            return self._get_fallback_research("authentication patterns")

    async def research_vps_deployment_strategies(self) -> Dict[str, Any]:
        """
        Research VPS deployment strategies and hosting options.

        Returns:
            Research on deployment, hosting, and infrastructure management
        """
        if not self.is_enabled():
            return self._get_fallback_research("VPS deployment strategies")

        try:
            # Create comprehensive search query for deployment
            search_query = """
            VPS deployment strategies FastAPI React production hosting
            Docker containerization Nginx reverse proxy SSL certificates
            automated deployment CI/CD GitHub Actions monitoring logging
            database deployment PostgreSQL Redis backup strategies
            server security hardening performance optimization scaling
            """

            # Search Archon knowledge base
            results = await self.archon_client.search_knowledge_base(
                query=search_query,
                match_count=8
            )

            # Process deployment research
            processed_results = self._process_deployment_research(results)

            logger.info("VPS deployment strategies research completed")
            return processed_results

        except Exception as e:
            logger.error(f"Error researching VPS deployment strategies: {e}")
            return self._get_fallback_research("VPS deployment strategies")

    async def get_architecture_guidance(self, project_context: str) -> Dict[str, Any]:
        """
        Get architecture guidance based on project context.

        Args:
            project_context: Description of the architecture question or challenge

        Returns:
            Architecture recommendations and best practices
        """
        if not self.is_enabled():
            return self._get_fallback_guidance(project_context)

        try:
            # Create architecture-specific search query
            search_query = f"""
            software architecture best practices {project_context}
            React FastAPI microservices patterns database design
            API design patterns scalability performance optimization
            security architecture authentication authorization
            deployment architecture Docker containerization
            """

            # Search Archon knowledge base
            results = await self.archon_client.search_knowledge_base(
                query=search_query,
                match_count=6
            )

            # Process architecture guidance
            processed_results = self._process_architecture_guidance(results, project_context)

            logger.info(f"Architecture guidance completed for: {project_context}")
            return processed_results

        except Exception as e:
            logger.error(f"Error getting architecture guidance: {e}")
            return self._get_fallback_guidance(project_context)

    async def research_implementation_patterns(self, technology: str, use_case: str) -> Dict[str, Any]:
        """
        Research implementation patterns for specific technologies.

        Args:
            technology: The technology to research (e.g., "React", "FastAPI", "PostgreSQL")
            use_case: The specific use case (e.g., "file upload", "real-time updates", "user management")

        Returns:
            Implementation patterns and code examples
        """
        if not self.is_enabled():
            return self._get_fallback_patterns(technology, use_case)

        try:
            # Create implementation-specific search query
            search_query = f"""
            {technology} implementation patterns {use_case}
            best practices code examples tutorial guide
            common pitfalls performance optimization security considerations
            production deployment testing strategies
            """

            # Search Archon knowledge base
            results = await self.archon_client.search_knowledge_base(
                query=search_query,
                match_count=5
            )

            # Process implementation patterns
            processed_results = self._process_implementation_patterns(results, technology, use_case)

            logger.info(f"Implementation patterns research completed: {technology} - {use_case}")
            return processed_results

        except Exception as e:
            logger.error(f"Error researching implementation patterns: {e}")
            return self._get_fallback_patterns(technology, use_case)

    def _process_storage_research(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and categorize file storage research results."""
        if not results.get('success', False):
            return self._get_fallback_research("file storage solutions")

        items = results.get('data', {}).get('items', [])

        # Categorize storage solutions
        storage_categories = {
            'cloud_storage': [],
            'api_integration': [],
            'security_considerations': [],
            'pricing_models': [],
            'implementation_patterns': []
        }

        for item in items:
            content = item.get('content', '').lower()
            title = item.get('title', '').lower()

            if any(term in content or term in title for term in ['google drive', 'dropbox', 'onedrive']):
                storage_categories['cloud_storage'].append(item)
            elif any(term in content or term in title for term in ['api', 'upload', 'integration']):
                storage_categories['api_integration'].append(item)
            elif any(term in content or term in title for term in ['security', 'authentication', 'oauth']):
                storage_categories['security_considerations'].append(item)
            elif any(term in content or term in title for term in ['pricing', 'cost', 'limits']):
                storage_categories['pricing_models'].append(item)
            elif any(term in content or term in title for term in ['implementation', 'code', 'example']):
                storage_categories['implementation_patterns'].append(item)

        return {
            'success': True,
            'research_topic': 'file storage solutions',
            'categories': storage_categories,
            'total_results': len(items),
            'recommendations': self._generate_storage_recommendations(storage_categories),
            'research_metadata': {
                'timestamp': datetime.now().isoformat(),
                'source': 'archon_knowledge_base'
            }
        }

    def _process_authentication_research(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and categorize authentication research results."""
        if not results.get('success', False):
            return self._get_fallback_research("authentication patterns")

        items = results.get('data', {}).get('items', [])

        # Categorize authentication solutions
        auth_categories = {
            'third_party_auth': [],
            'jwt_patterns': [],
            'session_management': [],
            'security_best_practices': [],
            'frontend_integration': []
        }

        for item in items:
            content = item.get('content', '').lower()
            title = item.get('title', '').lower()

            if any(term in content or term in title for term in ['firebase', 'oauth', 'google', 'apple']):
                auth_categories['third_party_auth'].append(item)
            elif any(term in content or term in title for term in ['jwt', 'token', 'refresh']):
                auth_categories['jwt_patterns'].append(item)
            elif any(term in content or term in title for term in ['session', 'cookie', 'state']):
                auth_categories['session_management'].append(item)
            elif any(term in content or term in title for term in ['security', 'csrf', 'xss']):
                auth_categories['security_best_practices'].append(item)
            elif any(term in content or term in title for term in ['react', 'frontend', 'client']):
                auth_categories['frontend_integration'].append(item)

        return {
            'success': True,
            'research_topic': 'authentication patterns',
            'categories': auth_categories,
            'total_results': len(items),
            'recommendations': self._generate_auth_recommendations(auth_categories),
            'research_metadata': {
                'timestamp': datetime.now().isoformat(),
                'source': 'archon_knowledge_base'
            }
        }

    def _process_deployment_research(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and categorize deployment research results."""
        if not results.get('success', False):
            return self._get_fallback_research("VPS deployment strategies")

        items = results.get('data', {}).get('items', [])

        # Categorize deployment solutions
        deployment_categories = {
            'containerization': [],
            'server_setup': [],
            'security_hardening': [],
            'monitoring_logging': [],
            'database_deployment': []
        }

        for item in items:
            content = item.get('content', '').lower()
            title = item.get('title', '').lower()

            if any(term in content or term in title for term in ['docker', 'container', 'kubernetes']):
                deployment_categories['containerization'].append(item)
            elif any(term in content or term in title for term in ['nginx', 'server', 'ssl', 'https']):
                deployment_categories['server_setup'].append(item)
            elif any(term in content or term in title for term in ['security', 'firewall', 'hardening']):
                deployment_categories['security_hardening'].append(item)
            elif any(term in content or term in title for term in ['monitoring', 'logging', 'metrics']):
                deployment_categories['monitoring_logging'].append(item)
            elif any(term in content or term in title for term in ['database', 'postgresql', 'backup']):
                deployment_categories['database_deployment'].append(item)

        return {
            'success': True,
            'research_topic': 'VPS deployment strategies',
            'categories': deployment_categories,
            'total_results': len(items),
            'recommendations': self._generate_deployment_recommendations(deployment_categories),
            'research_metadata': {
                'timestamp': datetime.now().isoformat(),
                'source': 'archon_knowledge_base'
            }
        }

    def _process_architecture_guidance(self, results: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Process architecture guidance results."""
        if not results.get('success', False):
            return self._get_fallback_guidance(context)

        items = results.get('data', {}).get('items', [])

        return {
            'success': True,
            'guidance_topic': context,
            'recommendations': items[:5],  # Top 5 recommendations
            'best_practices': [item for item in items if 'best practice' in item.get('content', '').lower()],
            'common_pitfalls': [item for item in items if 'pitfall' in item.get('content', '').lower() or 'avoid' in item.get('content', '').lower()],
            'total_results': len(items),
            'research_metadata': {
                'timestamp': datetime.now().isoformat(),
                'source': 'archon_knowledge_base',
                'context': context
            }
        }

    def _process_implementation_patterns(self, results: Dict[str, Any], technology: str, use_case: str) -> Dict[str, Any]:
        """Process implementation patterns results."""
        if not results.get('success', False):
            return self._get_fallback_patterns(technology, use_case)

        items = results.get('data', {}).get('items', [])

        return {
            'success': True,
            'technology': technology,
            'use_case': use_case,
            'patterns': items[:5],  # Top 5 patterns
            'code_examples': [item for item in items if 'code' in item.get('content', '').lower() or 'example' in item.get('content', '').lower()],
            'best_practices': [item for item in items if 'best practice' in item.get('content', '').lower()],
            'total_results': len(items),
            'research_metadata': {
                'timestamp': datetime.now().isoformat(),
                'source': 'archon_knowledge_base'
            }
        }

    def _generate_storage_recommendations(self, categories: Dict[str, List]) -> List[str]:
        """Generate file storage recommendations based on research."""
        recommendations = []

        if categories['cloud_storage']:
            recommendations.append("Consider Google Drive API for user-friendly file storage with familiar interface")

        if categories['api_integration']:
            recommendations.append("Implement robust API integration with retry logic and error handling")

        if categories['security_considerations']:
            recommendations.append("Prioritize OAuth2 authentication and secure file access controls")

        if categories['pricing_models']:
            recommendations.append("Research pricing tiers and storage limits for cost optimization")

        return recommendations

    def _generate_auth_recommendations(self, categories: Dict[str, List]) -> List[str]:
        """Generate authentication recommendations based on research."""
        recommendations = []

        if categories['third_party_auth']:
            recommendations.append("Implement Firebase Authentication for comprehensive third-party login support")

        if categories['jwt_patterns']:
            recommendations.append("Use JWT tokens with refresh token strategy for secure session management")

        if categories['security_best_practices']:
            recommendations.append("Implement CSRF protection and secure cookie handling")

        if categories['frontend_integration']:
            recommendations.append("Create seamless frontend authentication flow with proper error handling")

        return recommendations

    def _generate_deployment_recommendations(self, categories: Dict[str, List]) -> List[str]:
        """Generate deployment recommendations based on research."""
        recommendations = []

        if categories['containerization']:
            recommendations.append("Use Docker containers for consistent deployment environments")

        if categories['server_setup']:
            recommendations.append("Configure Nginx reverse proxy with SSL termination")

        if categories['security_hardening']:
            recommendations.append("Implement server security hardening and regular updates")

        if categories['monitoring_logging']:
            recommendations.append("Set up comprehensive monitoring and centralized logging")

        return recommendations

    def _get_fallback_research(self, topic: str) -> Dict[str, Any]:
        """Get fallback research when Archon is unavailable."""
        return {
            'success': False,
            'research_topic': topic,
            'categories': {},
            'total_results': 0,
            'recommendations': [f"Research {topic} manually - Archon knowledge base temporarily unavailable"],
            'fallback_used': True,
            'research_metadata': {
                'timestamp': datetime.now().isoformat(),
                'reason': 'archon_unavailable'
            }
        }

    def _get_fallback_guidance(self, context: str) -> Dict[str, Any]:
        """Get fallback guidance when Archon is unavailable."""
        return {
            'success': False,
            'guidance_topic': context,
            'recommendations': [],
            'best_practices': [],
            'common_pitfalls': [],
            'total_results': 0,
            'fallback_used': True,
            'research_metadata': {
                'timestamp': datetime.now().isoformat(),
                'reason': 'archon_unavailable'
            }
        }

    def _get_fallback_patterns(self, technology: str, use_case: str) -> Dict[str, Any]:
        """Get fallback patterns when Archon is unavailable."""
        return {
            'success': False,
            'technology': technology,
            'use_case': use_case,
            'patterns': [],
            'code_examples': [],
            'best_practices': [],
            'total_results': 0,
            'fallback_used': True,
            'research_metadata': {
                'timestamp': datetime.now().isoformat(),
                'reason': 'archon_unavailable'
            }
        }

# Singleton instance for use throughout the application
development_assistant = DevelopmentAssistant()

# Convenience functions for developers
async def research_file_storage():
    """Convenience function for researching file storage solutions."""
    return await development_assistant.research_file_storage_solutions()

async def research_authentication():
    """Convenience function for researching authentication patterns."""
    return await development_assistant.research_authentication_patterns()

async def research_deployment():
    """Convenience function for researching VPS deployment strategies."""
    return await development_assistant.research_vps_deployment_strategies()

async def get_architecture_advice(context: str):
    """Convenience function for getting architecture guidance."""
    return await development_assistant.get_architecture_guidance(context)

async def research_implementation(technology: str, use_case: str):
    """Convenience function for researching implementation patterns."""
    return await development_assistant.research_implementation_patterns(technology, use_case)