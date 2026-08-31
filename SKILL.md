---
name: job-scout
description: Find and rank internships or entry-level roles against evidence in the user's workspace, research patterns from successful applications, prepare truthful tailored materials, and assist with browser submission only after explicit per-job approval. Use for recurring job discovery, role-fit analysis, application tracking, cover letters, resumes, portfolios, and reviewed application workflows.
---

# Job Scout

Build a conservative, evidence-based job-search loop. Optimize for truthful fit and application quality, not application volume.

## Persistent state

All mutable state lives in a separate private directory, referred to here as `$STATE_DIR`.
This repository holds only the tool. Never commit profile, preference, ledger, or package files into it.

`$STATE_DIR` contains:

- profile.md: verified capabilities, projects, metrics, constraints, and gaps.
- preferences.md: confirmed preferences, provisional assumptions, and feedback.
- ledger.csv: deduplicated job and application history.
- daily/: dated discovery reports.
- packages/: one reviewed package per application.
- references/: research notes.

Do not inspect secrets, credentials, proprietary raw data, or unrelated personal identifiers. Read project summaries, READMEs, reports, and existing application drafts first.

## Refresh profile

1. Scan relevant project summaries and career documents.
2. Record claims only when a local source supports them.
3. Separate verified evidence, reasonable inference, and unknowns.
4. Preserve user corrections. Never promote an inferred skill into a verified claim.

## Daily scout

1. Read profile.md, preferences.md, and ledger.csv.
2. Search recent internships first, then plausible entry-level roles.
3. Cover Linkareer, original company career pages, Wanted, Jumpit, RocketPunch, LinkedIn, Saramin, JobKorea, and relevant public institutions or research labs. Prefer the original posting.
   Fetch the Linkareer listing page first; it renders server-side and its detail pages are readable. Web search results for Korean job boards are stale and have returned closed postings as open, so treat search hits as leads and confirm every deadline and open status on the posting page itself. Incruit and Saramin listing pages do not render.
4. Search the clusters in references/scoring.md and at most one adjacent exploratory cluster.
5. Verify open status, deadline, eligibility, and logistics.
6. Normalize and deduplicate with scripts/job_ledger.py.
7. Score with references/scoring.md.
8. Write daily/YYYY-MM-DD.md with exact workspace evidence and explicit gaps.
9. Deep-review at most three roles. Do not pad the list with weak matches.

## Prepare application

For a strong role, create packages/<company>-<role>-<date>/ containing:

- job-analysis.md: requirements, inferred evaluation rubric, deadline, risks.
- evidence-map.md: requirements mapped to verified evidence or gaps.
- resume-tailored.md: reordered, truthful bullets.
- portfolio-plan.md: project/page order, needed visuals, narrative.
- answers.md: drafts only for questions actually supplied.
- review.md: unresolved facts, sensitive fields, attachments, status.

Research successful materials using references/reference-research.md. Infer structure and evaluator priorities; never copy wording or claims.

## Apply

Follow references/submission.md. Scheduled runs stop at ready_for_review. Interactive submission requires explicit approval for the exact company, role, answers, and attachments. Never infer legal name, contact details, education dates, compensation, work authorization, disability status, or other sensitive values.

## Learning loop

After a user decision or outcome, update ledger.csv and preferences.md. Recalibrate ranking, not evidence, and avoid overfitting to one result.
