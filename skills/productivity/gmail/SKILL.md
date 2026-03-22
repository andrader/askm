---
name: gmail
description: >
  Automates cleaning up Gmail Promotions and Updates categories. 
  It fetches emails in batches, identifies unsubscribe methods (mailto or web links), 
  presents choices to the user, sends unsubscribe emails, tags them as 'unsubscribed', 
  archives them, and generates a final HTML report.
---

# Gmail Cleanup & Unsubscribe

This skill provides a structured workflow for cleaning up your Gmail inbox from recurring newsletters and promotional content using the `gws` CLI.

## Prerequisites

- **`gws` CLI**: Must be installed and authenticated (`gws auth login`).
- **`jq`**: Required for parsing JSON outputs.

## Workflow

The agent follows these steps to process emails:

### 1. Fetch & Analyze
The agent fetches a batch of emails (default 50) from either the `Promotions` or `Updates` category.

```bash
bash scripts/gmail_cleanup.sh get_promotions_emails 50
```

For each email, the agent fetches the `List-Unsubscribe` header to determine how to unsubscribe.

```bash
bash scripts/gmail_cleanup.sh fetch_unsubscribe_headers <ID>
```

### 2. User Selection
The agent presents a multi-select list to you using the `ask_user` tool, showing the sender and subject for each email that has an unsubscribe method.

### 3. Action execution
For each email you select:
- **Email Unsubscribe**: If a `mailto:` link is found, the agent sends an automated unsubscribe email.
- **Web Unsubscribe**: If an `http(s):` link is found, it's collected for the final report.
- **Label & Archive**: The message is tagged with the `unsubscribed` label and removed from the Inbox.

```bash
# Example labeling and archiving
bash scripts/gmail_cleanup.sh label_and_archive <ID>
```

### 4. Final Report
Once the batch is processed, the agent generates a summary report.

```bash
bash scripts/gmail_cleanup.sh generate_report '<RESULTS_JSON>'
```

The report `unsubscribe_report.html` will contain all actions taken and the links for any manual unsubscriptions that were needed.

## Scripts

- **`scripts/gmail_cleanup.sh`**: The main automation script containing all helper functions.

## Assets

- **`assets/report_template.html`**: The HTML template used for generating the final results report.
