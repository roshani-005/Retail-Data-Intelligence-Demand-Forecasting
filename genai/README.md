# Basic Generative AI Concept

The role asks for a basic understanding of Generative AI. This project demonstrates a controlled **natural-language-to-SQL** workflow rather than adding an unrelated chatbot.

## Flow

```text
Business Question
      ↓
LLM / GenAI layer
      ↓
SQL generated from database schema
      ↓
Read-only SQL validation
      ↓
PostgreSQL
      ↓
Result → business explanation
```

The repository contains a small offline demonstration in `text_to_sql.py`. It deliberately does not require an API key. A production implementation would replace the demo mapping with an LLM call while retaining the SQL validation boundary.

## Why this belongs in the project

It connects GenAI directly to the analytics workflow: a stakeholder can ask a business question without knowing SQL, while the system still controls which SQL is allowed to execute.
