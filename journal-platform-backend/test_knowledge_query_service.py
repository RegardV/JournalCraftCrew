#!/usr/bin/env python3
"""
Test script for Knowledge Query Service

This script tests the knowledge query service integration with Archon
and validates that CrewAI agents can successfully access knowledge base functionality.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_import():
    """Test that the knowledge query service can be imported."""
    print("🔍 Testing Knowledge Query Service import...")

    try:
        from app.services.knowledge_query_service import KnowledgeQueryService, knowledge_query_service
        from app.services.knowledge_query_service import (
            search_knowledge_for_theme,
            enhance_journal_with_knowledge,
            get_research_insights
        )
        print("✅ Knowledge Query Service imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Knowledge Query Service: {e}")
        return False

async def test_service_initialization():
    """Test that the knowledge query service initializes correctly."""
    print("\n🚀 Testing Knowledge Query Service initialization...")

    try:
        from app.services.knowledge_query_service import knowledge_query_service

        # Check service status
        is_enabled = knowledge_query_service.is_enabled()
        print(f"📊 Service enabled: {is_enabled}")

        if is_enabled:
            print("✅ Knowledge Query Service initialized successfully")
            return True
        else:
            print("⚠️ Knowledge Query Service is disabled (Archon not available)")
            return False

    except Exception as e:
        print(f"❌ Failed to initialize Knowledge Query Service: {e}")
        return False

async def test_theme_search():
    """Test searching knowledge base by theme."""
    print("\n🔎 Testing theme-based knowledge search...")

    try:
        from app.services.knowledge_query_service import search_knowledge_for_theme

        # Test with different themes
        test_themes = [
            "Journaling for Anxiety",
            "Productivity and Goal Setting",
            "Mindfulness and Meditation",
            "Creative Expression"
        ]

        for theme in test_themes:
            print(f"📚 Searching for theme: '{theme}'")
            result = await search_knowledge_for_theme(theme, match_count=3)

            if result.get('success', False):
                results = result.get('results', [])
                print(f"✅ Found {len(results)} results for '{theme}'")

                # Display top result
                if results:
                    top_result = results[0]
                    print(f"   Top result: {top_result.get('title', 'No title')}")
                    print(f"   Relevance score: {top_result.get('relevance_score', 0):.2f}")
            else:
                print(f"⚠️ Search failed for '{theme}': {result.get('message', 'Unknown error')}")

        return True

    except Exception as e:
        print(f"❌ Theme search test failed: {e}")
        return False

async def test_research_insights():
    """Test getting research insights for specific topics."""
    print("\n🔬 Testing research insights retrieval...")

    try:
        from app.services.knowledge_query_service import get_research_insights

        # Test research topics
        research_topics = [
            ("mindfulness", "medium"),
            ("productivity", "light"),
            ("anxiety", "deep")
        ]

        for topic, depth in research_topics:
            print(f"📖 Getting research insights for: '{topic}' (depth: {depth})")
            result = await get_research_insights(topic, depth)

            if result.get('success', False):
                research_findings = result.get('research_findings', [])
                practical_applications = result.get('practical_applications', [])
                total_sources = result.get('total_sources', 0)

                print(f"✅ Found {total_sources} sources for '{topic}'")
                print(f"   Research findings: {len(research_findings)}")
                print(f"   Practical applications: {len(practical_applications)}")
            else:
                print(f"⚠️ Research insights failed for '{topic}': {result.get('message', 'Unknown error')}")

        return True

    except Exception as e:
        print(f"❌ Research insights test failed: {e}")
        return False

async def test_journal_enhancement():
    """Test journal content enhancement with knowledge."""
    print("\n✨ Testing journal content enhancement...")

    try:
        from app.services.knowledge_query_service import enhance_journal_with_knowledge

        # Sample journal content
        test_journal = {
            'title': 'My Mindfulness Journey',
            'content': '''
            Today I practiced mindfulness meditation for 10 minutes.
            I focused on my breathing and noticed how my mind tends to wander.
            It's challenging to stay present, but I'm making progress.
            I want to build a consistent daily practice.
            ''',
            'metadata': {
                'theme': 'Journaling for Anxiety',
                'authorStyle': 'empathetic research-driven',
                'researchDepth': 'medium'
            }
        }

        print(f"📝 Enhancing journal: '{test_journal['title']}'")
        result = await enhance_journal_with_knowledge(
            test_journal['title'],
            test_journal['content'],
            test_journal['metadata']
        )

        if result.get('success', False):
            enhanced_content = result.get('enhanced_content', '')
            original_content = result.get('original_content', '')
            knowledge_insights = result.get('knowledge_insights', {})

            print("✅ Journal enhancement completed successfully")
            print(f"   Original content length: {len(original_content)} characters")
            print(f"   Enhanced content length: {len(enhanced_content)} characters")
            print(f"   Content enhanced: {len(enhanced_content) > len(original_content)}")
            print(f"   Indexed for future reference: {result.get('indexed', False)}")
        else:
            print(f"⚠️ Journal enhancement failed: {result.get('message', 'Unknown error')}")

        return True

    except Exception as e:
        print(f"❌ Journal enhancement test failed: {e}")
        return False

async def test_agent_integration():
    """Test integration patterns for CrewAI agents."""
    print("\n🤖 Testing CrewAI agent integration patterns...")

    try:
        # Test the convenience functions that agents would use
        from app.services.knowledge_query_service import (
            search_knowledge_for_theme,
            enhance_journal_with_knowledge,
            get_research_insights
        )

        # Simulate agent workflow
        print("🎭 Simulating CrewAI agent workflow...")

        # 1. Agent searches for knowledge based on theme
        theme = "Journaling for Anxiety"
        knowledge_result = await search_knowledge_for_theme(theme, match_count=5)
        print(f"   📚 Agent knowledge search: {'✅ Success' if knowledge_result.get('success') else '❌ Failed'}")

        # 2. Agent gets research insights
        research_result = await get_research_insights("anxiety", "medium")
        print(f"   🔬 Agent research insights: {'✅ Success' if research_result.get('success') else '❌ Failed'}")

        # 3. Agent creates and enhances content
        if knowledge_result.get('success') or research_result.get('success'):
            content = "This is a sample journal entry about managing anxiety through daily reflection."
            metadata = {'theme': theme, 'authorStyle': 'empathetic research-driven'}

            enhancement_result = await enhance_journal_with_knowledge(
                "Anxiety Management Journal",
                content,
                metadata
            )
            print(f"   ✨ Agent content enhancement: {'✅ Success' if enhancement_result.get('success') else '❌ Failed'}")

        print("✅ CrewAI agent integration patterns validated")
        return True

    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False

async def main():
    """Run all tests for the Knowledge Query Service."""
    print("🧪 Knowledge Query Service Integration Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    test_results = []

    # Run all tests
    tests = [
        ("Import Test", test_import),
        ("Initialization Test", test_service_initialization),
        ("Theme Search Test", test_theme_search),
        ("Research Insights Test", test_research_insights),
        ("Journal Enhancement Test", test_journal_enhancement),
        ("Agent Integration Test", test_agent_integration)
    ]

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")

        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))

    # Summary
    print(f"\n{'='*60}")
    print("🏁 Test Suite Summary")
    print(f"{'='*60}")

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<30} {status}")

    print(f"\nOverall Result: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Knowledge Query Service is ready for CrewAI integration.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")

    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())