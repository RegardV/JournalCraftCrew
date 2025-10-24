#!/usr/bin/env python3
"""
Prompt Analyzer for Journal Craft Crew
Extracts and analyzes all agent prompts for duplicity and effectiveness
"""

import os
import re
import json
from datetime import datetime

def extract_prompts_from_file(file_path):
    """Extract prompts and descriptions from agent files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find agent role, goal, and backstory
        role_match = re.search(r'role\s*=\s*["\']([^"\']+)["\']', content)
        goal_match = re.search(r'goal\s*=\s*["\']([^"\']+)["\']', content)
        backstory_match = re.search(r'backstory\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)

        # Find function prompts
        function_prompts = []
        prompt_pattern = r'(?:prompt|research_prompt|curation_prompt)\s*=\s*["\']([^"\']+)["\']'
        for match in re.finditer(prompt_pattern, content, re.DOTALL):
            function_prompts.append(match.group(1))

        # Find task descriptions
        task_patterns = [
            r'("""[^"]*""")',  # Triple quotes
            r"('''[^']*''')",   # Triple single quotes
            r'prompt["\']?\s*=\s*["\']([^"\']{50,})["\']',  # Long prompts
        ]

        long_prompts = []
        for pattern in task_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                prompt_text = match.group(1) if match.groups() else match.group(0)
                if len(prompt_text.strip()) > 30:  # Only keep substantial prompts
                    long_prompts.append(prompt_text.strip('\'"'))

        return {
            'role': role_match.group(1) if role_match else None,
            'goal': goal_match.group(1) if goal_match else None,
            'backstory': backstory_match.group(1) if backstory_match else None,
            'function_prompts': function_prompts,
            'long_prompts': long_prompts
        }

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def analyze_prompt_effectiveness(prompt_text, agent_role):
    """Analyze prompt effectiveness based on purpose"""
    if not prompt_text or len(prompt_text) < 20:
        return {'score': 0, 'issues': ['Too short or empty']}

    issues = []
    strengths = []
    score = 50  # Base score

    # Check for clarity
    if '?' in prompt_text and 'Generate' in prompt_text:
        score += 10
        strengths.append('Clear action verb with question')

    # Check for specificity
    specific_keywords = ['generate', 'create', 'write', 'analyze', 'research', 'curate', 'edit']
    if any(keyword in prompt_text.lower() for keyword in specific_keywords):
        score += 15
        strengths.append('Contains specific action verbs')

    # Check for output format specification
    output_formats = ['json', 'list', 'dictionary', 'markdown', 'structured']
    if any(fmt in prompt_text.lower() for fmt in output_formats):
        score += 20
        strengths.append('Specifies output format')

    # Check for length constraints
    if 'word' in prompt_text.lower() or 'character' in prompt_text.lower():
        score += 10
        strengths.append('Specifies length requirements')

    # Check for style guidance
    style_keywords = ['style', 'tone', 'voice', 'empathetic', 'professional', 'conversational']
    if any(keyword in prompt_text.lower() for keyword in style_keywords):
        score += 15
        strengths.append('Includes style guidance')

    # Check for context
    context_keywords = ['based on', 'using', 'given', 'theme', 'preferences']
    if any(keyword in prompt_text.lower() for keyword in context_keywords):
        score += 10
        strengths.append('Provides context')

    # Check for vagueness
    vague_phrases = ['make something', 'do something', 'create content', 'write stuff']
    if any(phrase in prompt_text.lower() for phrase in vague_phrases):
        score -= 20
        issues.append('Contains vague instructions')

    # Check for ambiguity
    if prompt_text.count('.') > 10 and len(prompt_text) < 200:
        score -= 10
        issues.append('Too many short sentences, may be confusing')

    # Check for missing constraints
    if 'length' not in prompt_text.lower() and 'word' not in prompt_text.lower():
        if agent_role.lower() not in ['manager', 'media']:
            issues.append('Missing length constraints')

    score = max(0, min(100, score))

    return {
        'score': score,
        'strengths': strengths,
        'issues': issues,
        'length': len(prompt_text),
        'word_count': len(prompt_text.split())
    }

