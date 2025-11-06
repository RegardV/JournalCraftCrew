# Unified Archon + OpenSpec System - Complete Usage Guide

## 🎯 Overview

The **Unified Development System** combines structured project management (OpenSpec) with AI-powered development assistance (Archon) to create a self-improving development workflow that learns from every project and session.

### **Core Philosophy**
- **Structured Planning** + **AI-Powered Research** = **Accelerated Development**
- **Every Task Tracked** + **Every Pattern Learned** = **Intelligent Evolution**
- **Session Continuity** + **Knowledge Accumulation** = **Productive Consistency**

## 🚀 Quick Start Guide

### **1. Session Initialization**
```bash
# Start a development session
cd /path/to/project
source ./dev-workflow.sh  # Load workflow commands
dev-start                # Initialize session with context
```

### **2. Complete Development Workflow**
```bash
# Planning Phase
dev-plan "journal library integration"

# Research Phase
dev-research "React file tree components"
# OR
python dev_assistant_cli.py architecture "file browser patterns"

# Implementation Phase
# (Your coding work here)

# Task Tracking
python dev_assistant_cli.py track "Create JournalLibrary component" --status pending
python dev_assistant_cli.py research "React components" --for-task "Create JournalLibrary component"

# Completion
python dev_assistant_cli.py complete "Create JournalLibrary component" --notes "Component created with file tree and PDF viewer"

# OpenSpec Sync
python openspec_sync.py --to-archon    # Push tasks to Archon
python openspec_sync.py --from-archon  # Pull progress back
```

### **3. Session End**
```bash
dev-end                  # Document session progress and plan next session
```

## 📋 Command Reference

### **OpenSpec Integration Commands**
```bash
# Planning & Specification
openspec proposal create "feature-name"              # Create new proposal
openspec task add --research-backed "task description"  # Add informed task
openspec change apply --with-archon-research           # Document implementation
openspec status --show-blocking                       # Check project status

# Synchronization
python openspec_sync.py --to-archon                  # Push OpenSpec → Archon
python openspec_sync.py --from-archon                # Pull Archon → OpenSpec
python openspec_sync.py --sync-all                   # Bidirectional sync
python openspec_sync.py --status                     # Show sync status
```

### **Archon Development Assistant Commands**
```bash
# Task Tracking
python dev_assistant_cli.py track "Task Name" --status pending --context "Description"
python dev_assistant_cli.py status                           # Show project status
python dev_assistant_cli.py complete "Task Name" --notes "Implementation notes"

# Research with Tracking
python dev_assistant_cli.py research "React patterns" --for-task "Component development"

# Classic Research Commands
python dev_assistant_cli.py storage                    # File storage research
python dev_assistant_cli.py auth                       # Authentication patterns
python dev_assistant_cli.py deployment                 # Deployment strategies
python dev_assistant_cli.py architecture "topic"         # Architecture guidance
python dev_assistant_cli.py patterns "React" "use-case"  # Implementation patterns
```

### **Enhanced Workflow Commands (dev-workflow.sh)**
```bash
dev-start              # Start development session
dev-status             # Show current status
dev-research "topic"    # Get Archon research
dev-plan "feature"      # Create OpenSpec proposal
dev-storage            # Quick file storage research
dev-auth               # Quick authentication research
dev-deployment         # Quick deployment research
dev-archon             # Access Archon CLI tools
dev-end                # End development session
```

## 🔧 Advanced Usage Patterns

### **Pattern 1: Research-Backed Task Creation**
```bash
# 1. Start with research
python dev_assistant_cli.py architecture "React file tree components"

# 2. Create informed task
python dev_assistant_cli.py track "Implement file tree component" \
    --status pending \
    --context "React with collapsible folders, search functionality"

# 3. Associate research with task
python dev_assistant_cli.py research "React tree view libraries" \
    --for-task "Implement file tree component"

# 4. Complete with learning capture
python dev_assistant_cli.py complete "Implement file tree component" \
    --notes "Used react-tree-view-library, implemented virtual scrolling"
```

### **Pattern 2: OpenSpec-Driven Development**
```bash
# 1. Create structured proposal
openspec proposal create "journal library frontend"

# 2. Generate research-backed tasks
openspec task breakdown --archon-informed

# 3. Sync tasks to Archon
python openspec_sync.py --to-archon

# 4. Work with Archon guidance
python dev_assistant_cli.py status
python dev_assistant_cli.py research "React component patterns"

# 5. Update progress in both systems
python dev_assistant_cli.py complete "Create JournalLibrary component"
python openspec_sync.py --from-archon
```

### **Pattern 3: Knowledge Accumulation**
```bash
# Each completion builds the knowledge base
python dev_assistant_cli.py complete "Add PDF viewer" \
    --notes "Used react-pdf, implemented zoom controls, page navigation"

# Future research benefits from past work
python dev_assistant_cli.py research "PDF viewing"
# → Returns: "Based on previous implementations: react-pdf works well for..."
```

## 📊 System Features

### **Task Intelligence**
- **Automatic Status Tracking**: Every task maintains complete history
- **Research Association**: Findings automatically linked to relevant tasks
- **Pattern Recognition**: System learns from completed work
- **Context Preservation**: Session-to-session continuity

