# Oriveda

> **Engineering the Future, Deliberately.**

Oriveda is a living engineering knowledge system that enables humans and AI to collaboratively design, build, evolve, and maintain production-grade software through structured knowledge, principled architecture, and deliberate decision-making.

Unlike traditional documentation repositories, Oriveda is designed to become the **single source of truth** for engineering knowledge. It captures not only *what* a system is, but *why* it exists, *how* it should evolve, and *which* decisions shape its future.

The long-term vision is to make Oriveda an engineering operating system where architecture, documentation, implementation, testing, and AI collaboration evolve together.

---

## Vision

Modern software projects often lose knowledge faster than they gain code.

Architecture decisions disappear into chat conversations.
Business rules become hidden inside implementations.
Documentation becomes outdated.
AI assistants lose context across sessions.

Oriveda exists to solve this problem.

Every important engineering decision should be:

- Discoverable
- Explainable
- Versioned
- Traceable
- Reusable
- Understandable by both humans and AI

The implementation is merely one consumer of this knowledge.

---

## Core Philosophy

Oriveda is built on one simple belief:

> **Knowledge outlives implementation.**

Code changes.

Frameworks change.

Programming languages change.

Engineering principles should not.

The objective is to preserve engineering knowledge independently of technology choices.

---

## The Oriveda Principles

### Principle 1

**Knowledge outlives implementation.**

Knowledge should survive framework migrations, language changes and complete rewrites.

---

### Principle 2

**Every decision should be discoverable.**

Architectural decisions should never exist only in conversations.

---

### Principle 3

**Every specification has one purpose.**

A specification should have a single responsibility and a clearly defined owner.

---

### Principle 4

**Documentation is executable knowledge.**

Documentation is not historical record.
It is the authoritative description of how a system should behave.

---

### Principle 5

**Humans and AI consume the same knowledge.**

Every specification should be understandable by both human engineers and AI engineering agents.

---

### Principle 6

**The framework evolves independently of products.**

Oriveda is reusable across multiple products and domains.

---

### Principle 7

**Every architectural shortcut is intentional.**

Shortcuts are acceptable only when documented together with their rationale and future migration strategy.

---

### Principle 8

**Consistency beats cleverness.**

Predictability creates maintainability.

---

## Repository Structure

```text
oriveda/
│
├── .oriveda/
│   ├── schemas/
│   ├── glossary.yaml
│   ├── knowledge_graph.yaml
│   ├── manifest.yaml
│   └── taxonomy.yaml
│
├── assets/
├── changelog/
├── examples/
│
├── knowledge/
│   ├── appendix/
│   ├── architecture/
│   ├── constitution/
│   ├── decisions/
│   ├── discovery/
│   ├── domains/
│   ├── features/
│   ├── prompts/
│   ├── standards/
│   └── vision/
│
├── scripts/
├── standards/
├── templates/
│
└── README.md
```

---

## Knowledge Hierarchy

Oriveda organizes engineering knowledge into multiple layers.

```text
Vision
        │
        ▼
Discovery
        │
        ▼
Constitution
        │
        ▼
Architecture
        │
        ▼
Standards
        │
        ▼
Domains
        │
        ▼
Features
        │
        ▼
Implementation Prompts
        │
        ▼
Engineering Decisions
```

Each layer builds upon the previous one.

---

## Getting Started With a New Project

Oriveda governs a project via a **bootstrap file** that lives in *that
project's own repository* — never here (see `ADR-0001`, `ADR-0002`). The
bootstrap file makes any coding agent working in that project
automatically follow Oriveda's protocols: which `PRM-*` prompt applies,
what the Constitution's Laws are once frozen, which Standards bind a
given change — without you having to paste a protocol document into every
session.

To set one up, give your coding agent the prompt below **from within your
target project** (not from this repository). It works whether or not your
project already has a repository or any code — Oriveda itself started
with framework knowledge and no product code, and reached implementation
(M8) only much later. If you have nothing but an idea, the agent
initializes a fresh workspace first; that workspace can become your real
product repository later, or simply hold documentation until it does.

