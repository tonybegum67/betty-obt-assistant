#!/usr/bin/env python3
"""
Quick test script to verify Betty works with synthetic TechCorp data
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from utils.vector_store import BettyVectorStore
        from utils.document_processor import DocumentProcessor
        print("✓ Utils imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_gps_data():
    """Test GPS data loading"""
    print("\nTesting GPS data...")
    try:
        import json
        with open('docs/GPS_2.0_Master.json', 'r') as f:
            data = json.load(f)

        assert data.get('total_clusters') == 13, "Expected 13 clusters"
        assert data.get('total_outcomes') == 558, "Expected 558 outcomes"
        assert data.get('version') == '2.0', "Expected version 2.0"

        # Check sanitization
        content = json.dumps(data)
        molex_count = content.lower().count('molex')
        techcorp_count = content.lower().count('techcorp')

        assert molex_count == 0, f"Found {molex_count} Molex references!"
        assert techcorp_count > 0, "No TechCorp references found!"

        print(f"✓ GPS data loaded: {data['total_outcomes']} outcomes, {data['total_clusters']} clusters")
        print(f"✓ Data sanitization verified: 0 Molex, {techcorp_count} TechCorp")
        return True
    except Exception as e:
        print(f"✗ GPS data test failed: {e}")
        return False

def test_pain_points():
    """Test pain points data"""
    print("\nTesting pain points data...")
    try:
        import json
        from pathlib import Path

        pain_points_found = 0
        for pain_file in Path('docs/TechCorp_Data').rglob('pain_points.json'):
            with open(pain_file, 'r') as f:
                data = json.load(f)
                pain_points_found += len(data)

        print(f"✓ Found {pain_points_found} pain points across capability areas")
        return True
    except Exception as e:
        print(f"✗ Pain points test failed: {e}")
        return False

def test_projects():
    """Test project data"""
    print("\nTesting project impacts data...")
    try:
        import json
        from pathlib import Path

        projects_found = 0
        for project_file in Path('docs/TechCorp_Data').rglob('project_impacts.json'):
            with open(project_file, 'r') as f:
                data = json.load(f)
                projects_found += len(data)

        print(f"✓ Found {projects_found} projects across capability areas")
        return True
    except Exception as e:
        print(f"✗ Project data test failed: {e}")
        return False

def test_vector_store():
    """Test vector store initialization"""
    print("\nTesting vector store initialization...")
    try:
        from utils.vector_store import BettyVectorStore

        # Just test initialization, don't load full DB
        vector_store = BettyVectorStore()
        print("✓ Vector store initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Vector store test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Betty OBT Assistant - Synthetic Data Validation")
    print("=" * 60)
    print()

    tests = [
        test_imports,
        test_gps_data,
        test_pain_points,
        test_projects,
        test_vector_store,
    ]

    results = []
    for test in tests:
        results.append(test())

    print()
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("✓ All tests passed! Betty is ready for the developer.")
        print()
        print("Next step: Run Betty with 'streamlit run betty_app.py'")
    else:
        print("⚠ Some tests failed. Please review errors above.")
        sys.exit(1)

    print("=" * 60)

if __name__ == '__main__':
    main()
