---
name: eval-skill
description: Guide an agent on how to evaluate the output quality of a skill using eval-driven iteration, assertions, and test cases. Use when asked to evaluate, test, grade, or measure an Agent Skill's performance.
---

# Evaluating Skill Output Quality

Evaluating a skill involves running structured evaluations (evals) to determine if it produces good outputs consistently and effectively.

## Designing Test Cases
A test case has three parts:
1. **Prompt**: A realistic user message.
2. **Expected output**: A human-readable description of what success looks like.
3. **Input files** (optional): Files the skill needs to work with.

Store test cases in `evals/evals.json` inside your skill directory:
```json
{
  "skill_name": "your-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "realistic user prompt here",
      "expected_output": "description of correct result",
      "files": ["evals/files/input.csv"],
      "assertions": [
        "The output file is valid JSON",
        "The output includes at least 3 recommendations"
      ]
    }
  ]
}
```

## Running Evals
1. Run each test case twice: once **with the skill** and once **without it** (or with a previous version) as a baseline.
2. Ensure each eval run starts with a clean context.
3. Keep track of timing data (duration and token counts) to compare costs.

## Writing Assertions
Assertions are verifiable statements about what the output should contain or achieve.
- **Good assertions**: "The output file is valid JSON", "The chart has labeled axes".
- **Weak assertions**: "The output is good", "The output uses exactly the phrase 'Total'".

## Grading Outputs
1. Evaluate each assertion against the actual outputs.
2. Record **PASS** or **FAIL** with specific evidence quoting or referencing the output.
3. Provide human review to catch things assertions missed (e.g., tone, layout).

## Iterating on the Skill
1. **Failed assertions** point to specific gaps.
2. **Human feedback** points to broader quality issues.
3. **Execution transcripts** reveal *why* things went wrong.
Use these three signals to adjust your `SKILL.md` instructions, generalize fixes, explain reasoning, or bundle repeated work into scripts.