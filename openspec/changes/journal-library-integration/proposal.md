# OpenSpec Change: Journal Library Integration

## Why
Enable users to access their completed CrewAI-generated journals through a web-based library interface that displays the folder structure and provides PDF access.

## What Changes
- Create journal library UI component to display CrewAI output
- Add API endpoints to read `LLM_output/` directory structure
- Implement file browser that replicates folder hierarchy
- Add PDF viewing and download capabilities
- Integrate with existing authentication system

## Current State Analysis

### ✅ **Working Components**
- **Landing Page**: Complete login/registration with third-party auth planning
- **CrewAI System**: 8 working agents (manager, content_curator, pdf_builder, media, editor, research, discovery, onboarding)
- **Output Structure**: `LLM_output/{date}_{timestamp}/` folders with generated content
- **PDF Generation**: Professional PDF creation with media support
- **File Structure**: Each project contains:
  - `LLM_output/` - Generated content
  - `Json_output/` - Structured data
  - `media/` - Images and assets
  - `PDF_output/` - Final PDFs

### ❌ **Missing Integration**
- **Library UI**: No interface to display completed journals
- **File Access**: No API to read CrewAI output folders
- **Folder Replication**: UI doesn't mirror actual directory structure
- **PDF Display**: No way to view/download generated PDFs
- **Project Status**: No completion tracking from web interface

## Implementation Strategy

### **Phase 1: Backend API Development**
1. **File System Scanner**: Read `LLM_output/` directory structure
2. **API Endpoints**:
   - `GET /api/journals/library` - List user's completed projects
   - `GET /api/journals/{project_id}/files` - Get project file tree
   - `GET /api/journals/{project_id}/download/{file_path}` - Download files
   - `GET /api/journals/{project_id}/status` - Check CrewAI completion status

### **Phase 2: Frontend Library Interface**
1. **Journal Library Component**: Display user's completed journals
2. **File Browser Component**: Replicate folder structure in UI
3. **PDF Viewer**: In-browser PDF display
4. **Download Manager**: File download capabilities
5. **Project Status**: Real-time CrewAI progress tracking

### **Phase 3: Integration Enhancement**
1. **Auto-refresh**: Library updates when CrewAI completes projects
2. **File Management**: Organized display of generated assets
3. **User Experience**: Intuitive navigation through journal content
4. **Media Support**: Display images alongside PDFs

## Technical Architecture

### **File Structure Mapping**
```
LLM_output/
├── 2025-03-20_22-52-24/
│   ├── LLM_output/
│   │   ├── journal_content.json
│   │   └── lead_magnet.json
│   ├── Json_output/
│   │   ├── 30day_journal_anxiety_empathetic.json
│   │   └── 6day_lead_magnet_anxiety_empathetic.json
│   ├── media/
│   │   ├── cover_image.jpg
│   │   └── day_01_image.jpg
│   └── PDF_output/
│       ├── journal.pdf
│       └── lead_magnet.pdf
└── journal_creation_b8b8bb66-7420-4afd-87fc-e06a0c577fe3/
    ├── [similar structure]
```

### **API Response Format**
```json
{
  "projects": [
    {
      "id": "2025-03-20_22-52-24",
      "title": "My Mindfulness Journal",
      "theme": "anxiety",
      "author_style": "empathetic",
      "created_at": "2025-03-20T22:52:24Z",
      "status": "completed",
      "files": {
        "pdfs": ["journal.pdf", "lead_magnet.pdf"],
        "media": ["cover_image.jpg", "day_01_image.jpg"],
        "data": ["journal_content.json", "lead_magnet.json"]
      }
    }
  ]
}
```

## Success Criteria

### **Functional Requirements**
- [ ] Users can view all completed journals in library
- [ ] Folder structure accurately reflects CrewAI output
- [ ] PDF files display and download correctly
- [ ] Media assets shown alongside journal content
- [ ] Real-time updates when CrewAI completes new projects

### **User Experience Goals**
- [ ] Intuitive navigation through journal library
- [ ] One-click access to generated PDFs
- [ ] Visual preview of journal content and assets
- [ ] Organized display of multiple completed projects

## Impact
- **Affected specs**: frontend, integration, user-experience
- **New user value**: Access to completed CrewAI journals
- **Enhanced workflow**: Complete journal creation to consumption pipeline