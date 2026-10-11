# Customer Reply Assistant Product Specification

## Purpose

Help customer service staff prepare consistent replies to common online-store questions using a predefined FAQ knowledge base. Northstar Demo Store is fictional; all prices, timelines, and policy rules are demonstration content.

## User and workflow

The first version serves one demo user without registration or login:

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

## Data

The JSON knowledge base contains 12 FAQs (`faq-101` through `faq-112`). Each contains `id`, `title`, `category`, `keywords`, and `answer`.

Topics: return policy, return process, refunds, exchanges, delivery time, shipping cost, tracking, cancellation, address changes, damage, incorrect items, and international delivery.

SQLite stores `id`, `question`, `reply`, nullable `faq_id`, and `created_at`. It does not store live orders, customer accounts, payment data, or a source-text snapshot. Original FAQ IDs must not be reused for unrelated content.

## Scope

The application suggests policy replies; it does not execute policy decisions. No automatic sending, email integration, refunds, order changes, live tracking, uploads, login, FAQ editor, history deletion, vector search, or external model calls are included.

The design uses a dark blue theme and English content. The FAQ matcher and API contract are shared across local and Docker runs.

## Completion gates

The application workflow is implemented and locally tested. Course completion additionally requires verified container execution, cloud deployment, a successful hosted CI run, deployment after passing checks, the agent extension pack, audit artifacts, reproducible deployment instructions, and peer reviews under the final course rules. See [the checklist](docs/submission-checklist.md).
