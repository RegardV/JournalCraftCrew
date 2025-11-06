"""
Journal Service

This service handles all journal entry operations including CRUD,
search, statistics, and file management.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_, and_
from fastapi import UploadFile
import os
import uuid
import json

from app.models.journal import JournalEntry

logger = logging.getLogger(__name__)

class JournalService:
    """Service for managing journal entries"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_journal_entry(
        self,
        user_id: int,
        title: str,
        content: str,
        ai_generated_content: Optional[str] = None,
        ai_theme: Optional[str] = None,
        ai_generation_date: Optional[str] = None,
        generation_prompt: Optional[str] = None,
        mood: Optional[str] = None,
        tags: Optional[List[str]] = None,
        cover_image: Optional[str] = None,
        attached_images: Optional[List[str]] = None,
        is_private: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new journal entry

        Args:
            user_id: User ID
            title: Entry title
            content: Entry content
            ai_generated_content: Original AI-generated content
            ai_theme: Theme used for AI generation
            ai_generation_date: When AI content was generated
            generation_prompt: Prompt used for generation
            mood: Mood of the entry
            tags: List of tags
            cover_image: Cover image URL
            attached_images: List of attached image URLs
            is_private: Whether entry is private

        Returns:
            Created journal entry data
        """
        try:
            # Create new journal entry
            journal_entry = JournalEntry(
                user_id=user_id,
                title=title,
                content=content,
                ai_generated_content=ai_generated_content,
                ai_theme=ai_theme,
                ai_generation_date=datetime.fromisoformat(ai_generation_date) if ai_generation_date else None,
                generation_prompt=generation_prompt,
                mood=mood,
                tags=tags or [],
                cover_image=cover_image,
                attached_images=attached_images or [],
                is_private=is_private,
                is_favorite=False,
                is_customized=False,
                word_count=len(content.split()),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Save to database
            self.db.add(journal_entry)
            await self.db.commit()
            await self.db.refresh(journal_entry)

            logger.info(f"Created journal entry {journal_entry.id} for user {user_id}")

            return self._format_journal_entry(journal_entry)

        except Exception as e:
            logger.error(f"Failed to create journal entry: {e}")
            await self.db.rollback()
            raise RuntimeError(f"Failed to create journal entry: {str(e)}")

    async def get_journal_entry(self, entry_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get a specific journal entry

        Args:
            entry_id: Entry ID
            user_id: User ID

        Returns:
            Journal entry data
        """
        try:
            # Query the entry
            result = await self.db.execute(
                select(JournalEntry).where(
                    and_(
                        JournalEntry.id == entry_id,
                        JournalEntry.user_id == user_id
                    )
                )
            )
            entry = result.scalar_one_or_none()

            if not entry:
                raise ValueError(f"Journal entry {entry_id} not found")

            return self._format_journal_entry(entry)

        except Exception as e:
            logger.error(f"Failed to get journal entry {entry_id}: {e}")
            raise RuntimeError(f"Failed to retrieve journal entry: {str(e)}")

    async def get_user_entries(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        mood_filter: Optional[str] = None,
        tag_filter: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user's journal entries with filtering and pagination

        Args:
            user_id: User ID
            skip: Number of entries to skip
            limit: Maximum number of entries to return
            search: Search query
            mood_filter: Filter by mood
            tag_filter: Filter by tag
            date_from: Filter by date from (ISO string)
            date_to: Filter by date to (ISO string)

        Returns:
            Dictionary with entries and pagination info
        """
        try:
            # Build base query
            query = select(JournalEntry).where(JournalEntry.user_id == user_id)

            # Apply filters
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        JournalEntry.title.ilike(search_term),
                        JournalEntry.content.ilike(search_term)
                    )
                )

            if mood_filter:
                query = query.where(JournalEntry.mood == mood_filter)

            if tag_filter:
                query = query.where(JournalEntry.tags.contains([tag_filter]))

            if date_from:
                date_from_dt = datetime.fromisoformat(date_from)
                query = query.where(JournalEntry.created_at >= date_from_dt)

            if date_to:
                date_to_dt = datetime.fromisoformat(date_to)
                query = query.where(JournalEntry.created_at <= date_to_dt)

            # Get total count
            count_query = select(func.count(JournalEntry.id)).where(JournalEntry.user_id == user_id)
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply ordering and pagination
            query = query.order_by(desc(JournalEntry.created_at)).offset(skip).limit(limit)

            # Execute query
            result = await self.db.execute(query)
            entries = result.scalars().all()

            # Format entries
            formatted_entries = [self._format_journal_entry(entry) for entry in entries]

            return {
                "entries": formatted_entries,
                "pagination": {
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "pages": (total + limit - 1) // limit
                }
            }

        except Exception as e:
            logger.error(f"Failed to get user entries: {e}")
            raise RuntimeError(f"Failed to retrieve journal entries: {str(e)}")

    async def update_journal_entry(
        self,
        entry_id: int,
        user_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        mood: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_private: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        is_customized: bool = False
    ) -> Dict[str, Any]:
        """
        Update a journal entry

        Args:
            entry_id: Entry ID
            user_id: User ID
            title: New title
            content: New content
            mood: New mood
            tags: New tags
            is_private: New privacy setting
            is_favorite: New favorite setting
            is_customized: Whether entry has been customized

        Returns:
            Updated journal entry data
        """
        try:
            # Get existing entry
            result = await self.db.execute(
                select(JournalEntry).where(
                    and_(
                        JournalEntry.id == entry_id,
                        JournalEntry.user_id == user_id
                    )
                )
            )
            entry = result.scalar_one_or_none()

            if not entry:
                raise ValueError(f"Journal entry {entry_id} not found")

            # Update fields
            if title is not None:
                entry.title = title
            if content is not None:
                entry.content = content
                entry.word_count = len(content.split())
            if mood is not None:
                entry.mood = mood
            if tags is not None:
                entry.tags = tags
            if is_private is not None:
                entry.is_private = is_private
            if is_favorite is not None:
                entry.is_favorite = is_favorite

            entry.is_customized = is_customized
            entry.updated_at = datetime.utcnow()

            # Save changes
            await self.db.commit()
            await self.db.refresh(entry)

            logger.info(f"Updated journal entry {entry_id} for user {user_id}")

            return self._format_journal_entry(entry)

        except Exception as e:
            logger.error(f"Failed to update journal entry {entry_id}: {e}")
            await self.db.rollback()
            raise RuntimeError(f"Failed to update journal entry: {str(e)}")

    async def delete_journal_entry(self, entry_id: int, user_id: int) -> None:
        """
        Delete a journal entry

        Args:
            entry_id: Entry ID
            user_id: User ID
        """
        try:
            # Get existing entry
            result = await self.db.execute(
                select(JournalEntry).where(
                    and_(
                        JournalEntry.id == entry_id,
                        JournalEntry.user_id == user_id
                    )
                )
            )
            entry = result.scalar_one_or_none()

            if not entry:
                raise ValueError(f"Journal entry {entry_id} not found")

            # Delete entry
            await self.db.delete(entry)
            await self.db.commit()

            logger.info(f"Deleted journal entry {entry_id} for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to delete journal entry {entry_id}: {e}")
            await self.db.rollback()
            raise RuntimeError(f"Failed to delete journal entry: {str(e)}")

    async def update_last_accessed(self, entry_id: int, user_id: int) -> None:
        """Update the last accessed timestamp for an entry"""
        try:
            result = await self.db.execute(
                select(JournalEntry).where(
                    and_(
                        JournalEntry.id == entry_id,
                        JournalEntry.user_id == user_id
                    )
                )
            )
            entry = result.scalar_one_or_none()

            if entry:
                entry.last_accessed = datetime.utcnow()
                await self.db.commit()

        except Exception as e:
            logger.error(f"Failed to update last accessed for entry {entry_id}: {e}")

    async def upload_entry_image(
        self,
        entry_id: int,
        user_id: int,
        file: UploadFile,
        is_ai_generated: bool = False
    ) -> Dict[str, Any]:
        """
        Upload an image for a journal entry

        Args:
            entry_id: Entry ID
            user_id: User ID
            file: Uploaded file
            is_ai_generated: Whether image is AI generated

        Returns:
            Image data
        """
        try:
            # Validate file
            if not file.content_type.startswith('image/'):
                raise ValueError("Only image files are allowed")

            # Generate unique filename
            file_extension = file.filename.split('.')[-1] if file.filename else 'jpg'
            filename = f"{uuid.uuid4()}.{file_extension}"

            # Create upload directory
            upload_dir = f"uploads/journals/{user_id}"
            os.makedirs(upload_dir, exist_ok=True)

            # Save file
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # Get the journal entry
            result = await self.db.execute(
                select(JournalEntry).where(
                    and_(
                        JournalEntry.id == entry_id,
                        JournalEntry.user_id == user_id
                    )
                )
            )
            entry = result.scalar_one_or_none()

            if not entry:
                raise ValueError(f"Journal entry {entry_id} not found")

            # Update entry with image
            image_url = f"/static/uploads/journals/{user_id}/{filename}"

            if is_ai_generated and not entry.cover_image:
                entry.cover_image = image_url
            else:
                if not entry.attached_images:
                    entry.attached_images = []
                entry.attached_images.append(image_url)

            entry.updated_at = datetime.utcnow()
            await self.db.commit()

            return {
                "id": str(uuid.uuid4()),
                "url": image_url,
                "filename": filename,
                "size": len(content),
                "content_type": file.content_type,
                "is_ai_generated": is_ai_generated
            }

        except Exception as e:
            logger.error(f"Failed to upload image for entry {entry_id}: {e}")
            raise RuntimeError(f"Failed to upload image: {str(e)}")

    async def get_journal_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Get journal statistics for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with statistics
        """
        try:
            # Total entries
            total_query = select(func.count(JournalEntry.id)).where(JournalEntry.user_id == user_id)
            total_result = await self.db.execute(total_query)
            total_entries = total_result.scalar()

            # Entries by mood
            mood_query = select(
                JournalEntry.mood,
                func.count(JournalEntry.id)
            ).where(
                and_(
                    JournalEntry.user_id == user_id,
                    JournalEntry.mood.isnot(None)
                )
            ).group_by(JournalEntry.mood)
            mood_result = await self.db.execute(mood_query)
            mood_stats = {row[0]: row[1] for row in mood_result}

            # AI generated entries
            ai_query = select(func.count(JournalEntry.id)).where(
                and_(
                    JournalEntry.user_id == user_id,
                    JournalEntry.ai_generated_content.isnot(None)
                )
            )
            ai_result = await self.db.execute(ai_query)
            ai_generated = ai_result.scalar()

            # Favorite entries
            favorite_query = select(func.count(JournalEntry.id)).where(
                and_(
                    JournalEntry.user_id == user_id,
                    JournalEntry.is_favorite == True
                )
            )
            favorite_result = await self.db.execute(favorite_query)
            favorites = favorite_result.scalar()

            # Total word count
            word_count_query = select(func.sum(JournalEntry.word_count)).where(JournalEntry.user_id == user_id)
            word_count_result = await self.db.execute(word_count_query)
            total_words = word_count_result.scalar() or 0

            # Recent activity (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_query = select(func.count(JournalEntry.id)).where(
                and_(
                    JournalEntry.user_id == user_id,
                    JournalEntry.created_at >= seven_days_ago
                )
            )
            recent_result = await self.db.execute(recent_query)
            recent_entries = recent_result.scalar()

            return {
                "total_entries": total_entries,
                "ai_generated_entries": ai_generated,
                "favorite_entries": favorites,
                "total_words": total_words,
                "recent_entries": recent_entries,
                "mood_distribution": mood_stats,
                "average_entry_length": total_words / total_entries if total_entries > 0 else 0
            }

        except Exception as e:
            logger.error(f"Failed to get journal statistics: {e}")
            raise RuntimeError(f"Failed to retrieve statistics: {str(e)}")

    async def search_entries(
        self,
        user_id: int,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search journal entries

        Args:
            user_id: User ID
            query: Search query
            skip: Number of entries to skip
            limit: Maximum number of entries to return

        Returns:
            Dictionary with entries and pagination info
        """
        try:
            search_term = f"%{query}%"

            # Build search query
            search_query = select(JournalEntry).where(
                and_(
                    JournalEntry.user_id == user_id,
                    or_(
                        JournalEntry.title.ilike(search_term),
                        JournalEntry.content.ilike(search_term)
                    )
                )
            ).order_by(desc(JournalEntry.created_at))

            # Get total count
            count_query = select(func.count(JournalEntry.id)).where(
                and_(
                    JournalEntry.user_id == user_id,
                    or_(
                        JournalEntry.title.ilike(search_term),
                        JournalEntry.content.ilike(search_term)
                    )
                )
            )
            total_result = await self.db.execute(count_query)
            total = total_result.scalar()

            # Apply pagination
            search_query = search_query.offset(skip).limit(limit)
            result = await self.db.execute(search_query)
            entries = result.scalars().all()

            # Format entries
            formatted_entries = [self._format_journal_entry(entry) for entry in entries]

            return {
                "entries": formatted_entries,
                "pagination": {
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                    "pages": (total + limit - 1) // limit
                },
                "query": query
            }

        except Exception as e:
            logger.error(f"Failed to search entries: {e}")
            raise RuntimeError(f"Failed to search entries: {str(e)}")

    async def export_to_project(
        self,
        entry_id: int,
        user_id: int,
        project_data: dict
    ) -> Dict[str, Any]:
        """
        Export journal entry to project format

        Args:
            entry_id: Entry ID
            user_id: User ID
            project_data: Project configuration

        Returns:
            Exported project data
        """
        try:
            # Get the entry
            entry_data = await self.get_journal_entry(entry_id, user_id)

            # Create project structure
            project = {
                "id": str(uuid.uuid4()),
                "title": project_data.get("title", entry_data["title"]),
                "description": project_data.get("description", f"Project based on journal entry: {entry_data['title']}"),
                "type": project_data.get("type", "journal_project"),
                "source_journal_entry": entry_data,
                "created_at": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "content": entry_data["content"],
                "mood": entry_data.get("mood"),
                "tags": entry_data.get("tags", []),
                "theme": entry_data.get("ai_theme"),
                "metadata": {
                    "original_entry_id": entry_id,
                    "export_type": project_data.get("export_type", "full"),
                    "include_ai_content": project_data.get("include_ai_content", False)
                }
            }

            return project

        except Exception as e:
            logger.error(f"Failed to export journal entry to project: {e}")
            raise RuntimeError(f"Failed to export to project: {str(e)}")

    def _format_journal_entry(self, entry: JournalEntry) -> Dict[str, Any]:
        """Format a journal entry for API response"""
        return {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "ai_generated_content": entry.ai_generated_content,
            "word_count": entry.word_count,
            "mood": entry.mood,
            "tags": entry.tags,
            "is_private": entry.is_private,
            "is_favorite": entry.is_favorite,
            "is_customized": entry.is_customized,
            "cover_image": entry.cover_image,
            "attached_images": entry.attached_images,
            "ai_theme": entry.ai_theme,
            "ai_generation_date": entry.ai_generation_date.isoformat() if entry.ai_generation_date else None,
            "generation_prompt": entry.generation_prompt,
            "created_at": entry.created_at.isoformat(),
            "updated_at": entry.updated_at.isoformat(),
            "last_accessed": entry.last_accessed.isoformat() if entry.last_accessed else None
        }