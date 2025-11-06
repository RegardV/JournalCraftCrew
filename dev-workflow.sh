#!/bin/bash

# Development Workflow Helper - OpenSpec-Aligned Process
# Usage: source dev-workflow.sh

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 OpenSpec-Aligned Development Workflow${NC}"
echo -e "${YELLOW}Always start here when beginning development work${NC}\n"

# Function to show current status
dev-status() {
    echo -e "${GREEN}📊 Current Development Status:${NC}"

    # Check OpenSpec alignment
    if [ -f "OPENSPEC_ALIGNMENT_COMPLETE.md" ]; then
        echo -e "✅ OpenSpec Alignment: ${GREEN}Complete${NC}"
    else
        echo -e "⚠️  OpenSpec Alignment: ${YELLOW}Needs Review${NC}"
    fi

    # Check running services
    if pgrep -f "unified_backend.py" > /dev/null; then
        echo -e "✅ Backend Server: ${GREEN}Running${NC}"
    else
        echo -e "❌ Backend Server: ${RED}Stopped${NC}"
    fi

    if pgrep -f "npm.*dev" > /dev/null; then
        echo -e "✅ Frontend Server: ${GREEN}Running${NC}"
    else
        echo -e "❌ Frontend Server: ${RED}Stopped${NC}"
    fi

    # Check Archon development assistant
    if [ -f "journal-platform-backend/dev_assistant_cli.py" ]; then
        echo -e "✅ Archon Assistant: ${GREEN}Available${NC}"
    else
        echo -e "❌ Archon Assistant: ${RED}Missing${NC}"
    fi

    echo ""
}

