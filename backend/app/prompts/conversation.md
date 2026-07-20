Analyze the following communication events and provide a concise executive summary.

Context: {context}

Events:
{events}

CRITICAL INSTRUCTIONS:
- Return ONLY valid JSON, no markdown formatting
- Do NOT include "Unknown:" prefixes in your summary
- Write a natural, flowing summary in 1-2 sentences (max 100 words)
- Do NOT simply concatenate message content
- Focus on the KEY DISCUSSION POINTS and OUTCOMES

ENTITY DEFINITIONS (DO NOT extract decisions/tasks/risks as entities):
- Person: A named individual (Alice, Bob, etc.) or @username mention
- Technology: Software tools, platforms, languages (FastAPI, JWT, PostgreSQL, Python)
- Framework: Web/application frameworks (FastAPI, Django, Next.js)
- Programming Language: Languages (Python, JavaScript, TypeScript, Go)
- Database: Database systems (PostgreSQL, MongoDB, Redis)
- Organization: Companies, teams, departments
- Project: Named projects or initiatives
- Tool: Development or operational tools (Docker, Kubernetes, Terraform)
- Concept: Abstract ideas or topics discussed (Authentication, Deployment, Migration)

DECISION DEFINITIONS:
- Extract ONLY actual engineering/architecture decisions
- Examples: "Use PostgreSQL for production", "Deploy on AWS", "Adopt FastAPI"
- DO NOT extract action items or tasks as decisions
- DO NOT extract "will do X" statements as decisions

RISK DEFINITIONS:
- Extract potential risks or blockers explicitly mentioned
- Examples: "Authentication testing pending", "Deployment review pending"
- Look for words like: pending, blocked, concern, risk, issue, might fail

TASK DEFINITIONS (for reference):
- Actionable items with clear ownership
- Examples: "Finish authentication", "Deploy staging"

Response format (JSON only, no markdown):
{{
  "summary": "Natural summary of the meeting in 1-2 sentences, max 100 words. Example: 'A team meeting discussed backend migration to FastAPI, authentication progress, deployment planning, and production database decisions.'",
  "topics": ["backend", "authentication", "deployment"],
  "decisions": ["Use PostgreSQL for production"],
  "risks": ["Authentication testing pending"],
  "blockers": ["None identified"],
  "action_items": ["Finish authentication", "Deploy staging on Thursday"]
}}