# Improvement Output Template

Use this template as a reference for the expected output structure of the spec quality improver.

## Structure

The output follows this exact format:

```markdown
# Improved Specification
<full improved spec content here>

---

# Improvement Traceability Report

| Issue ID | Spec Section | Improvement Type | Summary |
|--------|-------------|------------------|---------|
| QI-01  | Requirements | Clarity           | Clarified vague wording |
| AC-02  | Feature X    | Acceptance        | Added measurable criteria |
| EC-01  | Feature Y    | Edge Case         | Added invalid input case |
```

## Improved Specification Guidelines

- Preserve all original requirements and functionality
- Only modify sections that were flagged in the analysis report
- Apply changes systematically based on issue categories
- Maintain original document structure unless structural improvements were recommended

## Traceability Report Guidelines

- List every change made with reference to the original issue
- Use consistent improvement type classifications:
  - Clarity: Language clarification, ambiguity resolution
  - Acceptance: Criteria addition or improvement
  - Edge Case: Missing scenario addition
  - Consistency: Terminology or formatting fixes
  - Structural: Organization or formatting improvements
- Provide concise but meaningful summaries
- Maintain traceability for audit purposes