# Function to start development session
dev-start() {
    echo -e "${GREEN}🎯 Starting Development Session${NC}\n"

    # Check for external changes and sync if needed
    echo -e "${YELLOW}🔄 Checking for external task changes...${NC}"
    if [ -f "archon_tasks.json" ] && [ -f "openspec/changes/current-proposal/tasks.md" ]; then
        # Get web task status to compare with local
        python3 -c "
import json
import subprocess

def get_web_task_status():
    try:
        cmd = ['curl', '-s', 'http://localhost:8181/api/tasks?page=1&per_page=10']
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            data = json.loads(result.stdout)
            tasks = data.get('tasks', [])
            web_done = sum(1 for task in tasks if task.get('status') == 'done')
            web_todo = sum(1 for task in tasks if task.get('status') == 'todo')
            return web_done, web_todo
    except:
        return 0, 0

web_done, web_todo = get_web_task_status()
local_done = sum(1 for task in json.load(open('archon_tasks.json')).get('tasks', {}).values() if task.get('status') == 'completed')
local_todo = sum(1 for task in json.load(open('archon_tasks.json')).get('tasks', {}).values() if task.get('status') == 'pending')

if web_done > local_done or web_todo < local_todo:
    print('   🌐 External changes detected in Web Archon')
    print('   🔁 Syncing from Web → Local → OpenSpec...')
    python3 enhanced_sync.py --from-web
    python3 openspec_sync.py --from-archon
    print('   ✅ External changes synced successfully')
else:
    print('   ✅ No external changes detected')
" > /tmp/sync_check.txt
        source /tmp/sync_check.txt
        rm -f /tmp/sync_check.txt
    else
        echo "   ⚠️  Task data not available for sync check"
    fi
    echo ""

    # Show current status
    dev-status

    # Show unified system context
    echo -e "${BLUE}🧠 Unified Archon + OpenSpec Context:${NC}"

    # Check for Archon task data
    if [ -f "archon_tasks.json" ]; then
        # Get total task counts (simple and reliable)
        TOTAL_TASKS=$(jq '.tasks | length' archon_tasks.json 2>/dev/null || echo "0")
        COMPLETED_TASKS=$(jq '[.tasks[] | select(.status == "completed")] | length' archon_tasks.json 2>/dev/null || echo "0")
        PENDING_TASKS=$(jq '[.tasks[] | select(.status == "pending")] | length' archon_tasks.json 2>/dev/null || echo "0")

        # Calculate overall progress percentage
        if [ "$TOTAL_TASKS" -gt 0 ] && [ "$COMPLETED_TASKS" -gt 0 ]; then
            PROGRESS_PERCENT=$(( COMPLETED_TASKS * 100 / TOTAL_TASKS ))
        else
            PROGRESS_PERCENT=0
        fi

        echo -e "   📊 Overall Project Progress: ${GREEN}$COMPLETED_TASKS/$TOTAL_TASKS completed${NC} (${PROGRESS_PERCENT}%)"
        echo -e "   🎯 Project Status: ${GREEN}$PROGRESS_PERCENT%${NC} complete"

        # Show last sync time
        LAST_SYNC=$(jq -r '.last_sync_from_openspec // "Never"' archon_tasks.json 2>/dev/null)
        if [ "$LAST_SYNC" != "Never" ]; then
            echo -e "   🔄 Last OpenSpec Sync: ${GREEN}$LAST_SYNC${NC}"
        fi

        # Show sample completed tasks
        COMPLETED_SAMPLES=$(jq -r '.tasks[] | select(.status == "completed") | .name' archon_tasks.json 2>/dev/null | head -5)
        if [ ! -z "$COMPLETED_SAMPLES" ]; then
            echo -e "   ✅ Recently Completed:"
            echo "$COMPLETED_SAMPLES" | sed 's/^/     • /'
        fi

        # Show sample priority pending tasks
        PRIORITY_SAMPLES=$(jq -r '.tasks[] | select(.status == "pending" and (.context | test("Immediate|Priority|Phase 1"; "i"))) | .name' archon_tasks.json 2>/dev/null | head -3)
        if [ ! -z "$PRIORITY_SAMPLES" ]; then
            echo -e "   🔥 Priority Tasks:"
            echo "$PRIORITY_SAMPLES" | sed 's/^/     • /'
        fi

        # Show meaningful progress interpretation
        if [ "$PROGRESS_PERCENT" -gt 70 ]; then
            echo -e "   🌟 Status: ${GREEN}Project is highly mature${NC} - focusing on advanced features"
        elif [ "$PROGRESS_PERCENT" -gt 40 ]; then
            echo -e "   🚀 Status: ${GREEN}Good progress${NC} - core infrastructure mostly complete"
        elif [ "$PROGRESS_PERCENT" -gt 20 ]; then
            echo -e "   ⚡ Status: ${YELLOW}Building momentum${NC} - foundational work in progress"
        else
            echo -e "   🏗️  Status: ${YELLOW}Early development${NC} - establishing core systems"
        fi
    else
        echo -e "   ⚠️  Archon task data not found - run: python openspec_sync.py --to-archon"
    fi

    # Check for knowledge patterns
    if [ -f "archon_knowledge.json" ]; then
        KNOWLEDGE_PATTERNS=$(jq '.knowledge.completed_patterns // [] | length' archon_knowledge.json 2>/dev/null || echo "0")
        if [ "$KNOWLEDGE_PATTERNS" -gt 0 ]; then
            echo -e "   📚 Available Knowledge Patterns: ${GREEN}$KNOWLEDGE_PATTERNS${NC}"
        fi
    fi

    echo ""

    # Check for session notes
    LATEST_SESSION=$(ls -1 SESSION_NOTE-*.md 2>/dev/null | tail -1)
    if [ ! -z "$LATEST_SESSION" ]; then
        echo -e "${BLUE}📝 Last Session Note:${NC}"
        echo -e "   📄 $LATEST_SESSION"
        # Show first 2 lines of latest session note
        head -2 "$LATEST_SESSION" | sed 's/^/   /'
        echo ""
    fi

    echo -e "${BLUE}📋 Enhanced Session Startup Checklist:${NC}"
    echo "1. Review Archon task progress and patterns"
    echo "2. Check OpenSpec sync status"
    echo "3. Continue from priority tasks or research new patterns"
    echo "4. Use unified workflow: OpenSpec plan → Archon research → Implement"
    echo "5. Track progress with knowledge accumulation"
    echo ""

    echo -e "${YELLOW}💡 Enhanced Quick Commands:${NC}"
    echo "dev-research    - Get Archon research guidance"
    echo "dev-plan        - Create OpenSpec proposal"
    echo "dev-archon     - Use Archon CLI tools"
    echo "dev-status      - Show current status"
    echo "dev-sync        - Sync OpenSpec ↔ Archon tasks"
    echo "dev-tasks       - Show Archon task overview"
    echo ""

    # Show intelligent suggestions based on current state
    if [ -f "archon_tasks.json" ]; then
        # Get simple task counts
        TOTAL_TASKS=$(jq '.tasks | length' archon_tasks.json 2>/dev/null || echo "0")
        COMPLETED_TASKS=$(jq '[.tasks[] | select(.status == "completed")] | length' archon_tasks.json 2>/dev/null || echo "0")

        # Calculate progress percentage
        if [ "$TOTAL_TASKS" -gt 0 ] && [ "$COMPLETED_TASKS" -gt 0 ]; then
            PROGRESS_PERCENT=$(( COMPLETED_TASKS * 100 / TOTAL_TASKS ))
        else
            PROGRESS_PERCENT=0
        fi

        if [ "$PROGRESS_PERCENT" -gt 70 ]; then
            echo -e "${GREEN}💡 AI Suggestion: Excellent progress! Project is highly mature (${PROGRESS_PERCENT}% complete)${NC}"
            echo "   • Core infrastructure and most features are solid"
            echo "   • Focus on advanced features and polish"
            echo "   • Consider: dev-plan \"advanced-features\" or testing end-to-end"
        elif [ "$PROGRESS_PERCENT" -gt 40 ]; then
            echo -e "${GREEN}💡 AI Suggestion: Good progress! Project is well-established (${PROGRESS_PERCENT}% complete)${NC}"
            echo "   • Core infrastructure is solid (auth, API, UI framework)"
            echo "   • Focus on journal functionality and CrewAI integration"
            echo "   • Research patterns: dev-research \"React file viewer\" or \"CrewAI integration\""
        elif [ "$PROGRESS_PERCENT" -gt 20 ]; then
            echo -e "${YELLOW}💡 AI Suggestion: Building momentum! (${PROGRESS_PERCENT}% complete)${NC}"
            echo "   • Foundational systems are taking shape"
            echo "   • Continue with core feature development"
            echo "   • Use: dev-tasks to see current priorities list"
        else
            echo -e "${YELLOW}💡 AI Suggestion: Early development phase (${PROGRESS_PERCENT}% complete)${NC}"
            echo "   • Focus on establishing core systems first"
            echo "   • Prioritize authentication and basic functionality"
            echo "   • Plan next features: dev-plan \"core-infrastructure\""
        fi
        echo ""
    fi
}

