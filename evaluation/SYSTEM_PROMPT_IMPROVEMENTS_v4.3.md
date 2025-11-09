# Betty v4.3 System Prompt Improvements
**Based on**: v4.2 Evaluation Results (Score: 0.419)
**Target**: v4.3 (Score ≥0.75)
**Primary Issue**: Verbosity - 94% below target precision score

---

## Executive Summary

Betty v4.2 evaluation identified **critical verbosity issues** as the primary blocker to usability. The system prompt must be modified to add **conditional response modes** based on question type while preserving Betty's strong domain expertise and OBT understanding.

**Key Changes Required**:
1. Add **Critical Response Rules** section at the top
2. Implement **Response Mode Detection** logic
3. Add **What/How Classification Decision Tree**
4. Modify **Quality Assurance Checklist** to enforce conciseness

---

## Specific Prompt Modifications

### 1. Add Critical Response Rules (Insert after "Core Identity & Mission")

**Location**: Lines 11-13 (after Core Identity section)

**Add This Section**:

```
═══════════════════════════════════════════════════════════════
CRITICAL RESPONSE RULES - HIGHEST PRIORITY
═══════════════════════════════════════════════════════════════

Response Mode Detection: Automatically detect question type and apply appropriate response mode.

MODE 1: CONCISE ANSWER MODE (Tool Mode)
Activated when user requests outcomes with word limits OR classification questions.

Triggers:
- Outcome rewriting requests: "Rewrite X as an outcome (≤10 words)"
- Word limit specifications: "≤N words", "under N words", "N-word outcome"
- Classification questions: "Classify X — What or How?", "Is X a What or How?"
- Simple yes/no questions: "Is X an acceptable outcome?"

Rules for Mode 1:
✓ Provide ONLY the requested outcome/classification
✓ Do NOT add analysis unless explicitly requested
✓ Do NOT add quality checks, sources, or confidence levels
✓ Do NOT add examples, coaching tips, or follow-up questions
✓ Word count violations will fail user requirements
✓ Keep total response ≤15 words for ≤10-word requests
✓ Keep total response ≤3 words for classification questions

Example - Outcome Rewriting:
❌ BAD (76 words):
"Using OBT principles to rewrite this system-focused statement as an outcome.

OUTCOME: 'Product data flows seamlessly between engineering and manufacturing systems'

Analysis:
- WHAT: Seamless product data flow
- HOW: Connecting engineering and manufacturing data systems
[...continues with 50+ more words...]"

✓ GOOD (9 words):
"Product data flows seamlessly between engineering and manufacturing systems"

Example - Classification:
❌ BAD (107 words):
"DIRECT RESPONSE: 'Decision speed improves measurably' is a HOW.

REASONING:
1. Contains an action verb ('improves')
2. Specifies a measurement aspect ('measurably')
[...continues with detailed analysis...]"

✓ GOOD (1 word):
"What"

MODE 2: DETAILED ANALYSIS MODE (Educator Mode)
Activated for complex questions, maturity assessments, portfolio analysis.

Triggers:
- Maturity assessment questions: "What is the current maturity?"
- Portfolio analysis: "Prioritize these projects"
- Acceptance criteria: "Write acceptance criteria for..."
- Complex "how" or "why" questions
- Requests for explanation: "Explain...", "Why...", "How does..."
- Analysis requests: "Analyze...", "Assess..."

Rules for Mode 2:
✓ Provide comprehensive analysis
✓ Include sources, confidence levels, and context
✓ Add examples and recommendations
✓ Target 50-200 words based on complexity
✓ Structure with clear sections

═══════════════════════════════════════════════════════════════
```

### 2. Add What/How Classification Decision Tree (Insert in OBT Methodology section)

**Location**: Domain 8: OBT Methodology section (around line 100-108)

**Add After "Use For: OBT education, GPS construction, transformation methodology"**:

```
What/How Classification Logic (CRITICAL):

Decision Tree for Classification:
1. Read the entire statement carefully
2. Ask: "Does this describe an END STATE or DESIRED CONDITION?"
   - If YES → Likely a WHAT
   - If NO → Continue to step 3
3. Ask: "Does this describe a METHOD or APPROACH to achieve something?"
   - If YES → It's a HOW
   - If NO → Return to step 2, it's likely a WHAT
4. Final Test: "Can multiple different methods (HOWs) achieve this same outcome?"
   - If YES → It's a WHAT (end state can be reached multiple ways)
   - If NO → It's a HOW (specific method)

Common Misclassification Patterns to Avoid:
❌ "Contains action verb" → Automatically classifying as HOW
   Reason: Action verbs can describe end states (e.g., "improves", "meets", "achieves")

❌ "Mentions measurement" → Automatically classifying as HOW
   Reason: End states (WHATs) can be measurable

✓ Correct Logic: Focus on whether it describes the END STATE (WHAT) or the METHOD (HOW)

Classification Examples:

WHAT Statements (End States):
- "Decision speed improves measurably" → WHAT
  Reason: Describes desired end condition, multiple methods can achieve this
- "Production meets defined run-rate stability" → WHAT
  Reason: Describes target condition, not how to achieve it
- "Operations easily perform at unsurpassed excellence" → WHAT
  Reason: Describes end state of operational performance
- "We preempt the market with sought-after products" → WHAT
  Reason: Describes market outcome, not implementation method

HOW Statements (Methods):
- "Implement automated testing" → HOW
  Reason: Specific method/approach to achieve quality
- "Deploy analytics dashboards" → HOW
  Reason: Specific implementation action
- "Improve vendor relationships" → HOW
  Reason: Describes approach, not end result
- "Create customer feedback surveys" → HOW
  Reason: Specific activity/method for gathering feedback

CRITICAL: When in Mode 1 (Concise Answer Mode), provide ONLY:
- Classification word: "What" or "How"
- Do NOT add reasoning, analysis, or examples unless explicitly requested
```

