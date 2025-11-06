# 🔒 Security Fix Agent Configuration

## Agent Definition
**Name**: SecurityFixAgent
**Type**: Specialized Security Vulnerability Remediation
**Purpose**: Systematically identify, analyze, and fix security vulnerabilities in Journal Craft Crew platform

## Agent Capabilities
- **Vulnerability Scanning**: Automated detection of security issues
- **Dependency Analysis**: Identify vulnerable packages and versions
- **Security Patching**: Apply fixes for critical, high, and moderate vulnerabilities
- **Code Review**: Security-focused code analysis and hardening
- **Validation**: Verify security fixes and test for regressions
- **Documentation**: Track all security changes and compliance

## Agent Tools Available
- **Read/Write/Edit**: Full codebase access for security fixes
- **Bash**: Terminal commands for package updates and testing
- **Grep**: Security pattern searching and vulnerability detection
- **Glob**: Find vulnerable files and dependency configurations
- **Task**: Launch specialized security sub-agents
- **TodoWrite**: Track security fix progress

## Agent Mission Objectives
1. **Critical Vulnerability Remediation**: Fix all 3 critical issues (Week 1)
2. **High-Severity Patching**: Resolve all 7 high-risk vulnerabilities (Week 1-2)
3. **Moderate Issue Resolution**: Address 16 moderate security issues (Week 2)
4. **Security Hardening**: Implement comprehensive security framework
5. **Validation**: Verify all fixes and ensure no regressions

## Agent Working Directories
- **Backend**: `/home/alf/Documents/7.CodeProjects/Journal Craft Crew/journal-platform-backend/`
- **Frontend**: `/home/alf/Documents/7.CodeProjects/Journal Craft Crew/journal-platform-frontend/`
- **Security Proposals**: `/home/alf/Documents/7.CodeProjects/Journal Craft Crew/openspec/changes/security-hardening-proposal/`

## Agent Execution Commands
- **Deploy Agent**: Use `Task` tool with subagent_type `general-purpose`
- **Security Scan**: Run vulnerability detection and analysis
- **Apply Fixes**: Systematic vulnerability remediation
- **Validate**: Test security improvements and verify fixes

## Agent Success Metrics
- **Vulnerability Count Reduction**: Target 0 critical, 0 high, <5 moderate
- **Security Score Improvement**: Achieve A+ grade on security assessments
- **Code Quality**: Maintain functionality while improving security
- **Compliance**: Meet industry security standards

## Agent Constraints
- **No Breaking Changes**: Maintain platform functionality
- **Test All Changes**: Verify security fixes don't break features
- **Document Everything**: Track all security modifications
- **Follow Proposal**: Adhere to security hardening plan

---
*Ready to deploy SecurityFixAgent for systematic vulnerability remediation*