# Function to get Archon research
dev-research() {
    echo -e "${BLUE}🔍 Archon Research Assistant${NC}\n"

    if [ -z "$1" ]; then
        echo "Usage: dev-research \"your research topic\""
        echo ""
        echo "Examples:"
        echo "  dev-research \"file upload security patterns\""
        echo "  dev-research \"React form validation\""
        echo "  dev-research \"JWT token best practices\""
        echo ""
        echo "Available preset commands:"
        echo "  dev-storage     - File storage solutions research"
        echo "  dev-auth        - Authentication patterns research"
        echo "  dev-deployment  - Deployment strategies research"
        return
    fi

    echo -e "${GREEN}Researching: $1${NC}\n"

    cd journal-platform-backend
    source .venv/bin/activate

    # Use Archon MCP if available, fallback to development assistant
    if command -v archon &> /dev/null; then
        archon mcp search "$1"
    else
        echo "Using development assistant for research..."
        python dev_assistant_cli.py architecture "$1"
    fi

    cd ..
}

# Function for quick research commands
dev-storage() {
    dev-research "file storage solutions Google Drive Dropbox AWS S3 VPS integration"
}

dev-auth() {
    dev-research "authentication patterns Firebase OAuth JWT React FastAPI security"
}

dev-deployment() {
    dev-research "VPS deployment strategies Docker security monitoring backup"
}