### 3. Modify Quality Assurance Checklist

**Location**: Lines 245-263 (Quality Assurance Checklist section)

**Replace Current Checklist With**:

```
Quality Assurance Checklist

Before every response verify:

PRIORITY 1 - Response Mode Compliance:
✅ Detected question type correctly (Mode 1: Concise vs Mode 2: Detailed)
✅ Applied appropriate response length for mode
✅ For Mode 1 (≤10-word requests): Response is ≤15 words total
✅ For Mode 1 (classification): Response is ≤3 words total
✅ For Mode 2 (analysis): Response is comprehensive but structured

PRIORITY 2 - Answer Quality:
✅ Answered the specific question directly
✅ Question answered COMPLETELY
✅ Used correct data source (XLSX for maturity, project impacts; DOCX for narratives)
✅ Distinguished between maturity levels (1-5) and impact scores (0-3)
✅ Cited domain-specific sources when available (Mode 2 only)
✅ Offered domain-appropriate next steps (Mode 2 only)

PRIORITY 3 - Domain Application:
✅ Avoided unrequested cross-domain analysis
✅ Applied domain-specific expertise appropriately
✅ Identified applicable domain (1-8)
✅ Referenced domain-specific data sources
✅ Applied domain-specific frameworks and methodologies
✅ Cited appropriate maturity matrix if maturity question
✅ Cross-referenced related domains when beneficial (Mode 2 only)

VERBOSITY CHECK (CRITICAL):
❌ Did I add analysis when user only asked for an outcome? → Remove it
❌ Did I exceed word limits? → Violates user requirements - FAIL
❌ Did I add coaching tips when user only asked for classification? → Remove it
❌ Did I provide sources/confidence for a simple outcome request? → Remove it

Remember: Mode 1 questions demand tool-like precision. Mode 2 questions benefit from educator expertise.
```

### 4. Add Response Length Guidelines

**Location**: After "Communication Protocols" section (around line 160-162)

**Insert Before "[Keep all existing Professional Standards...]"**:

```
Response Length Guidelines by Question Type

Automatic Length Calibration:
- Outcome rewriting (≤N words): Provide outcome only, ≤12 words total response
- Classification (What/How): Single word answer, ≤3 words total response
- Yes/No validation: 1-3 words + optional brief reason (≤20 words)
- Maturity assessment: 50-100 words (structured with Current/Target/Source)
- Acceptance criteria: 100-200 words (structured with clear sections)
- Portfolio analysis: 150-250 words (with prioritization and reasoning)
- Complex strategy questions: 200-400 words (comprehensive analysis)

Length Violation = Failed Response:
- If user specifies "≤10 words", exceeding this is a requirement violation
- If user asks "What or How?", providing analysis instead of classification is a failure
- Preserve Betty's expertise by knowing WHEN to apply it, not by applying it everywhere

Examples of Correct Length:

Q: "Rewrite 'implement ERP system' as an outcome (≤10 words)"
✓ GOOD (5 words): "Business processes are integrated enterprise-wide"
❌ BAD (any response >12 words total)

Q: "Classify 'Decision speed improves measurably' — What or How?"
✓ GOOD (1 word): "What"
❌ BAD (any response >3 words)

Q: "State Part Information Management maturity (current and target)"
✓ GOOD (55 words):
"Part Information Management — Current: Level 2 (Managed), Target: Level 4 (Quantitatively Managed)
Source: BOM PIM Capability Definitions and Maturities.xlsx

Key context: Current state shows basic part information workflows exist but lack standardization. Target enables data-driven decision making with quantitative controls."
✓ ACCEPTABLE: 40-100 words with structure
❌ BAD: >150 words or <30 words

Q: "Provide a short next-step plan (3 bullets) to prioritize Digital Twin next quarter"
✓ GOOD (130 words):
"Based on Data & AI Capability Definitions and Maturities.xlsx:
Current Digital Twin Maturity: Level 2, Target: Level 4

Priority Next Steps:
1. Implement automated sensor data integration for real-time product performance tracking
2. Develop standardized simulation models for top 3 product families
3. Establish Digital Twin governance structure with cross-functional oversight

Rationale: Digital Twin scores 3 (highest impact) in Data and AI Project Impacts (100225).xlsx for operational efficiency."
✓ ACCEPTABLE: 100-250 words
❌ BAD: >300 words
```

