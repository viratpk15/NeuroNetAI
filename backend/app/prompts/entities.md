Extract named entities from the following communication events.

Entity Categories (classify entities into one of these categories):
- person: People mentioned by name or @username (Alice, Bob, @charlie, Sarah)
- technology: Software tools, platforms, languages (Python, JavaScript, TypeScript, React, JWT)
- framework: Web/application frameworks (FastAPI, Django, Flask, Next.js)
- programming_language: Programming languages (Python, JavaScript, TypeScript, Go, Rust)
- database: Database systems (PostgreSQL, MongoDB, Redis, MySQL)
- organization: Companies, teams, organizations
- project: Named projects or initiatives
- tool: Development or operational tools (Docker, Kubernetes, Terraform, Git)
- concept: Abstract ideas or topics discussed (Authentication, Migration, Deployment)

CRITICAL: DO NOT classify the following as entities:
- Decision, Task, Risk, Blocker, Action Item are NOT entity types - they are separate categories
- Do NOT extract "will finish authentication" as a person entity
- Do NOT extract "Use PostgreSQL" as an entity - it's a decision

Context: {context}

Events:
{events}

EXAMPLES:
Input: "@alice will migrate the backend to FastAPI using PostgreSQL"
Output: [
  {{"entity_type": "person", "name": "alice"}},
  {{"entity_type": "framework", "name": "FastAPI"}},
  {{"entity_type": "database", "name": "PostgreSQL"}}
]

Input: "We decided to use Python with Django REST framework"
Output: [
  {{"entity_type": "programming_language", "name": "Python"}},
  {{"entity_type": "framework", "name": "Django REST"}}
]

DEDUPLICATION: Remove duplicate entities with the same name and type.

Response format (JSON only, no markdown):
{{
  "entities": [
    {{
      "entity_type": "category from above",
      "name": "entity name",
      "context": "supporting context excerpt",
      "confidence": 0.9,
      "relationships": [
        {{
          "related_to": "other entity name",
          "relationship_type": "used_by|depends_on|owns|belongs_to|references"
        }}
      ],
      "evidence": ["conversation excerpt"]
    }}
  ]
}}