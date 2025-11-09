# Betty Evaluation - Quick Start Guide

## 🚀 Run Evaluation in 3 Steps

### Step 1: Navigate to Evaluation Directory
```bash
cd /Users/tonybegum/Dev/Betty/evaluation
```

### Step 2: Run Full Evaluation (50 questions)
```bash
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --output results/evaluation_$(date +%Y%m%d_%H%M%S).csv
```

### Step 3: Generate Report
```bash
agenteval report \
  --input results/evaluation_*.csv \
  --output results/summary_report.html
```

---

## 📊 What Gets Tested

### 50 Questions Across 6 Categories:

1. **Outcome Rewriting** (12 questions, 25%)
   - Converting activities to outcomes
   - Example: "implement ERP" → "Business processes are integrated enterprise-wide"

2. **Classification** (10 questions, 20%)
   - What vs How distinction
   - Example: "Decision speed improves" → What (not How)

3. **Acceptance Criteria** (6 questions, 15%)
   - Defining owner, measure, evidence
   - Example: Owner: HR/L&D; Measure: competency pass rate; Goal: 90% in 12mo

4. **Domain Expertise** (10 questions, 20%)
   - 8 product development domains
   - GPS framework, maturity assessments, data sources

5. **Maturity Assessment** (5 questions, 10%)
   - 1-5 capability maturity scale
   - Example: Current Level 2 (Managed), Target Level 4 (Quantitatively Managed)

6. **Portfolio Analysis** (7 questions, 10%)
   - Project prioritization, RACI, risk assessment

---

## 🎯 Scoring System

### 5 Dimensions (Weighted):

| Dimension | Weight | Scale | What It Measures |
|-----------|--------|-------|------------------|
| **Exact Match** | 15% | 0/1 | Perfect answer match |
| **Semantic Similarity** | 25% | 0-1 | Meaning similarity |
| **Rubric Precision** | 20% | 0-3 | Length & concept accuracy |
| **Rubric Adherence** | 25% | 0-3 | OBT rule compliance |
| **Rubric Explanation** | 15% | 0-3 | Justification quality |

### Target Scores:

- **Excellent:** ≥0.85 (Production ready)
- **Good:** 0.75-0.84 (Minor improvements needed)
- **Acceptable:** 0.65-0.74 (Needs work)
- **Needs Improvement:** 0.50-0.64 (Significant gaps)
- **Insufficient:** <0.50 (Major issues)

---

## 🔍 Quick Tests

### Test Single Question
```bash
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --filter "test_id=1" \
  --output results/test_q1.csv \
  --verbose
```

### Test Specific Category
```bash
# Test only outcome rewriting
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --filter "category=outcome_rewriting" \
  --output results/outcome_test.csv
```

### Test Specific Domain
```bash
# Test only OBT Methodology
agenteval run \
  --config betty_evaluation.yml \
  --testset betty_testset_50q.csv \
  --filter "domain=OBT Methodology" \
  --output results/obt_test.csv
```

---

## 📁 File Structure

```
/Users/tonybegum/Dev/Betty/evaluation/
├── betty_evaluation.yml          # AWS AgentCore configuration
├── betty_testset_50q.csv         # 50-question testset
├── README_EVALUATION.md          # Comprehensive documentation
├── QUICK_START.md                # This file
└── results/                      # Evaluation outputs (created automatically)
    ├── evaluation_YYYYMMDD_HHMMSS.csv
    └── summary_report.html
```

---

## ⚠️ Common Issues

### Issue: "agenteval: command not found"
**Solution:**
```bash
pip install agenteval-cli
```

### Issue: Low Adherence Scores (<2.0)
**Cause:** Betty violating OBT rules (>10 words, metrics in outcomes, How verbs)
**Solution:** Review system prompt OBT compliance sections

### Issue: Poor Semantic Similarity (<0.60)
**Cause:** Missing domain knowledge or incorrect data
**Solution:** Verify knowledge base loaded (54 documents)

### Issue: Slow Response Times (>30s)
**Cause:** Large vector searches, API latency
**Solution:** Optimize ChromaDB indexing, adjust search limits

---

## 🎓 OBT Quick Reference

### Outcome Statement Rules:
1. ✅ **≤10 words**
2. ✅ **Present tense** (describes achieved state)
3. ✅ **Metric-free** (numbers go in acceptance criteria)
4. ✅ **Result-focused** (What, not How)
5. ✅ **No implementation verbs** (deploy, implement, build, create)

### What vs How:
- **What (Outcome):** "Decisions are data-informed consistently"
- **How (Method):** "Deploy analytics dashboards"

### Acceptance Criteria Format:
- **Owner:** Who is accountable
- **Measure:** What metric tracks success
- **Goal:** Target value with timeline
- **Evidence:** Proof of achievement

### Maturity Scale (1-5):
1. **Initial** - Ad hoc, reactive
2. **Managed** - Repeatable but inconsistent
3. **Defined** - Documented and standardized
4. **Quantitatively Managed** - Measured and controlled
5. **Optimized** - Continuous improvement

### Impact Scoring (0-3):
- **0** - No impact
- **1** - Low impact
- **2** - Medium impact (counts in totals)
- **3** - High impact (counts in totals)

---

## 📞 Support

**Developer:** Tony Begum, AI Architect, BoldARC Advisors
**Version:** 4.2
**Documentation:** See README_EVALUATION.md for comprehensive guide