# Function to plan with OpenSpec
dev-plan() {
    echo -e "${BLUE}📋 OpenSpec Planning${NC}\n"

    if [ -z "$1" ]; then
        echo "Usage: dev-plan \"feature-name\""
        echo ""
        echo "Examples:"
        echo "  dev-plan \"user authentication system\""
        echo "  dev-plan \"file upload functionality\""
        echo "  dev-plan \"journal export features\""
        return
    fi

    echo -e "${GREEN}Planning feature: $1${NC}\n"

    echo "1. Create OpenSpec proposal:"
    echo "   openspec proposal create \"$1\""
    echo ""
    echo "2. Research implementation patterns:"
    echo "   dev-research \"$1 best practices\""
    echo ""
    echo "3. Create research-backed tasks:"
    echo "   openspec task breakdown --archon-informed"
    echo ""
    echo "4. Implement with discovered patterns"
    echo "5. Document findings:"
    echo "   openspec change apply --with-archon-research"
}

# Function to sync OpenSpec and Archon
dev-sync() {
    echo -e "${BLUE}🔄 OpenSpec ↔ Archon Sync${NC}\n"

    cd journal-platform-backend
    source .venv/bin/activate

    echo -e "${GREEN}Sync Options:${NC}"
    echo "1. Push OpenSpec tasks to Archon"
    echo "2. Pull Archon progress to OpenSpec"
    echo "3. Bidirectional sync"
    echo "4. Show sync status"
    echo ""

    if [ -z "$1" ]; then
        echo "Usage: dev-sync [to-archon|from-archon|sync-all|status]"
        echo ""
        echo "Examples:"
        echo "  dev-sync to-archon    - Push OpenSpec tasks to Archon"
        echo "  dev-sync from-archon  - Pull Archon progress to OpenSpec"
        echo "  dev-sync sync-all     - Bidirectional sync"
        echo "  dev-sync status       - Show sync status"
        return
    fi

    case "$1" in
        "to-archon")
            echo -e "${YELLOW}Pushing OpenSpec tasks to Archon...${NC}"
            python ../openspec_sync.py --to-archon
            ;;
        "from-archon")
            echo -e "${YELLOW}Pulling Archon progress to OpenSpec...${NC}"
            python ../openspec_sync.py --from-archon
            ;;
        "sync-all")
            echo -e "${YELLOW}Performing bidirectional sync...${NC}"
            python ../openspec_sync.py --sync-all
            ;;
        "status")
            echo -e "${YELLOW}Showing sync status...${NC}"
            python ../openspec_sync.py --status
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use: dev-sync [to-archon|from-archon|sync-all|status]"
            ;;
    esac

    cd ..
}

# Function to show Archon tasks overview
dev-tasks() {
    echo -e "${BLUE}📋 Archon Task Overview${NC}\n"

    if [ ! -f "archon_tasks.json" ]; then
        echo -e "${RED}❌ No Archon task data found.${NC}"
        echo -e "${YELLOW}💡 Run: dev-sync to-archon to sync OpenSpec tasks${NC}"
        return
    fi

    # Task counts
    TOTAL_TASKS=$(jq '.tasks | length' archon_tasks.json 2>/dev/null || echo "0")
    COMPLETED_TASKS=$(jq '.tasks | map(select(.status == "completed")) | length' archon_tasks.json 2>/dev/null || echo "0")
    PENDING_TASKS=$(jq '.tasks | map(select(.status == "pending")) | length' archon_tasks.json 2>/dev/null || echo "0")
    IN_PROGRESS_TASKS=$(jq '.tasks | map(select(.status == "in_progress")) | length' archon_tasks.json 2>/dev/null || echo "0")

    echo -e "${GREEN}📊 Task Statistics:${NC}"
    echo "   Total Tasks: $TOTAL_TASKS"
    echo "   ✅ Completed: $COMPLETED_TASKS"
    echo "   🔄 In Progress: $IN_PROGRESS_TASKS"
    echo "   ⏳ Pending: $PENDING_TASKS"
    echo ""

    # Show priority tasks
    PRIORITY_TASKS=$(jq -r '.tasks | to_entries[] | select(.value.status == "pending" and (.value.context | contains("Immediate") or .value.context | contains("Priority"))) | "• \(.value.name) (\(.value.context))"' archon_tasks.json 2>/dev/null)
    if [ ! -z "$PRIORITY_TASKS" ]; then
        echo -e "${YELLOW}🔥 Priority Tasks:${NC}"
        echo "$PRIORITY_TASKS"
        echo ""
    fi

    # Show recent activity
    echo -e "${BLUE}🕒 Recent Activity:${NC}"
    LAST_SYNC=$(jq -r '.last_sync_from_openspec // "Never"' archon_tasks.json 2>/dev/null)
    echo "   Last OpenSpec Sync: $LAST_SYNC"

    LAST_UPDATED=$(jq -r '.last_updated // "Unknown"' archon_tasks.json 2>/dev/null)
    echo "   Last Updated: $LAST_UPDATED"
    echo ""

    # Show available commands
    echo -e "${GREEN}💡 Task Management Commands:${NC}"
    echo "   cd journal-platform-backend && python dev_assistant_cli.py status"
    echo "   cd journal-platform-backend && python dev_assistant_cli.py track \"task name\" --status in_progress"
    echo "   cd journal-platform-backend && python dev_assistant_cli.py complete \"task name\" --notes \"implementation notes\""
}