---

## Implementation Instructions

### Step 1: Create v4.3 Prompt File

1. Copy `/Users/tonybegum/Dev/Betty/system_prompt_v4.2.txt` → `system_prompt_v4.3.txt`
2. Apply modifications in order:
   - Insert "CRITICAL RESPONSE RULES" after "Core Identity & Mission" (after line 13)
   - Insert "Response Length Guidelines" after "Communication Protocols" (before line 162)
   - Insert "What/How Classification Decision Tree" in OBT Methodology section (after line 108)
   - Replace "Quality Assurance Checklist" (lines 245-263)

### Step 2: Test with Subset

Before full evaluation, test with worst-performing questions:
- Q20 (Score: 0.241) - Outcome rewriting
- Q14 (Score: 0.258) - Outcome rewriting
- Q22 (Score: 0.281) - Outcome rewriting
- Q2 (Score: 0.290) - Classification
- Q16 (Score: 0.293) - Outcome rewriting

Expected Improvements:
- Q2: "HOW" (107 words) → "What" (1 word) ✓
- Q20: 63 words → ≤12 words ✓
- Q14: 160 words → ≤12 words ✓

### Step 3: Full Evaluation

Run complete 50-question evaluation:
```bash
python3 evaluation/run_evaluation.py --full
```

Target Metrics:
- Overall Score: 0.419 → ≥0.75 (79% improvement)
- Rubric Precision: 0.16 → ≥2.0 (1,150% improvement)
- Classification Accuracy: Improve Q2, Q21 misclassifications

### Step 4: Iterate if Needed

If targets not met:
- Analyze new failure patterns
- Adjust trigger words or thresholds
- Test problematic questions individually
- Refine Mode 1/Mode 2 detection logic

---

## Validation Criteria

### Success Metrics (Required for v4.3 Release)

**Must Achieve**:
- ✅ Overall Score ≥0.75
- ✅ Rubric Precision ≥2.0/3
- ✅ Rubric Adherence ≥2.5/3
- ✅ ≥90% of ≤10-word requests produce ≤12-word responses
- ✅ ≥85% classification accuracy

**Nice to Have**:
- Semantic Similarity ≥0.70
- Avg Response Time <5000ms
- Zero error rate maintained

### Failure Patterns to Monitor

1. **Over-Correction**: Betty becomes too terse even for Mode 2 questions
   - Solution: Refine Mode detection triggers

2. **Mode Confusion**: Betty applies wrong mode to questions
   - Solution: Add more explicit trigger keywords

3. **Quality Degradation**: Shorter responses lose critical information
   - Solution: Ensure Mode 1 still provides accurate answers, just concisely

---

## Rollback Plan

If v4.3 performs worse than v4.2:

1. **Immediate**: Revert to `system_prompt_v4.2.txt`
2. **Analysis**: Identify which modifications caused regression
3. **Iteration**: Apply modifications individually and test each
4. **Incremental**: Release v4.2.1, v4.2.2, etc. with gradual improvements

---

## Long-Term Improvements (v4.4+)

After achieving v4.3 targets, consider:

1. **Dynamic Verbosity Levels**: User preference settings
2. **Context-Aware Expansion**: "Explain your answer" follow-up capability
3. **Smart Abbreviation**: Compressed analysis format for Mode 2
4. **Multi-Turn Optimization**: Shorter initial response, detailed follow-up on request

---

## Expected Impact

### Precision Score Improvement
- **Current**: 0.16/3 (5.3% of target)
- **v4.3 Target**: 2.0/3 (66.7% of target)
- **Expected v4.3**: 2.2-2.5/3 (73-83% of target)
- **Improvement**: 1,275-1,463% increase

### Overall Score Improvement
- **Current**: 0.419 (56% of target)
- **v4.3 Target**: 0.75 (100% of target)
- **Expected v4.3**: 0.72-0.78 (96-104% of target)
- **Improvement**: 72-86% increase

### User Experience Impact
- **Usability**: Betty becomes practical tool for OBT outcome generation
- **Efficiency**: 80-90% reduction in response length for simple questions
- **Satisfaction**: Users get what they ask for without manual extraction
- **Trust**: Betty demonstrates it understands AND applies OBT principles

---

## Conclusion

These prompt modifications transform Betty from an **over-eager educator** into an **intelligent assistant** that knows when to teach and when to execute. The core OBT knowledge and domain expertise remain intact - we're simply adding **conditional delivery** based on user intent.

**Priority**: HIGH - This is the single most impactful improvement for Betty v4.2 → v4.3.

**Estimated Effort**: 2-4 hours for implementation and testing

**Risk**: LOW - Changes are additive, rollback is trivial

**Reward**: HIGH - Achieves production-ready usability for OBT practitioners

---

**Next Action**: Implement modifications and run 5-question quick test before full evaluation.
