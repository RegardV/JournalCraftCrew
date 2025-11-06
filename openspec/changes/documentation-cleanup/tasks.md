# Documentation Cleanup Tasks

## 📋 Implementation Tasks

### Phase 1: Archive Setup
- [ ] Create archive directory: `openspec/archive/root-cleanup-2025-10-30/`
- [ ] List all files to be archived (21 proposal/summary files)
- [ ] Verify git status before moving files

### Phase 2: File Migration
- [ ] Move PROPOSAL files to archive:
  - [ ] AGENT_SYSTEM_IMPROVEMENT_PROPOSAL.md
  - [ ] ALIGNED_IMPLEMENTATION_STRATEGY.md
  - [ ] HYBRID_PLATFORM_PROPOSAL.md
  - [ ] IMAGE_INFERENCE_SYSTEM_PLAN.md
  - [ ] OPENSPEC_COMPLIANT_DOCUMENTATION_PROPOSAL.md
  - [ ] PHASE1_WEB_UI_IMPLEMENTATION_PLAN.md
- [ ] Move SUMMARY files to archive:
  - [ ] CRITICAL_REPRIORITIZATION_SUMMARY.md
  - [ ] DOCUMENTATION_PROPOSALS_SUMMARY.md
  - [ ] FRONTEND_RESCUE_SUCCESS_REPORT.md
  - [ ] IMPLEMENTATION_SUMMARY.md
  - [ ] PHASE1_COMPLETION_SUMMARY.md
  - [ ] PHASE2_COMPLETION_UPDATE.md
  - [ ] PROMPT_ANALYSIS_REPORT.md
  - [ ] PROPOSAL_REASSESSMENT_REPORT.md
- [ ] Move other files to archive:
  - [ ] FRAGMENTED_SYSTEM_ASSESSMENT.md
  - [ ] JOURNAL_PDF_FORMAT_ANALYSIS.md
  - [ ] PROPOSAL_REORGANIZATION_SUMMARY.md
  - [ ] PROPOSAL_UPDATE_PHASE1_COMPLETE.md
  - [ ] REPRIORIZED_PROPOSALS_PLAN.md
  - [ ] RESCUE_OPERATION_LOG.md
  - [ ] UPDATED_EXECUTION_PLAN.md
  - [ ] UPDATED_PRIORITY_PLAN.md

### Phase 3: OpenSpec Integration
- [ ] Move AGENTS.md to `openspec/agents/legacy-agents.md`
- [ ] Move changelog.md to `openspec/changelog.md`
- [ ] Move Scandoc.md to `openspec/archive/scandoc.md`

### Phase 4: Root File Updates
- [ ] Update README.md:
  - [ ] Fix brand name from "Journal Craft" to "Journal Craft Crew"
  - [ ] Update project description to current state
  - [ ] Add reference to OpenSpec documentation structure
  - [ ] Update installation and setup instructions
- [ ] Update CLAUDE.md:
  - [ ] Add reference to OpenSpec for project management
  - [ ] Update instructions to use OpenSpec workflow
- [ ] Review UI_DESIGN_STANDARDS.md (keep as-is)

### Phase 5: Verification
- [ ] Verify all files moved with git history preserved
- [ ] Check root directory has only 3 .md files
- [ ] Test internal links in remaining files
- [ ] Verify OpenSpec structure is intact
- [ ] Commit changes with descriptive message

## 🎯 Success Criteria
- [ ] Root directory reduced from 28 to 3 .md files
- [ ] All content preserved and accessible
- [ ] No broken internal links
- [ ] Git history maintained for all files
- [ ] Clean, professional project structure
- [ ] OpenSpec workflow clearly documented in CLAUDE.md

## ⚠️ Notes
- Use `git mv` to preserve file history
- Create backup before major changes
- Test documentation access after reorganization