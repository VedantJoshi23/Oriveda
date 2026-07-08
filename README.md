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

## Naming Convention

### Specifications

```text
OV-001 Discovery Report
OV-002 Product Analysis
OV-003 Feature Inventory
```

---

### Architecture Decision Records

```text
ADR-001
ADR-002
ADR-003
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

```text
PRM-IMPLEMENT
PRM-REVIEW
PRM-DISCOVERY
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