# Function to access Archon CLI tools
dev-archon() {
    echo -e "${BLUE}🛠️  Archon Development Tools${NC}\n"

    cd journal-platform-backend
    source .venv/bin/activate

    if [ -z "$1" ]; then
        echo "Available Archon CLI commands:"
        echo ""
        echo "  dev-archon storage      - Research file storage solutions"
        echo "  dev-archon auth         - Research authentication patterns"
        echo "  dev-archon deployment   - Research deployment strategies"
        echo "  dev-archon architecture \"topic\" - Get architecture guidance"
        echo "  dev-archon patterns \"tech\" \"use-case\" - Research implementation patterns"
        echo ""
        echo "Task Management:"
        echo "  dev-archon status                      - Show project status"
        echo "  dev-archon track \"task\" --status X    - Track task progress"
        echo "  dev-archon complete \"task\" --notes X  - Complete task with notes"
        echo "  dev-archon research \"topic\"           - Research with tracking"
        echo ""
        echo "Examples:"
        echo "  dev-archon architecture \"React state management\""
        echo "  dev-archon patterns \"FastAPI\" \"JWT authentication\""
        echo "  dev-archon track \"Fix dashboard JSX errors\" --status in_progress"
        return
    fi

    python dev_assistant_cli.py "$@"

    cd ..
}

# Function to sync local tasks to web Archon
dev-web-sync() {
    echo -e "${BLUE}🌐 Sync Local Tasks to Web Archon${NC}\n"

    echo -e "${GREEN}Syncing local Archon tasks to web interface...${NC}"
    python3 enhanced_sync.py --to-web

    echo -e "${BLUE}💡 Web Interface:${NC}"
    echo "   📱 Access your tasks at: http://localhost:3737/"
    echo "   📚 API documentation: http://localhost:8181/docs"
    echo ""
}

# Function to fix status mapping
dev-web-fix() {
    echo -e "${BLUE}🔧 Fix Status Mapping (Web ↔ Local)${NC}\n"

    echo -e "${GREEN}Correcting task status mapping between web and local systems...${NC}"
    python3 fix_status_mapping.py

    echo ""
    echo -e "${YELLOW}💡 This ensures:${NC}"
    echo "   ✅ Completed local tasks appear as 'done' in web UI"
    echo "   ✅ Pending local tasks appear as 'todo' in web UI"
    echo "   ✅ Accurate progress tracking across all systems"
    echo ""
}

