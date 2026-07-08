---
id:
title: <Project Name> — Engineering Constitution
version: 0.1.0
status: Proposal
owner:
reviewers: []
created:
updated:
milestone: M2
category: Constitution
priority: Critical
depends_on: []
required_by: []
related_documents: []
related_domains: []
related_features: []
related_decisions: []
tags:
  - constitution
risk: High
complexity:
---

# <Project Name> — Engineering Constitution

Amending a Frozen version of this document requires an ADR and an explicit
remediation statement (see `OV-002` Lifecycle). This is a higher bar than
other specifications.

## 1. Engineering Philosophy

One or two paragraphs: what does "good" mean for this project, specifically.

## 2. Rigor Level

**Chosen:** Production-grade | Enterprise-grade | FAANG-level discipline

What this concretely includes and excludes (be specific — "production-grade"
means nothing without a list of what ceremony is and isn't required).

## 3. AI Collaboration Contract

**Chosen:** Code Generator | Senior Engineer | Principal Engineer (technical partner)

What this obligates the agent to do, stated as commitments, not vibes.

## 4. Architecture Ambition

**Chosen:** Monolith | Modular Monolith | Hybrid (monolith now, event-contracts
for future extraction) | Microservices

## 5. Laws

Numbered, non-negotiable rules. Each entry must cite its source.

### Law 1

> Statement of the law.

**Source:** `OV-001` recommendation `<investigation>` / `<claim id>`, or
owner choice from §2–4 above.

*(repeat per law)*

## 6. Amendment Process

This Constitution may be revised only via: (1) an ADR stating the reason
and (2) an explicit list of existing work that becomes non-compliant and
needs remediation. Ordinary version-bump revisions (as used by other
specifications) do not apply here once this document is Frozen.
