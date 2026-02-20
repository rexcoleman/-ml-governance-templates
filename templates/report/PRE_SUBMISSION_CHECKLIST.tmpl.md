# PRE-SUBMISSION CHECKLIST

{{PROJECT_NAME}} — Academic Honesty & Submission Readiness Audit

---

## Purpose

This checklist ensures that the submitted repository and report are compliant with academic honesty policies, contain no prohibited artifacts, and are fully reproducible. Run this checklist before every submission.

---

## 1) Repository Hygiene

### Files That MUST NOT Be in the Repo

- [ ] **Course materials** — Assignment docs, FAQs, grading rubrics, spec documents provided by instructors
- [ ] **Internal scaffolding** — Implementation playbooks, task boards, risk registers, decision logs, changelogs (unless the assignment requires them)
- [ ] **Audit reports** — Any compliance audit documents
- [ ] **Draft/scratch files** — Hypothesis drafts, notes, TODO lists
- [ ] **Raw data** — Large data files should be gitignored, not committed
- [ ] **Compiled files** — `.pyc`, `__pycache__/`, `.ipynb_checkpoints/`
- [ ] **IDE files** — `.vscode/`, `.idea/`, `.DS_Store`
- [ ] **Credentials** — `.env`, API keys, tokens

### Verification Commands

```bash
# Check for course materials (adapt patterns to your course)
git ls-files | grep -iE "(assignment|rubric|faq|spec_requirements|honesty)" | head -20

# Check for compiled files
git ls-files | grep -E "\\.pyc$|__pycache__" | head -20

# Check for large files
git ls-files | xargs ls -la 2>/dev/null | awk '$5 > 1000000 {print $5, $NF}' | sort -rn | head -10

# Check for sensitive files
git ls-files | grep -iE "(\\.env|credentials|secret|token)" | head -10
```

---

## 2) Git History Audit

### Raw Data in History

Even if raw data files are currently gitignored, they may exist in old commits.

```bash
# Check for data files in git history
git rev-list --objects --all | grep -iE "\\.(csv|tsv|json|npz|pkl|parquet)$" | head -20

# Check for large blobs in history
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectsize) %(objectname) %(rest)' | awk '$1 == "blob" && $2 > 1000000 {print $2, $4}' | sort -rn | head -10
```

**If found:** Consider an orphan branch strategy to create a clean single-commit history:

```bash
git checkout --orphan clean-main
git rm -r --cached .
git add -A
git commit -m "Clean submission commit"
git branch -D main
git branch -m clean-main main
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## 3) Report Content Audit

- [ ] **Report link** — Valid READ-ONLY link (not a placeholder like `XXXX-REPLACE-ME`)
- [ ] **Git SHA** — Matches the actual final commit pushed to the institutional repo
- [ ] **AI Use Statement** — Present, accurate, placed before References
- [ ] **Test count** — If mentioned (e.g., "294 tests pass"), verify it matches `pytest` output
- [ ] **Dataset statistics** — Row counts, feature counts, class distributions match actual data
- [ ] **Metric values** — All reported numbers trace to `final_eval_results.json`
- [ ] **No internal references** — Report doesn't reference internal docs (playbooks, task boards, etc.)
- [ ] **Special characters** — No unescaped `#` in LaTeX URLs, no Unicode in LaTeX that your editor can't compile

---

## 4) Reproducibility Verification

- [ ] **Environment installs cleanly:** `{{ENV_MANAGER}} env create -f {{ENV_FILE}}` exits 0
- [ ] **All scripts exist:** Every command in REPRO document references an existing script
- [ ] **Tests pass:** `python -m pytest tests/ -v` — all pass
- [ ] **Seeds documented:** Default seed and stability list in REPRO
- [ ] **Data paths documented:** REPRO explains where to get data and where to place it

---

## 5) Institutional Repository Check

- [ ] **Correct repo:** Code is on the institutional GitHub (not personal)
- [ ] **Correct branch:** Main/master branch has the submission code
- [ ] **Commit SHA matches:** REPRO document SHA matches the actual pushed commit
- [ ] **No extra commits after SHA:** If REPRO references a specific SHA, no subsequent commits change the code

---

## 6) Academic Honesty Specific

*(Adapt to your institution's policy.)*

- [ ] **No prior-semester materials:** No code, reports, or solutions from prior semesters
- [ ] **No collaboration artifacts:** No shared code from classmates (unless permitted)
- [ ] **AI disclosure:** All AI-assisted work properly disclosed per policy
- [ ] **Citations:** All external references properly cited
- [ ] **Original work:** Analysis and interpretation are original, not copied

---

## 7) Final Delivery Checklist

| Item | Status | Notes |
|------|--------|-------|
| Report PDF within page limit | [ ] | |
| REPRO PDF complete | [ ] | |
| Code pushed to institutional repo | [ ] | |
| SHA in REPRO matches push | [ ] | |
| READ-ONLY link works in incognito | [ ] | |
| Submission platform uploaded | [ ] | |
| Before deadline | [ ] | |
