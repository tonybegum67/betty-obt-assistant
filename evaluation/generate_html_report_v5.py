#!/usr/bin/env python3
"""
Generate HTML report from v5.0 evaluation CSV results
"""

import csv
import json
from datetime import datetime
from pathlib import Path

def generate_html_report(csv_path: str, output_path: str):
    """Generate comprehensive HTML report from v5.0 CSV results"""

    # Read CSV results
    results = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append(row)

    # Calculate summary statistics
    total = len(results)
    errors = sum(1 for r in results if r['error'])

    avg_overall = sum(float(r['overall_score']) for r in results) / total
    avg_semantic = sum(float(r['semantic_correctness']) for r in results) / total
    avg_obt = sum(float(r['obt_adherence']) for r in results) / total
    avg_complete = sum(float(r['response_completeness']) for r in results) / total
    avg_comm = sum(float(r['professional_communication']) for r in results) / total
    avg_time = sum(int(r['execution_time_ms']) for r in results) / total
    avg_words = sum(int(r['word_count']) for r in results) / total

    # Rating distribution
    rating_counts = {'EXCELLENT': 0, 'GOOD': 0, 'ACCEPTABLE': 0, 'NEEDS_IMPROVEMENT': 0, 'POOR': 0}
    for r in results:
        rating = r['rating']
        if rating in rating_counts:
            rating_counts[rating] += 1

    # Generate HTML
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Betty v5.0 Evaluation Report - {timestamp}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 5px 0;
            font-size: 1.1em;
            opacity: 0.95;
        }}
        .summary {{
            background-color: #f9f9f9;
            padding: 25px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 5px solid #667eea;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        .test-case {{
            border: 2px solid #ddd;
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            background: white;
        }}
        .excellent {{ border-left: 5px solid #28a745; background-color: #f1f9f3; }}
        .good {{ border-left: 5px solid #17a2b8; background-color: #f1f9fc; }}
        .acceptable {{ border-left: 5px solid #ffc107; background-color: #fffbf1; }}
        .needs-improvement {{ border-left: 5px solid #fd7e14; background-color: #fff5f1; }}
        .poor {{ border-left: 5px solid #dc3545; background-color: #fff1f1; }}

        .scores {{
            display: flex;
            gap: 15px;
            margin: 15px 0;
            flex-wrap: wrap;
        }}
        .score-box {{
            padding: 12px 16px;
            border-radius: 6px;
            text-align: center;
            min-width: 100px;
            background-color: #f0f0f0;
            border: 1px solid #ddd;
        }}
        .score-box strong {{
            display: block;
            font-size: 0.85em;
            color: #666;
            margin-bottom: 5px;
        }}
        .score-value {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}

        .rating-chart {{
            margin: 20px 0;
        }}
        .rating-bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .rating-label {{
            min-width: 180px;
            font-weight: 500;
        }}
        .rating-fill {{
            height: 30px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            display: flex;
            align-items: center;
            padding: 0 10px;
            color: white;
            font-weight: bold;
        }}

        .breakdown {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}

        .checks {{
            margin: 10px 0;
        }}
        .check-item {{
            padding: 5px 0;
            font-size: 0.95em;
        }}
        .check-passed {{
            color: #28a745;
        }}
        .check-failed {{
            color: #dc3545;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}

        .comparison {{
            background: linear-gradient(135deg, #f6f9fc 0%, #e9f2f9 100%);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}

        .improvement {{
            color: #28a745;
            font-weight: bold;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge-excellent {{ background-color: #28a745; color: white; }}
        .badge-good {{ background-color: #17a2b8; color: white; }}
        .badge-acceptable {{ background-color: #ffc107; color: #333; }}
        .badge-needs {{ background-color: #fd7e14; color: white; }}
        .badge-poor {{ background-color: #dc3545; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Betty v5.0 Evaluation Report</h1>
            <p>Real-World Usability Focus | Generated: {timestamp}</p>
            <p>Test Cases: {total} | Success Rate: {((total-errors)/total*100):.1f}%</p>
        </div>

        <div class="summary">
            <h2>📊 Executive Summary</h2>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{avg_overall:.3f}</div>
                    <div class="metric-label">Overall Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_semantic:.3f}</div>
                    <div class="metric-label">Semantic Correctness</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_obt:.3f}</div>
                    <div class="metric-label">OBT Adherence</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_complete:.3f}</div>
                    <div class="metric-label">Response Completeness</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_comm:.3f}</div>
                    <div class="metric-label">Professional Communication</div>
                </div>
            </div>

            <div class="comparison">
                <h3>🎯 Performance vs v4.3 Baseline</h3>
                <p style="font-size: 1.2em;">
                    <strong>v4.3 Baseline:</strong> 0.307 (POOR - 70% failed)<br>
                    <strong>v5.0 Score:</strong> {avg_overall:.3f}
                    <span class="improvement">+{((avg_overall - 0.307) / 0.307 * 100):.1f}% improvement</span>
                </p>
                <p>
                    <strong>Key Changes:</strong> Reasoning and sources now ADD value •
                    Realistic length expectations • Transparent scoring •
                    Human-centered evaluation
                </p>
            </div>

            <h3>📈 Rating Distribution</h3>
            <div class="rating-chart">
"""

    # Add rating bars
    for rating, count in rating_counts.items():
        pct = (count / total) * 100
        width_pct = max(pct, 5)  # Minimum 5% width for visibility

        badge_class = {
            'EXCELLENT': 'badge-excellent',
            'GOOD': 'badge-good',
            'ACCEPTABLE': 'badge-acceptable',
            'NEEDS_IMPROVEMENT': 'badge-needs',
            'POOR': 'badge-poor'
        }.get(rating, '')

        html += f"""
                <div class="rating-bar">
                    <div class="rating-label">
                        <span class="badge {badge_class}">{rating}</span>
                    </div>
                    <div class="rating-fill" style="width: {width_pct}%;">
                        {count} ({pct:.1f}%)
                    </div>
                </div>
"""

    html += f"""
            </div>

            <h3>⏱️ Performance Metrics</h3>
            <p>
                <strong>Avg Response Time:</strong> {avg_time:.0f}ms<br>
                <strong>Avg Word Count:</strong> {avg_words:.1f} words<br>
                <strong>Errors:</strong> {errors} ({(errors/total*100):.1f}%)
            </p>
        </div>

        <h2>🔍 Detailed Test Case Results</h2>
"""

    # Add individual test cases
    for i, result in enumerate(results, 1):
        rating = result['rating']
        rating_class = {
            'EXCELLENT': 'excellent',
            'GOOD': 'good',
            'ACCEPTABLE': 'acceptable',
            'NEEDS_IMPROVEMENT': 'needs-improvement',
            'POOR': 'poor',
            'ERROR': 'poor'
        }.get(rating, 'acceptable')

        badge_class = {
            'EXCELLENT': 'badge-excellent',
            'GOOD': 'badge-good',
            'ACCEPTABLE': 'badge-acceptable',
            'NEEDS_IMPROVEMENT': 'badge-needs',
            'POOR': 'badge-poor'
        }.get(rating, '')

        # Parse passed/failed checks
        try:
            passed_checks = json.loads(result['passed_checks'])
            failed_checks = json.loads(result['failed_checks'])
        except:
            passed_checks = {'obt': [], 'communication': []}
            failed_checks = {'obt': [], 'communication': []}

        html += f"""
        <div class="test-case {rating_class}">
            <h3>Test Case #{i} <span class="badge {badge_class}">{rating}</span> (Score: {result['overall_score']})</h3>
            <p><strong>Mode:</strong> {result['mode']}</p>
            <p><strong>Prompt:</strong> {result['prompt']}</p>
            <p><strong>Expected:</strong> {result['expected_response'][:200]}{'...' if len(result['expected_response']) > 200 else ''}</p>
            <p><strong>Agent Response:</strong> ({result['word_count']} words)<br>
            {result['agent_response'][:500]}{'...' if len(result['agent_response']) > 500 else ''}</p>

            <div class="scores">
                <div class="score-box">
                    <strong>Semantic</strong>
                    <div class="score-value">{result['semantic_correctness']}</div>
                </div>
                <div class="score-box">
                    <strong>OBT</strong>
                    <div class="score-value">{result['obt_adherence']}</div>
                </div>
                <div class="score-box">
                    <strong>Complete</strong>
                    <div class="score-value">{result['response_completeness']}</div>
                </div>
                <div class="score-box">
                    <strong>Communication</strong>
                    <div class="score-value">{result['professional_communication']}</div>
                </div>
                <div class="score-box">
                    <strong>Time</strong>
                    <div class="score-value">{result['execution_time_ms']}ms</div>
                </div>
            </div>

            <div class="breakdown">
                <strong>Score Breakdown:</strong><br>
                {result['score_breakdown']}
            </div>

            <div class="checks">
                <strong>✓ Passed Checks:</strong>
"""

        # Add passed checks
        for check_type, checks in passed_checks.items():
            for check in checks:
                html += f'<div class="check-item check-passed">✓ {check}</div>'

        if failed_checks['obt'] or failed_checks['communication']:
            html += '<br><strong>✗ Failed Checks:</strong>'
            for check_type, checks in failed_checks.items():
                for check in checks:
                    html += f'<div class="check-item check-failed">✗ {check}</div>'

        html += """
            </div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ HTML report generated: {output_path}")


if __name__ == "__main__":
    # Find most recent v5 CSV file
    results_dir = Path(__file__).parent / "results"
    csv_files = list(results_dir.glob("evaluation_v5_full_*.csv"))

    if not csv_files:
        print("✗ No v5.0 evaluation results found")
        exit(1)

    latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_html = results_dir / f"evaluation_v5_report_{timestamp}.html"

    print(f"Generating HTML report from: {latest_csv.name}")
    generate_html_report(str(latest_csv), str(output_html))
    print(f"\n🎉 Report ready! Open: {output_html}")