def find_duplicate_phrases(prompts_data):
    """Find duplicate phrases across different agent prompts"""
    all_texts = []

    for agent_name, agent_data in prompts_data.items():
        if not agent_data:
            continue

        # Combine all prompt texts from this agent
        text_parts = [
            agent_data.get('role', '') or '',
            agent_data.get('goal', '') or '',
            agent_data.get('backstory', '') or '',
            ' '.join(agent_data.get('function_prompts', []) or []),
            ' '.join(agent_data.get('long_prompts', []) or [])
        ]
        combined_text = ' '.join([part for part in text_parts if part]).lower()

        all_texts.append((agent_name, combined_text))

    # Find common phrases
    duplicate_analysis = {}
    common_words = set()

    # Extract common single words
    word_counts = {}
    for agent_name, text in all_texts:
        words = text.split()
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 chars
                if word not in word_counts:
                    word_counts[word] = []
                word_counts[word].append(agent_name)

    # Find words used by 3+ agents
    for word, agents in word_counts.items():
        if len(agents) >= 3:
            common_words.append((word, agents))

    # Find common phrases
    phrase_analysis = {}
    for agent_name, text in all_texts:
        # Extract common phrases
        common_phrases = [
            'journaling guide',
            'content creation',
            'themed journaling',
            'user preferences',
            'data flow',
            'ensure variety',
            'structured content',
            'professional presentation'
        ]

        for phrase in common_phrases:
            if phrase in text:
                if phrase not in phrase_analysis:
                    phrase_analysis[phrase] = []
                phrase_analysis[phrase].append(agent_name)

    return {
        'common_words': common_words,
        'common_phrases': phrase_analysis
    }

