"""
Journal Library Scanner Service

Scans LLM_output directory for CrewAI-generated journals and provides
structured access to completed projects for the web interface.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class JournalScannerService:
    """Service to scan and parse CrewAI output directories"""

    def __init__(self, llm_output_dir: str = "../LLM_output"):
        self.llm_output_dir = Path(llm_output_dir)
        self.projects_cache = {}
        self.last_scan = None

    def scan_projects(self) -> List[Dict[str, any]]:
        """Scan LLM_output directory and return list of projects"""
        try:
            if not self.llm_output_dir.exists():
                logger.warning(f"LLM_output directory not found: {self.llm_output_dir}")
                return []

            projects = []

            # Each subdirectory in LLM_output is a project
            for project_dir in self.llm_output_dir.iterdir():
                if project_dir.is_dir():
                    project_info = self._parse_project(project_dir)
                    if project_info:
                        projects.append(project_info)

            # Sort by creation date (newest first)
            projects.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            self.projects_cache = {p['id']: p for p in projects}
            self.last_scan = datetime.now()

            return projects

        except Exception as e:
            logger.error(f"Error scanning projects: {e}")
            return []

    def get_project_by_id(self, project_id: str) -> Optional[Dict[str, any]]:
        """Get specific project details by ID"""
        if not self.projects_cache:
            self.scan_projects()

        return self.projects_cache.get(project_id)

    def get_project_files(self, project_id: str) -> Dict[str, List[str]]:
        """Get file structure for a specific project"""
        project = self.get_project_by_id(project_id)
        if not project:
            return {}

        project_path = self.llm_output_dir / project_id

        files = {
            'pdfs': [],
            'media': [],
            'data': [],
            'all': []
        }

        try:
            # Scan for files in subdirectories
            for root, dirs, filenames in os.walk(project_path):
                rel_path = Path(root).relative_to(project_path)

                for filename in filenames:
                    file_path = Path(root) / filename
                    rel_file_path = str(rel_path / filename)

                    # Categorize files by directory
                    if 'PDF_output' in str(root):
                        if filename.endswith('.pdf'):
                            files['pdfs'].append(rel_file_path)
                    elif 'media' in str(root):
                        files['media'].append(rel_file_path)
                    elif 'Json_output' in str(root) or 'LLM_output' in str(root):
                        if filename.endswith('.json'):
                            files['data'].append(rel_file_path)

                    files['all'].append(rel_file_path)

            return files

        except Exception as e:
            logger.error(f"Error scanning project files: {e}")
            return {}

    def get_file_path(self, project_id: str, file_path: str) -> Path:
        """Get absolute file path for download"""
        project = self.get_project_by_id(project_id)
        if not project:
            return None

        return self.llm_output_dir / project_id / file_path

    def _parse_project(self, project_path: Path) -> Optional[Dict[str, any]]:
        """Parse project directory to extract metadata"""
        try:
            # Extract project ID from directory name
            project_id = project_path.name

            # Look for metadata in JSON files
            json_dir = project_path / "Json_output"
            llm_dir = project_path / "LLM_output"

            # Generate a better title from folder name
            folder_title = self._extract_title_from_foldername(project_id)

            metadata = {
                'id': project_id,
                'title': folder_title,
                'theme': 'unknown',
                'author_style': 'unknown',
                'created_at': self._parse_date_from_filename(project_id),
                'status': 'completed',
                'files': {}
            }

            # Try to extract title from JSON files
            title_found = False
            for json_file in json_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'title' in data and data['title']:
                            metadata['title'] = data['title']
                            title_found = True
                        if 'theme' in data:
                            metadata['theme'] = data['theme']
                        if 'author_style' in data:
                            metadata['author_style'] = data['author_style']
                        if title_found:
                            break
                except Exception as e:
                    logger.debug(f"Could not read {json_file}: {e}")

            # Check if PDFs exist (indicates completion)
            pdf_dir = project_path / "PDF_output"
            if pdf_dir.exists():
                pdf_files = list(pdf_dir.glob("*.pdf"))
                metadata['has_pdfs'] = len(pdf_files) > 0

            return metadata

        except Exception as e:
            logger.error(f"Error parsing project {project_path}: {e}")
            return None

    def _extract_title_from_foldername(self, foldername: str) -> str:
        """Extract a readable title from folder name"""
        try:
            # If foldername contains date at the end, extract the title part
            if '_' in foldername:
                parts = foldername.split('_')
                # Check if last part looks like a date (YYYY-MM-DD)
                last_part = parts[-1]
                if len(last_part) == 10 and last_part.count('-') == 2:
                    # Remove date part and clean up title
                    title_parts = parts[:-1]
                    title = ' '.join(title_parts)
                    # Replace underscores with spaces and capitalize
                    title = title.replace('_', ' ').title()
                    return title

            # Replace underscores with spaces and capitalize
            title = foldername.replace('_', ' ').title()
            # Remove common suffixes
            for suffix in ['2025', '2024', '2023']:
                if title.endswith(suffix):
                    title = title[:-len(suffix)].strip()

            return title
        except:
            return foldername

    def _parse_date_from_filename(self, filename: str) -> str:
        """Extract date from directory name with multiple patterns supported"""
        try:
            # Pattern 1: '2025-03-20_22-52-24' (journal_creation format)
            if '_' in filename and filename.count('_') >= 1:
                parts = filename.split('_')
                if len(parts) >= 2 and parts[0].count('-') == 2:  # YYYY-MM-DD format
                    date_part = parts[0]
                    time_part = parts[1]
                    return f"{date_part}T{time_part.replace('-', ':')}Z"

            # Pattern 2: Date at the end like 'Project_Name_2025-03-20'
            if '_' in filename:
                parts = filename.split('_')
                for part in reversed(parts):
                    if part.count('-') == 2 and len(part) == 10:  # YYYY-MM-DD
                        # Try to get file modification time as fallback
                        try:
                            import os
                            from pathlib import Path
                            project_path = self.llm_output_dir / filename
                            if project_path.exists():
                                mod_time = datetime.fromtimestamp(project_path.stat().st_mtime())
                                return mod_time.isoformat()
                        except:
                            pass
                        # Return date part with default time
                        return f"{part}T12:00:00Z"

            # Pattern 3: Use filesystem creation time as fallback
            try:
                import os
                project_path = self.llm_output_dir / filename
                if project_path.exists():
                    # Use the earliest time we can find (creation or modification)
                    creation_time = datetime.fromtimestamp(project_path.stat().st_mtime())
                    return creation_time.isoformat()
            except:
                pass

            # Pattern 4: Return current time as last resort
            return datetime.now().isoformat()
        except Exception as e:
            logger.debug(f"Could not parse date from filename {filename}: {e}")
            return datetime.now().isoformat()

    def is_project_complete(self, project_id: str) -> bool:
        """Check if a project has completed successfully"""
        project = self.get_project_by_id(project_id)
        if not project:
            return False

        # Check for PDF files (completion indicator)
        project_path = self.llm_output_dir / project_id
        pdf_dir = project_path / "PDF_output"

        return pdf_dir.exists() and len(list(pdf_dir.glob("*.pdf"))) > 0