```text
You are setting up this project to be governed by the Oriveda engineering
framework (https://github.com/VedantJoshi23/Oriveda).

1. If this directory is not already a git repository, run `git init`.
   A project doesn't need existing code to start — only a place to keep
   Oriveda's own artifacts (evidence log, and later Constitution,
   Architecture, Domain and Feature specs) as they're produced.

2. Add Oriveda as a git submodule at `.oriveda-framework/`:
     git submodule add https://github.com/VedantJoshi23/Oriveda.git .oriveda-framework

3. Create a bootstrap file at this project's root (name it `CLAUDE.md`,
   or `AGENTS.md` if you use a different agent — create both if you use
   more than one). It must:
   - State that this project follows Oriveda, and point to
     `.oriveda-framework/knowledge/prompts/OV-008-prompt-library-protocol.md`
     for the full prompt catalog.
   - Instruct: before any action, identify which PRM-* prompt applies
     to the current task and load only the Frozen specs it points to —
     never restate their content into this bootstrap file.
   - Once this project has a frozen Constitution
     (`knowledge/constitution/` in this project, not the submodule),
     point to it and state its Laws must never be silently violated.
   - State clearly that this file is a pointer, not a copy — if it starts
     accumulating restated rules instead of references, that's a mistake
     to fix, not a convenience to keep.

4. Mirror Oriveda's own `knowledge/` layout in this project (discovery,
   constitution, architecture, standards, domains, features, decisions),
   empty for now — this is where this project's own specs will live as
   each milestone produces them. These are this project's artifacts, not
   Oriveda's; they use this project's own DOM-/FEAT-/STD-/ADR- naming,
   not Oriveda's OV- numbering.

5. Once set up, begin with `PRM-DISCOVERY`
   (`.oriveda-framework/knowledge/discovery/
   OV-000-knowledge-acquisition.md` and `OV-001-discovery-protocol.md`):
   ask me what evidence I have about this project (existing code, a PRD,
   Figma, screenshots, a video — anything), and start Discovery from
   whatever I actually have. Don't assume a repository full of code is
   required.
```

This prompt is intentionally generic — see `examples/` in this repository
for what the output of following it looked like end-to-end against a
sample project.

---

## Naming Convention

### Specifications

Oriveda's own protocols, one per milestone (see `knowledge/`):

```text
OV-000 Knowledge Acquisition Specification (M1)
OV-001 M1 Discovery Protocol
OV-002 M2 Constitution Protocol
OV-003 M3 System Architecture Protocol
OV-004 M3 Technology Decisions Protocol
OV-005 M4 Standards Protocol
OV-006 M5 Domain Specification Protocol
OV-007 M6 Feature Specification Protocol
OV-008 M7 Prompt Library Protocol
```

---

### Architecture Decision Records

```text
ADR-0001
ADR-0002
ADR-0003
```

---

### Domains

```text
DOM-CATALOG
DOM-INVENTORY
DOM-ORDER
DOM-PAYMENT
```

---

### Features

```text
FEAT-WISHLIST
FEAT-COUPONS
FEAT-CHECKOUT
```

---

### Standards

```text
STD-API
STD-DATABASE
STD-CODE
STD-TESTING
```

---

### Prompt Templates

The fixed catalog defined by `OV-008`, one per protocol above plus one
cross-cutting review prompt:

```text
PRM-DISCOVERY
PRM-CONSTITUTION
PRM-ARCHITECTURE
PRM-STANDARDS
PRM-DOMAIN
PRM-FEATURE
PRM-REVIEW
```

---

## Metadata Specification

Every specification begins with machine-readable metadata.

```yaml
---
id: OV-001
title:
version:
status:
owner:
reviewers:
created:
updated:
milestone:
category:
priority:
depends_on:
required_by:
related_documents:
related_domains:
related_features:
related_decisions:
tags:
risk:
complexity:
---
```

This metadata allows future tooling and AI agents to understand relationships between specifications without parsing natural language.

---

## Specification Lifecycle

Every specification follows the same lifecycle.

```text
Proposal
      │
      ▼
Draft
      │
      ▼
Architecture Review
      │
      ▼
Revision
      │
      ▼
Approved
      │
      ▼
Frozen
      │
      ▼
Superseded
```

Knowledge evolves deliberately.

---

## Versioning

Oriveda maintains two independent version histories.

### Framework Version

Tracks the evolution of Oriveda itself.

Example:

```text
0.1.0
0.2.0
1.0.0
```

---

### Specification Version

Tracks revisions to individual specifications.

Example:

```text
OV-001 v1.0.0
OV-001 v1.1.0
OV-001 v2.0.0
```

---

## Contribution Guidelines

Every contribution should improve both the implementation **and** the engineering knowledge.

### Rules

1. Every specification must include metadata.
2. Every architectural decision must have an ADR.
3. Every feature belongs to exactly one owning domain.
4. Every specification declares its dependencies.
5. Breaking changes require impact analysis.
6. No orphan specifications.
7. Documentation and implementation evolve together.
8. Cross-references must remain valid.
9. New standards should be reusable beyond a single project.
10. Engineering knowledge is treated as a first-class artifact.

---

## Long-Term Vision

The first implementation of Oriveda will power a production-grade jewelry e-commerce platform.

The framework itself, however, is intentionally domain-agnostic.

The long-term goal is to make Oriveda reusable for any software system—from SaaS platforms and marketplaces to healthcare, ERP, fintech, and AI-native applications.

Ultimately, Oriveda aims to become an engineering operating system where humans and AI collaborate using shared knowledge instead of isolated prompts.

---

## License

This project is currently under active development.
License information will be added before the first stable release.