def analyze_all_prompts():
    """Main analysis function"""
    print("🔍 PROMPT ANALYSIS FOR JOURNAL CRAFT CREW")
    print("=" * 60)
    print("Extracting and analyzing all agent prompts...")
    print()

    # Find all agent files
    agent_files = {
        'Manager Agent': 'agents/manager_agent.py',
        'Onboarding Agent': 'agents/onboarding_agent.py',
        'Discovery Agent': 'agents/discovery_agent.py',
        'Research Agent': 'agents/research_agent.py',
        'Content Curator Agent': 'agents/content_curator_agent.py',
        'Editor Agent': 'agents/editor_agent.py',
        'Media Agent': 'agents/media_agent.py',
        'PDF Builder Agent': 'agents/pdf_builder_agent.py'
    }

    prompts_data = {}

    # Extract prompts from each agent
    for agent_name, file_path in agent_files.items():
        print(f"📖 Analyzing {agent_name}...")
        if os.path.exists(file_path):
            prompts_data[agent_name] = extract_prompts_from_file(file_path)
        else:
            print(f"  ⚠️  File not found: {file_path}")
            prompts_data[agent_name] = None

    print("\n🤖 AGENT PROMPT ANALYSIS:")
    print("-" * 50)

    for agent_name, data in prompts_data.items():
        if not data:
            continue

        print(f"\n📍 {agent_name}:")

        if data['role']:
            print(f"  🎭 Role: {data['role']}")
            effectiveness = analyze_prompt_effectiveness(data['role'], agent_name)
            print(f"  📊 Role Effectiveness: {effectiveness['score']}/100")
            if effectiveness.get('strengths'):
                print(f"    ✓ Strengths: {', '.join(effectiveness['strengths'])}")
            if effectiveness.get('issues'):
                print(f"    ⚠️  Issues: {', '.join(effectiveness['issues'])}")

        if data['goal']:
            print(f"  🎯 Goal: {data['goal']}")
            effectiveness = analyze_prompt_effectiveness(data['goal'], agent_name)
            print(f"  📊 Goal Effectiveness: {effectiveness['score']}/100")

        if data['backstory']:
            print(f"  📖 Backstory: {data['backstory'][:100]}...")

        if data['function_prompts']:
            print(f"  🔧 Function Prompts ({len(data['function_prompts'])}):")
            for i, prompt in enumerate(data['function_prompts'], 1):
                effectiveness = analyze_prompt_effectiveness(prompt, agent_name)
                print(f"    {i}. [Score: {effectiveness['score']}/100] {prompt[:80]}...")
                if effectiveness.get('issues'):
                    print(f"       Issues: {', '.join(effectiveness['issues'])}")

        if data['long_prompts']:
            print(f"  📝 Long Prompts ({len(data['long_prompts'])}):")
            for i, prompt in enumerate(data['long_prompts'], 1):
                effectiveness = analyze_prompt_effectiveness(prompt, agent_name)
                print(f"    {i}. [Score: {effectiveness['score']}/100, Length: {effectiveness['word_count']} words]")
                if effectiveness.get('strengths'):
                    print(f"       ✓ Strengths: {', '.join(effectiveness['strengths'][:2])}")
                if effectiveness.get('issues'):
                    print(f"       ⚠️  Issues: {', '.join(effectiveness['issues'][:2])}")

    # Analyze duplicity
    print("\n🔄 DUPLICITY ANALYSIS:")
    print("-" * 50)

    duplicate_analysis = find_duplicate_phrases(prompts_data)

    print("\n📝 Common Phrases Across Agents:")
    for phrase, agents in duplicate_analysis['common_phrases'].items():
        if len(agents) > 1:
            print(f"  \"{phrase}\" used by: {', '.join(agents)}")

    print("\n🔤 Common Words Across Agents:")
    common_words = sorted(duplicate_analysis['common_words'], key=lambda x: len(x[1]), reverse=True)
    for word, agents in common_words[:10]:  # Top 10 most common
        if len(agents) > 2:
            print(f"  \"{word}\" used by {len(agents)} agents")

    # Overall effectiveness analysis
    print("\n📊 OVERALL EFFECTIVENESS ANALYSIS:")
    print("-" * 50)

    total_scores = []
    all_issues = []
    all_strengths = []

    for agent_name, data in prompts_data.items():
        if not data:
            continue

        for prompt_type in ['role', 'goal', 'backstory']:
            if data[prompt_type]:
                analysis = analyze_prompt_effectiveness(data[prompt_type], agent_name)
                total_scores.append(analysis['score'])
                all_issues.extend(analysis['issues'])
                all_strengths.extend(analysis['strengths'])

        for prompt in data['function_prompts'] + data['long_prompts']:
            analysis = analyze_prompt_effectiveness(prompt, agent_name)
            total_scores.append(analysis['score'])
            all_issues.extend(analysis['issues'])
            all_strengths.extend(analysis['strengths'])

    if total_scores:
        avg_score = sum(total_scores) / len(total_scores)
        print(f"  📈 Average Prompt Effectiveness: {avg_score:.1f}/100")

        # Count common issues
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        print("\n  ⚠️  Most Common Issues:")
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        for issue, count in sorted_issues[:5]:
            print(f"    {count}x: {issue}")

        # Count common strengths
        strength_counts = {}
        for strength in all_strengths:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1

        print("\n  ✅ Most Common Strengths:")
        sorted_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)
        for strength, count in sorted_strengths[:5]:
            print(f"    {count}x: {strength}")

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print("-" * 50)

    recommendations = [
        "1. Standardize output format specifications across all agents",
        "2. Add specific length constraints to content generation prompts",
        "3. Reduce duplicate phrases between agents for clearer differentiation",
        "4. Include more specific style guidance in editing prompts",
        "5. Add error handling instructions to all LLM calls",
        "6. Ensure consistency in terminology across agent descriptions",
        "7. Add validation requirements to structured output prompts",
        "8. Include examples of expected output format in complex prompts"
    ]

    for rec in recommendations:
        print(f"  {rec}")

    return {
        'agents_analyzed': len([a for a in prompts_data.values() if a]),
        'total_prompts': len(total_scores),
        'average_effectiveness': avg_score if total_scores else 0,
        'common_issues': dict(sorted_issues[:3]) if sorted_issues else {},
        'common_strengths': dict(sorted_strengths[:3]) if sorted_strengths else {},
        'duplicate_phrases': len(duplicate_analysis['common_phrases']),
        'recommendations': recommendations
    }

if __name__ == "__main__":
    result = analyze_all_prompts()

    print(f"\n📋 ANALYSIS SUMMARY:")
    print(json.dumps(result, indent=2))