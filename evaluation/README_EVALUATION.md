# Betty v4.2 AWS AgentCore Evaluation Guide

## Overview

This evaluation framework tests Betty's strategic transformation capabilities across Outcome-Based Thinking (OBT) methodology and 8 product development domains.

**Version:** 4.2
**Created:** October 2025
**Developer:** Tony Begum, AI Architect, BoldARC Advisors
**Test Coverage:** 50 questions across 6 categories

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Evaluation Framework](#evaluation-framework)
3. [Test Categories](#test-categories)
4. [Scoring Methodology](#scoring-methodology)
5. [Running Evaluations](#running-evaluations)
6. [Interpreting Results](#interpreting-results)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- AWS CLI configured with appropriate credentials
- AWS AgentCore access and permissions
- Betty v4.2 deployed and accessible
- Python 3.9+ (for local evaluation scripts)

### Installation

```bash
# Navigate to evaluation directory
cd /Users/tonybegum/Dev/Betty/evaluation

# Install AWS AgentCore CLI (if not already installed)
pip install agenteval-cli

# Verify installation
agenteval --version
```

### Running Your First Evaluation

```bash
# Run evaluation with the provided testset
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --output results/evaluation_$(date +%Y%m%d_%H%M%S).csv

# Generate summary report
agenteval report \
  --input results/evaluation_*.csv \
  --output results/summary_report.html
```

---

## Evaluation Framework

### Test Dimensions

Betty's evaluation uses a **5-dimensional scoring system**:

| Dimension | Weight | Scale | Description |
|-----------|--------|-------|-------------|
| **Exact Match** | 15% | 0/1 | Binary match to expected response |
| **Semantic Similarity** | 25% | 0-1 | Vector similarity between responses |
| **Rubric Precision** | 20% | 0-3 | Length accuracy & concept precision |
| **Rubric Adherence** | 25% | 0-3 | OBT methodology compliance |
| **Rubric Explanation** | 15% | 0-3 | Response quality & justification |

### Overall Score Calculation

```
Overall Score =
  (Exact_Match × 0.15) +
  (Semantic_Similarity × 0.25) +
  (Rubric_Precision/3 × 0.20) +
  (Rubric_Adherence/3 × 0.25) +
  (Rubric_Explanation/3 × 0.15)
```

### Performance Benchmarks

| Rating | Score Range | Description |
|--------|-------------|-------------|
| **Excellent** | 0.85 - 1.00 | Outstanding OBT methodology mastery |
| **Good** | 0.75 - 0.84 | Strong performance with minor gaps |
| **Acceptable** | 0.65 - 0.74 | Adequate understanding, needs improvement |
| **Needs Improvement** | 0.50 - 0.64 | Significant gaps in methodology |
| **Insufficient** | < 0.50 | Fundamental misunderstanding |

---

## Test Categories

### 1. Outcome Rewriting (25% - 12 questions)

**Purpose:** Tests ability to convert activity statements to outcome statements

**Example:**
- **Prompt:** "Rewrite 'implement ERP system' as an outcome (≤10 words)"
- **Expected:** "Business processes are integrated enterprise-wide"
- **Common Errors:**
  - Including metrics: "ERP system achieves 95% adoption"
  - Using How verbs: "Deploy SAP ERP across all locations"
  - Exceeding word limit

**Scoring Focus:**
- Rubric Precision: 3 = concise, 4-7 words, clear concept
- Rubric Adherence: 3 = present tense, metric-free, ≤10 words
- Rubric Explanation: 2-3 = adequate to clear reasoning

### 2. Classification (20% - 10 questions)

**Purpose:** Tests ability to distinguish What (outcomes) from How (methods)

**Example:**
- **Prompt:** "Classify 'Decision speed improves measurably' — What or How?"
- **Expected:** "What"
- **Common Errors:**
  - Confusing result states with methods
  - Misclassifying ambiguous statements

**Scoring Focus:**
- Exact Match: Critical for binary classification
- Rubric Explanation: Must provide clear justification

### 3. Acceptance Criteria (15% - 6 questions)

**Purpose:** Tests ability to define owner, measure, and evidence for outcomes

**Example:**
- **Prompt:** "Write acceptance criteria for 'Workforce capabilities enhanced significantly'"
- **Expected:** "Owner: HR/L&D; Measure: competency assessment pass rate; Goal: 90% within 12 months; Evidence: assessment reports"

**Scoring Focus:**
- Rubric Precision: Must include all 4 components (owner, measure, goal, evidence)
- Rubric Adherence: Metrics belong HERE, not in outcome statements

### 4. Domain Expertise (20% - 10 questions)

**Purpose:** Tests knowledge across 8 product development domains

**Domains Tested:**
1. Change Control Management (3 questions)
2. BOM & PIM Management (3 questions)
3. Requirements Management (2 questions)
4. Design Management & Collaboration (3 questions)
5. Data & AI (2 questions)
6. Global PD (4 questions)
7. OBT Methodology (8 questions)
8. Cross-Domain Integration (5 questions)

**Scoring Focus:**
- Domain accuracy and data source citation
- Distinction between maturity levels (1-5) and impact scores (0-3)
- Confidence level statements

### 5. Maturity Assessment (10% - 5 questions)

**Purpose:** Tests capability maturity evaluation on 1-5 scale

**Maturity Levels:**
1. **Initial:** Ad hoc, reactive processes
2. **Managed:** Repeatable but inconsistent
3. **Defined:** Standardized and documented
4. **Quantitatively Managed:** Measured and controlled
5. **Optimized:** Continuous improvement focus

**Example:**
- **Prompt:** "State Part Information Management maturity (current and target)"
- **Expected:** "Part Information Management — Current: Level 2 (Managed), Target: Level 4 (Quantitatively Managed)"

### 6. Portfolio Analysis (10% - 7 questions)

**Purpose:** Tests project prioritization and impact scoring

**Topics:**
- Project priority ranking by capability impact
- Portfolio weight analysis (Pain/Capabilities/Infrastructure)
- RACI stakeholder assignment
- Risk identification and mitigation

---

## Scoring Methodology

### Rubric Precision (0-3 scale)

| Score | Length Precision | Concept Precision | Description |
|-------|------------------|-------------------|-------------|
| **3** | Exact or ±1-2 words | 100% concepts covered | Excellent - concise and complete |
| **2** | ±3-5 words | 80-90% concepts | Good - minor verbosity or gaps |
| **1** | ±6-15 words | 50-79% concepts | Fair - moderate issues |
| **0** | >15 words off | <50% concepts | Poor - excessive verbosity or missing concepts |

### Rubric Adherence (0-3 scale)

**OBT Compliance Checklist:**
- ✅ ≤10 words for outcome statements
- ✅ Present tense for achieved states
- ✅ Metric-free (numbers in acceptance criteria only)
- ✅ Distinguishes What from How
- ✅ Avoids implementation verbs (deploy, implement, build, create)

| Score | Violations | Description |
|-------|------------|-------------|
| **3** | 0 violations | Excellent - perfect OBT adherence |
| **2** | 1-2 minor violations | Good - minor format issues |
| **1** | 3-4 violations | Fair - multiple violations but core understanding present |
| **0** | 5+ violations | Poor - fundamental misunderstanding |

### Rubric Explanation (0-3 scale)

| Score | Justification Quality | Description |
|-------|----------------------|-------------|
| **3** | Clear with evidence | Excellent - transparent reasoning with supporting evidence |
| **2** | Adequate explanation | Good - sufficient explanation with minor gaps |
| **1** | Minimal reasoning | Fair - unclear or incomplete reasoning |
| **0** | No justification | Poor - missing or incorrect reasoning |

---

## Running Evaluations

### Standard Evaluation Run

```bash
# Full 50-question evaluation
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --output results/full_evaluation_$(date +%Y%m%d_%H%M%S).csv \
  --verbose
```

### Category-Specific Evaluation

```bash
# Test only outcome rewriting (questions 1-12, 19-20, 27, 29-30, 33-34, 36, 38-39)
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --filter "category=outcome_rewriting" \
  --output results/outcome_rewriting_$(date +%Y%m%d_%H%M%S).csv
```

### Domain-Specific Evaluation

```bash
# Test only OBT Methodology domain
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --filter "domain=OBT Methodology" \
  --output results/obt_methodology_$(date +%Y%m%d_%H%M%S).csv
```

### Parallel Execution (Faster)

```bash
# Run with 4 parallel workers
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --workers 4 \
  --output results/parallel_evaluation_$(date +%Y%m%d_%H%M%S).csv
```

---

## Interpreting Results

### Output CSV Format

The evaluation produces CSV files with these columns:

| Column | Description |
|--------|-------------|
| `test_id` | Question number (1-50) |
| `category` | Test category (outcome_rewriting, classification, etc.) |
| `domain` | Domain area (OBT Methodology, Global PD, etc.) |
| `prompt` | Question text |
| `expected_response` | Correct answer |
| `agent_response` | Betty's actual response |
| `exact_match` | 0 or 1 |
| `semantic_similarity` | 0.0 - 1.0 |
| `rubric_precision` | 0-3 |
| `rubric_adherence` | 0-3 |
| `rubric_explanation` | 0-3 |
| `overall_score` | 0.0 - 1.0 (weighted composite) |
| `execution_time_ms` | Response time in milliseconds |
| `error` | Error message if failure occurred |
| `analysis_notes` | Detailed scoring rationale |

### Example Result Analysis

```csv
test_id,category,prompt,expected_response,agent_response,exact_match,semantic_similarity,rubric_precision,rubric_adherence,overall_score,analysis_notes
1,outcome_rewriting,"Rewrite 'implement ERP system' as an outcome","Business processes are integrated enterprise-wide","Business processes integrate seamlessly enterprise-wide",0,0.95,3,3,0.89,"Excellent - added 'seamlessly' (acceptable enhancement), maintains OBT compliance"
```

**Interpretation:**
- **Exact Match = 0:** Response differs slightly from expected
- **Semantic Similarity = 0.95:** Very close meaning (excellent)
- **Rubric Precision = 3:** Proper length (7 words vs 6 expected)
- **Rubric Adherence = 3:** Perfect OBT compliance
- **Overall Score = 0.89:** Excellent performance

### Summary Report Generation

```bash
# Generate HTML summary report with visualizations
agenteval report \
  --input results/full_evaluation_20251016_155003.csv \
  --output results/summary_report.html \
  --charts

# Generate category breakdown
agenteval report \
  --input results/full_evaluation_20251016_155003.csv \
  --group-by category \
  --output results/category_analysis.html
```

### Key Metrics to Monitor

1. **Overall Score:** Should be ≥0.75 for production readiness
2. **Rubric Adherence:** Should be ≥2.5 average (OBT compliance)
3. **Semantic Similarity:** Should be ≥0.70 average
4. **Execution Time:** Should be <15s per question (target), <30s (threshold)
5. **Error Rate:** Should be <5% of questions

---

## Troubleshooting

### Common Issues

#### 1. Low Rubric Adherence Scores

**Symptoms:** Average rubric_adherence < 2.0

**Common Causes:**
- Betty violating ≤10 word rule for outcomes
- Including metrics in outcome statements
- Using How verbs (implement, deploy, create)
- Missing present tense

**Solutions:**
- Review system prompt OBT compliance sections
- Check if Betty is providing too much context/explanation
- Verify knowledge base has correct OBT methodology documents

#### 2. Poor Semantic Similarity

**Symptoms:** Average semantic_similarity < 0.60

**Common Causes:**
- Betty misunderstanding question intent
- Missing domain knowledge
- Hallucination or incorrect data citations

**Solutions:**
- Verify knowledge base is properly loaded (54 documents)
- Check if specific domain files are accessible
- Review system prompt domain routing logic

#### 3. Excessive Response Times

**Symptoms:** execution_time_ms > 30000 (30 seconds)

**Common Causes:**
- Large knowledge base searches
- Complex RAG retrieval
- API throttling or network latency

**Solutions:**
- Optimize vector database indexing
- Adjust search result limit (currently 8)
- Consider caching frequent queries

#### 4. High Error Rates

**Symptoms:** >10% of questions return errors

**Common Causes:**
- API connection issues
- Knowledge base unavailable
- System prompt corruption

**Solutions:**
- Verify Streamlit app is running
- Check ChromaDB connection
- Validate system prompt integrity

### Validation Commands

```bash
# Check Betty service health
curl http://localhost:8501/_stcore/health

# Verify knowledge base size
# Should show 54 documents loaded
grep "Loading.*documents" logs/streamlit.log

# Test single question manually
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --filter "test_id=1" \
  --output results/debug_test.csv \
  --verbose
```

---

## Advanced Usage

### Custom Testset Creation

Create your own CSV testset with this structure:

```csv
test_id,category,domain,prompt,expected_response,distractor_1,distractor_2,distractor_3,rubric_precision_target,rubric_adherence_target,rubric_explanation_target,notes
51,outcome_rewriting,Custom Domain,Your question here,Expected answer,Wrong answer 1,Wrong answer 2,Wrong answer 3,3,3,2,Optional notes
```

### Batch Evaluation

```bash
# Run multiple testsets in sequence
for testset in testsets/*.csv; do
  agenteval run \
    --config betty_evaluation.yml \
    --testset "$testset" \
    --output "results/batch_$(basename $testset)"
done

# Aggregate all results
agenteval report \
  --input results/batch_*.csv \
  --aggregate \
  --output results/batch_summary.html
```

### Continuous Evaluation (CI/CD Integration)

```yaml
# .github/workflows/betty_evaluation.yml
name: Betty Evaluation
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Betty Evaluation
        run: |
          pip install agenteval-cli
          agenteval run \
            --config evaluation/betty_evaluation.yml \
            --testset evaluation/betty_testset_50q.csv \
            --output results/ci_evaluation.csv \
            --threshold 0.75
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: evaluation-results
          path: results/
```

---

## Reference Materials

### OBT Methodology Quick Reference

**What vs How:**
- **What (Outcome):** Describes the achieved result state
  - Example: "Decisions are data-informed consistently"
- **How (Method):** Describes the activity or implementation
  - Example: "Deploy analytics dashboards"

**Outcome Statement Rules:**
1. ≤10 words
2. Present tense
3. Metric-free
4. Result-focused
5. No implementation verbs

**Acceptance Criteria Format:**
- **Owner:** Who is accountable
- **Measure:** What metric tracks success
- **Goal:** Target value with timeline
- **Evidence:** Proof of achievement

### Betty v4.2 Key Facts

- **Total Knowledge Files:** 54 documents
- **Data Completeness:** 95%
- **Domains:** 8 (Change Control, BOM/PIM, Requirements, Design, PD Framework, Data & AI, Global PD, OBT)
- **GPS Framework:** 288 outcomes across 13 clusters
- **Model:** Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
- **Embedding:** all-mpnet-base-v2
- **Destination:** "Customers always choose Molex first"

### Maturity Scale Reference

| Level | Name | Description |
|-------|------|-------------|
| **1** | Initial | Ad hoc, reactive, inconsistent |
| **2** | Managed | Repeatable but not standardized |
| **3** | Defined | Documented and standardized |
| **4** | Quantitatively Managed | Measured and controlled |
| **5** | Optimized | Continuous improvement |

### Impact Scoring Reference

| Score | Meaning | Description |
|-------|---------|-------------|
| **0** | No Impact | Project doesn't address this capability |
| **1** | Low Impact | Minor improvement or enabler |
| **2** | Medium Impact | Significant capability advancement |
| **3** | High Impact | Transformational capability change |

**Note:** Only scores of 2 and 3 count toward total impact calculations.

---

## Support and Feedback

For questions, issues, or feedback regarding Betty's evaluation framework:

**Developer:** Tony Begum, AI Architect
**Organization:** BoldARC Advisors
**Version:** 4.2
**Last Updated:** October 2025

---

## Appendix: Complete Test Breakdown

### Category Distribution

| Category | Questions | Weight | Focus |
|----------|-----------|--------|-------|
| Outcome Rewriting | 12 | 25% | Activity → Outcome transformation |
| Classification | 10 | 20% | What vs How distinction |
| Acceptance Criteria | 6 | 15% | Owner/Measure/Evidence definition |
| Domain Expertise | 10 | 20% | Multi-domain knowledge |
| Maturity Assessment | 5 | 10% | 1-5 capability maturity scale |
| Portfolio Analysis | 7 | 10% | Project prioritization and alignment |

### Domain Distribution

| Domain | Questions | Focus Areas |
|--------|-----------|-------------|
| OBT Methodology | 27 | Core methodology, GPS framework |
| Global PD | 9 | Enterprise strategy, KPIs, portfolio |
| Change Control | 4 | ECO workflows, traceability |
| BOM & PIM | 3 | Master data, part information |
| Requirements | 2 | Requirement capture, validation |
| Design Management | 3 | Design workflows, collaboration |
| Data & AI | 2 | Data governance, AI strategy |

### Question Type Distribution

| Type | Count | Examples |
|------|-------|----------|
| Outcome Creation | 15 | "Create a ≤10-word outcome for..." |
| Classification | 10 | "Classify X — What or How?" |
| Reframing | 7 | "Rewrite X as an outcome" |
| Criteria Definition | 6 | "Write acceptance criteria for..." |
| Knowledge Recall | 8 | "State maturity level...", "What is...?" |
| Analysis | 4 | "Prioritize projects...", "Which area underrepresented?" |

---

## Changelog

**v4.2 (October 2025)**
- Initial evaluation framework creation
- 50-question testset with 6 categories
- 8-domain coverage including new SharePoint data
- 5-dimensional scoring methodology
- AWS AgentCore integration configuration

---

## License

Internal use only - BoldARC Advisors / Molex Product Development