### **Knowledge Accumulation**
- **Completed Patterns**: Stores implementation approaches for future reference
- **Research Findings**: Preserves valuable research across projects
- **Session History**: Maintains development timeline and insights
- **Best Practices**: Builds library of proven solutions

### **Workflow Integration**
- **Bidirectional Sync**: OpenSpec ↔ Archon seamless integration
- **Progress Visualization**: Real-time project status with AI insights
- **Smart Suggestions**: Context-aware recommendations based on patterns
- **Session Handoff**: Perfect continuity between development sessions

## 🗂️ File Structure

### **Core Files**
```
project-root/
├── dev-assistant_cli.py          # Enhanced Archon CLI
├── openspec_sync.py             # OpenSpec integration
├── dev-workflow.sh              # Interactive workflow commands
├── archon_tasks.json            # Task tracking data
├── archon_knowledge.json        # Knowledge accumulation
└── openspec/
    ├── changes/                 # OpenSpec proposals and tasks
    ├── AGENTS.md               # Agent development guidelines
    └── ...
```

### **Data Organization**
- **archon_tasks.json**: All tracked tasks with history and status
- **archon_knowledge.json**: Accumulated patterns and research findings
- **openspec/changes/**: Structured proposals with markdown tasks
- **SESSION_NOTE-*.md**: Session handoff documentation

## 🎯 Success Metrics

### **Immediate Benefits**
- ✅ **Research Efficiency**: Findings automatically associated with tasks
- ✅ **Task Visibility**: Complete project status at all times
- ✅ **Session Continuity**: Never lose context between sessions
- ✅ **Knowledge Growth**: Every project makes future work easier

### **Long-term Value**
- ✅ **Pattern Library**: Reusable solutions for common problems
- ✅ **Intelligent Suggestions**: AI recommendations based on actual work
- ✅ **Workflow Optimization**: Process improves with every session
- ✅ **Development Acceleration**: Each project builds on previous knowledge

## 🔄 Session Management

### **Starting a Session**
```bash
dev-start
# Shows:
# - Last session progress
# - Current project status
# - Intelligent task suggestions
# - Recent research findings
```

### **During Development**
```bash
# Real-time status updates
python dev_assistant_cli.py status

# Research with automatic task linking
python dev_assistant_cli.py research "topic" --for-task "current task"

# Progress tracking
python dev_assistant_cli.py track "task" --status in_progress
```

### **Ending a Session**
```bash
dev-end
# Prompts for:
# - Session summary
# - Next session priorities
# - Knowledge capture
# - OpenSpec documentation updates
```

## 🚀 Best Practices

### **Development Workflow**
1. **Always start with research** before implementation
2. **Track every task** with appropriate context
3. **Associate research** with relevant tasks automatically
4. **Complete with learning notes** to build knowledge base
5. **Sync regularly** between OpenSpec and Archon

### **Knowledge Building**
1. **Be specific** in implementation notes
2. **Include research findings** in task completion
3. **Document patterns** that work well
4. **Use context** to make future research more effective
5. **Review accumulated knowledge** before starting new work

### **Session Management**
1. **Start each session** with `dev-start` for context
2. **End each session** with `dev-end` for continuity
3. **Create session notes** for complex projects
4. **Use sync commands** to maintain consistency
5. **Review status** regularly to track progress

## 📚 Example Workflows

### **Complete Feature Development**
```bash
# 1. Research Phase
python dev_assistant_cli.py architecture "React journal library"

# 2. Planning Phase
python dev_assistant_cli.py track "Create JournalLibrary component" --status pending

# 3. Implementation Phase
python dev_assistant_cli.py research "React file tree" --for-task "Create JournalLibrary component"
# (Implementation work here)

# 4. Testing Phase
python dev_assistant_cli.py track "Test JournalLibrary component" --status in_progress

# 5. Completion Phase
python dev_assistant_cli.py complete "Create JournalLibrary component" \
    --notes "Used react-tree-view, implemented file browser, PDF viewer integrated"

# 6. Documentation Phase
python openspec_sync.py --from-archon
```

### **Multi-Session Project**
```bash
# Session 1
dev-start
python dev_assistant_cli.py research "authentication patterns"
python dev_assistant_cli.py track "Implement auth system" --status pending
dev-end

# Session 2
dev-start
python dev_assistant_cli.py status  # Shows previous session context
python dev_assistant_cli.py track "Implement auth system" --status in_progress
# (Implementation work)
python dev_assistant_cli.py complete "Implement auth system" --notes "JWT tokens, bcrypt, secure sessions"
```

## 🎉 Getting Started Immediately

```bash
# 1. Initialize your development environment
cd your-project
source ./dev-workflow.sh

# 2. Start your first enhanced session
dev-start

# 3. Try the unified workflow
python dev_assistant_cli.py status

# 4. Create your first tracked task
python dev_assistant_cli.py track "Initialize project setup" --status pending

# 5. Research with automatic association
python dev_assistant_cli.py research "project setup best practices" --for-task "Initialize project setup"

# 6. Complete the task
python dev_assistant_cli.py complete "Initialize project setup" --notes "Project structure created, dependencies installed"

# 7. Check the results
python dev_assistant_cli.py status
```

---

**This unified system transforms development from a linear process into an intelligent, self-improving workflow that accumulates knowledge with every project and session.**

*Generated by Claude Code Assistant*
*Unified Archon + OpenSpec System* ✅