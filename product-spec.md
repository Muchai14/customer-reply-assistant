# Customer Reply Assistant Product Specification

## Purpose

Help customer service staff prepare consistent replies to common online-store questions using a predefined FAQ knowledge base. The agreed scenario is a fictional watch and accessories store, retaining the existing Northstar Demo Store name. All timelines and policy rules are demonstration content; no company or customer information is used.

## Agreed simplified version

The following decisions were confirmed during the product brainstorming:

- Adapt the existing app rather than start a separate project.
- Assist customer service staff with drafts; staff review them and can copy them into their usual support channel. The app does not send messages to customers.
- Use English for the interface, policies, and replies, and retain the dark blue theme.
- Use a form with a question field, draft editor, source policy, and saved-reply history instead of chat bubbles.
- Generate drafts with free keyword matching and templates. No language-model service or paid AI API is required. The frontend still communicates with the backend through the app's own API.
- Display the matching policy so staff can check the source before using the draft.
- Allow staff to edit and explicitly save replies for future reference.
- When nothing matches, explain that no matching policy was found and allow a manual reply; do not invent an answer.
- Limit the simplified knowledge base to the five policies listed below.

**Implementation status:** These are the agreed requirements for the next simplification. This document update does not change the running app. The current implementation still has 12 FAQs; reducing it to five and updating related UI copy and tests remain to be done.

## User and workflow

The first version is a staff-facing demo without registration or login. On the hosted site, users share the same history; enter fictional content only:

**Enter question → Match FAQ → Review source and draft → Edit → Save → View history**

Example: “What is your return policy?” matches `faq-101`. The application displays the full policy and a template-based draft. The reviewer decides whether the answer applies and edits it before saving.

## Functional acceptance criteria

| Feature | Expected behavior |
| --- | --- |
| Question input | Trim surrounding whitespace; accept 1–1,000 characters; reject blank or oversized input |
| Matching | Normalize case and punctuation; match contiguous whole-word keyword phrases |
| Ranking | Score by longest matched phrase in words; resolve ties by ascending FAQ ID |
| Draft | Display `Hello, ` followed by the matched FAQ answer, plus the source title and original answer |
| No match | Display an explanation, an empty draft, and no source; allow a manual reply |
| Editing | Permit reviewer changes; changing the question requires a new lookup before saving |
| Saving | Explicit click stores trimmed question, final reply, source ID or null, generated ID, and UTC timestamp |
| Validation | Reject blank or over-5,000-character replies and unknown FAQ IDs |
| History | Display newest records first, break timestamp ties by descending ID, and allow record details |
| Pagination | API defaults to 20 records, maximum 100; frontend displays five per page |
| Persistence | Saved replies remain after app restart |
| Error handling | Explain failed requests and preserve typed content after save failure |
| Duplicate handling | Disable saving an identical unchanged reply again in the UI; edits create a new record |
| Accessibility | Labeled controls, keyboard focus indicators, live status messages, responsive layout |

## Five-policy scope

| Policy | Existing ID to preserve | What the reply explains |
| --- | --- | --- |
| Return eligibility | `faq-101` | Fictional return conditions and exclusions |
| How to return an item | `faq-102` | Steps for requesting a return |
| Refund timing | `faq-103` | General policy timing, without claiming a refund was issued |
| Delivery timing | `faq-105` | General delivery estimates, without checking an actual order |
| Tracking instructions | `faq-107` | How a customer can find tracking information, without live tracking lookup |

Product recommendations, watch specifications, exchanges, and the other existing FAQ topics are outside the agreed simplified version. Do not renumber the retained FAQs or reuse removed IDs for different policies. Existing saved records must be preserved when implementing the smaller dataset.

## Data and saved replies

The current JSON knowledge base contains 12 FAQs (`faq-101` through `faq-112`). The target is the five retained policies above. Each FAQ contains `id`, `title`, `category`, `keywords`, and `answer`.

SQLite locally and Neon PostgreSQL online store `id`, `question`, `reply`, nullable `faq_id`, and `created_at`. Saving creates a history record for later reference; generating a draft alone does not save anything. The app does not store live orders, customer accounts, payment data, or a source-text snapshot.

Saved replies are not automatically verified or used to generate new drafts. Future AI-agent retrieval or evaluation could use carefully reviewed records, but that is outside this version and would require approval labels, policy-version tracking, and appropriate privacy controls.

## Scope

The application suggests policy replies; it does not execute policy decisions. No automatic sending, email integration, refunds, order changes, live tracking, uploads, login, FAQ editor, history deletion, vector search, or external model calls are included.

The design uses a dark blue theme and English content. The FAQ matcher and API contract are shared across local and Docker runs.

## Completion gates

The application workflow is implemented and locally tested. Course completion additionally requires verified container execution, cloud deployment, a successful hosted CI run, deployment after passing checks, the agent extension pack, audit artifacts, reproducible deployment instructions, and peer reviews under the final course rules. See [the checklist](docs/submission-checklist.md).
