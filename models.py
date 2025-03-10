from pydantic import BaseModel, Field
from typing import List, Optional

class CourseInput(BaseModel):
    """Input parameters for course creation"""
    topic: str = Field(..., description="The main topic of the course")
    course_subject: str = Field(..., description="The broader subject category")
    course_topic: str = Field(..., description="The specific topic within the subject")

class ResearchFinding(BaseModel):
    """Individual research finding"""
    content: str = Field(..., description="The content of the finding")
    source: Optional[str] = Field(None, description="Source of the finding")

class ImageReference(BaseModel):
    """Reference to an image to be used in the course"""
    description: str = Field(..., description="Description of the image")
    source: Optional[str] = Field(None, description="Source URL or reference")

class ResearchData(BaseModel):
    """Data collected by the Research Agent"""
    topic: str = Field(..., description="Research topic")
    findings: List[ResearchFinding] = Field(default_factory=list, description="List of research findings")
    image_refs: List[ImageReference] = Field(default_factory=list, description="List of image references")

class CourseModule(BaseModel):
    """Individual module in the course"""
    title: str = Field(..., description="Module title")
    content: str = Field(..., description="Module content")
    image_placement: Optional[str] = Field(None, description="Description of where to place an image")

class DraftContent(BaseModel):
    """Draft content created by the Content Curator Agent"""
    title: str = Field(..., description="Course title")
    modules: List[CourseModule] = Field(default_factory=list, description="List of course modules")
    
class FinalContent(BaseModel):
    """Final content after editing"""
    title: str = Field(..., description="Course title")
    modules: List[CourseModule] = Field(default_factory=list, description="List of course modules")
    notes: Optional[str] = Field(None, description="Additional notes or comments")

class PDFContent(BaseModel):
    """Content for PDF generation"""
    title: str = Field(..., description="Course title")
    body: List[CourseModule] = Field(default_factory=list, description="Content modules for the PDF")
    footer: str = Field("© CourseCraft Crew", description="Footer text for the PDF")
    image_paths: List[str] = Field(default_factory=list, description="Paths to images to include")