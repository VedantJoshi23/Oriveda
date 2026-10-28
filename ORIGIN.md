# I Asked for a Website Prompt and Accidentally Designed an Engineering Methodology

*The origin story of [Oriveda](https://github.com/VedantJoshi23/Oriveda).*

---

It started with a shopping list.

I wanted to build a production-grade jewelry e-commerce website, and I did what everyone does now: I opened a chat with an AI and asked it to generate me a prompt. Not a small one — I listed thirteen infrastructure layers I wanted covered (frontend foundations, auth, caching, load balancing, error tracking, disaster recovery, the works) and asked for "a robust prompt to an absolute completeness" that I could hand to any coding agent.

I also told it to ask me up to seven clarifying questions first. That instruction turned out to matter more than the whole list above it.

## The seven questions

The questions forced decisions I hadn't actually made yet: Was this a demo or a real business? How much engineering rigor did I want? Should the AI behave like a code generator, a senior engineer, or a principal engineer responsible for the system's long-term health?

I chose: real business, production-grade without enterprise ceremony, milestone-driven delivery, and a modular monolith with boundaries clean enough to evolve into microservices later without paying the microservices tax on day one.

Answering those questions took longer than writing my original request. It was the first hint that the prompt wasn't the hard part. *Knowing what I wanted* was the hard part, and no amount of prompt engineering substitutes for it.

## The crack in the plan

Then the AI said something that broke my original framing: one massive prompt can't work.

Not because of context limits — because of *change rates*. My engineering philosophy should almost never change. My architecture should change rarely. My coding standards occasionally. My feature specs constantly. Jamming all of that into one prompt means every small change forces you to regenerate everything, and nothing is stable enough to build on.

So the prompt split into layers, and the bottom layer got a name that stuck: the **Engineering Constitution** — a small set of immutable laws that every future decision must satisfy. And here's the thing I only saw in hindsight: the moment a prompt is layered, versioned, and stable enough to build on, **it isn't a prompt anymore. It's documentation.** Not documentation as historical record — documentation as the executable source of truth. If the code and the spec disagree, the code is wrong.

The deeper realization was that software projects don't fail because teams lack code generators. They fail because knowledge is fragmented, assumptions are invisible, and decisions lose their rationale over time. AI just made the problem easier to see.

## Getting a name

For a while the framework was called Oracle. Then I renamed it **Oriveda**: *Ori* from the Orion constellation — humanity's oldest navigation aid, guided vision — and *Veda* from the Vedas — foundational knowledge. Guided vision plus foundational knowledge. The motto followed: **"Engineering the Future, Deliberately."**

The name ended up fitting the idea better than the project it came from. Oriveda wasn't about generating software. It was about navigating uncertainty using knowledge that could be trusted.

## The idea that made it different

The last idea of the conversation is the one I now think matters most.

Every spec-driven AI workflow I'd seen assumes you start from a clean requirements document. Real projects don't look like that. You inherit a half-documented repo, a Figma file, some screenshots, a competitor you're chasing, and someone's memory of what was agreed. The interesting question isn't "what should we build?" — it's "**what do we actually know, and how do we know it?**"

So Oriveda starts with **evidence**. Every piece of extracted knowledge becomes an atomic claim carrying a confidence score and a citation to its source:

- *"Orders have a status field — 99% confidence, observed in source code."*
- *"A wishlist feature exists — 70% confidence, inferred from a screenshot."*

Facts, inferences, and assumptions are labeled as such, and the agent is forbidden from treating an assumption as settled. Better yet, it stops asking generic discovery questions. It asks only for the *specific missing evidence that would materially raise confidence* — "the largest remaining uncertainty is your order-fulfillment rules; a single admin screenshot or workflow diagram would resolve it." That's how a senior engineer joins an existing project. That's what I wanted from an AI.

Traditional documentation asks teams to write down what they know. Oriveda asks a more fundamental question: *how do you know it?* A requirement without provenance is just a claim. Once every claim carries evidence, confidence, and traceability, disagreement becomes measurable instead of political.

Most AI coding assistants start with code. Most documentation systems start with requirements. **Oriveda starts with evidence.**

## The lens

Once we had evidence as the foundation, one test became the lens for every decision that followed:

> *If this project grows to 100 engineers and 10 million users, would this decision still make sense? If not, why is it acceptable today?*

It's not a demand that everything scale. It's a demand that every shortcut be *intentional* — and, now, *documented against evidence*. "We're doing the simple thing because we're small, and here's what we'll change when that stops being true" is a fine answer. Silence is not.

## Where it stands

What began as one chat eventually became a framework of versioned protocols governing knowledge acquisition, architecture, standards, domain knowledge, feature specifications, and prompt orchestration — all validated for consistency and drift. The details evolved, but the principle stayed the same: every decision should be traceable back to evidence.

Humans and AI agents read the same specifications, and nothing important lives only in a chat transcript. Which is a kind of poetic justice, because this whole thing *started* as a chat transcript, and the first thing I did was refuse to let the knowledge in it evaporate.

The funny part is that the jewelry website still exists. It was supposed to be the project. Instead, it became the first test case.

I started by asking an AI for a prompt. I ended up building a system for ensuring that neither humans nor AI ever have to start from scratch again.

---

*Oriveda is open source and under active development — the [Quickstart](README.md#quickstart) takes one prompt. Bring whatever evidence you have: a repo, a PRD, screenshots, or nothing but an idea.*