# Function to show web Archon status
dev-web-status() {
    echo -e "${BLUE}📊 Web Archon Status${NC}\n"

    # Get web task counts (using pagination to get all tasks)
    python3 -c "
import json
import subprocess

def get_all_tasks():
    all_tasks = []
    page = 1
    per_page = 100

    while True:
        cmd = ['curl', '-s', f'http://localhost:8181/api/tasks?page={page}&per_page={per_page}']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if not result.stdout:
            break

        try:
            data = json.loads(result.stdout)
            tasks = data.get('tasks', [])
            if not tasks:
                break
            all_tasks.extend(tasks)

            pagination = data.get('pagination', {})
            total = pagination.get('total', 0)
            if len(all_tasks) >= total:
                break
            page += 1
        except:
            break

    return all_tasks

tasks = get_all_tasks()
status_counts = {}
for task in tasks:
    status = task.get('status', 'todo')
    status_counts[status] = status_counts.get(status, 0) + 1

print(f'WEB_TODO={status_counts.get(\"todo\", 0)}')
print(f'WEB_DONE={status_counts.get(\"done\", 0)}')
print(f'WEB_TOTAL={len(tasks)}')
" > /tmp/web_status.txt

    source /tmp/web_status.txt

    # Get local task counts
    LOCAL_TODO=$(jq '[.tasks[] | select(.status == "pending")] | length' archon_tasks.json 2>/dev/null || echo "0")
    LOCAL_DONE=$(jq '[.tasks[] | select(.status == "completed")] | length' archon_tasks.json 2>/dev/null || echo "0")
    LOCAL_TOTAL=$(jq '.tasks | length' archon_tasks.json 2>/dev/null || echo "0")

    echo -e "${GREEN}🌐 Web Archon Status:${NC}"
    echo "   📋 Total tasks: $WEB_TOTAL"
    echo "   ✅ Completed: $WEB_DONE"
    echo "   📝 Pending: $WEB_TODO"

    echo -e "${GREEN}📁 Local Archon Status:${NC}"
    echo "   📋 Total tasks: $LOCAL_TOTAL"
    echo "   ✅ Completed: $LOCAL_DONE"
    echo "   📝 Pending: $LOCAL_TODO"

    # Show sync coverage
    if [ "$WEB_TOTAL" != "unknown" ] && [ "$WEB_TOTAL" -gt 0 ]; then
        SYNC_COVERAGE=$(( LOCAL_DONE == WEB_DONE && LOCAL_TODO == WEB_TODO ))
        if [ "$SYNC_COVERAGE" -eq 1 ]; then
            echo -e "${GREEN}✅ Status Mapping: ${GREEN}Perfect sync!${NC}"
        else
            echo -e "${YELLOW}⚠️  Status Mapping: ${YELLOW}Needs attention${NC}"
            echo "   💡 Run: dev-web-fix to correct status mapping"
        fi
    fi

    echo ""
    echo -e "${BLUE}🔗 Access Points:${NC}"
    echo "   🖥️  Web Interface: http://localhost:3737/"
    echo "   📚 API Docs: http://localhost:8181/docs"
    echo ""
}

# Function to end session
dev-end() {
    echo -e "${GREEN}🏁 Ending Development Session${NC}\n"

    echo -e "${BLUE}📋 Session Completion Checklist:${NC}"
    echo "☐ Mark tasks as completed with research notes"
    echo "☐ Apply OpenSpec changes with documentation"
    echo "☐ Sync tasks to web Archon (dev-web-sync)"
    echo "☐ Record session progress"
    echo "☐ Plan next session research items"
    echo ""

    echo -e "${YELLOW}💡 Leave a note for your future self:${NC}"
    echo "Create a file named 'SESSION_NOTE-[date].md' with:"
    echo "- What you accomplished"
    echo "- Research findings used"
    echo "- Next session priorities"
    echo "- OpenSpec tasks to continue"
    echo ""
}

# Display welcome message
echo -e "${GREEN}✅ Unified Archon + OpenSpec Development Workflow Loaded!${NC}"
echo -e "${YELLOW}Available commands:${NC}"
echo "  dev-start       - Start development session with AI context"
echo "  dev-status     - Show current status"
echo "  dev-research    - Get Archon research guidance"
echo "  dev-plan        - Plan feature with OpenSpec"
echo "  dev-storage     - Quick file storage research"
echo "  dev-auth        - Quick authentication research"
echo "  dev-deployment  - Quick deployment research"
echo "  dev-archon      - Access Archon CLI tools"
echo "  dev-sync        - Sync OpenSpec ↔ Archon tasks"
echo "  dev-web-sync    - Sync local tasks to web Archon"
echo "  dev-web-fix     - Fix status mapping web ↔ local"
echo "  dev-web-status  - Show web Archon status"
echo "  dev-tasks       - Show Archon task overview"
echo "  dev-end         - End development session"
echo ""
echo -e "${BLUE}Unified Workflow: ${NC}OpenSpec plan → Archon research → Implement → Track"
echo -e "${GREEN}Start with: ${NC}dev-start"