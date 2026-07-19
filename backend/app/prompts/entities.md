Extract named entities from the following communication events.

Entity types to extract:
- person: People mentioned (@username or names)
- technology: Technologies, languages, tools (Python, FastAPI, React, etc.)
- framework: Frameworks (FastAPI, Django, Next.js, etc.)
- library: Libraries (pydantic, langchain, etc.)
- repository: Repository names (owner/repo or github.com/owner/repo)
- api: API endpoints (/v1/users, /api/auth)
- database: Databases (PostgreSQL, MongoDB, Redis)
- service: Services (auth-service, payment-api)
- organization: Organizations (companies, teams)
- deadline: Deadlines, dates, milestones
- component: Components, modules (AuthModule, UserComponent)
- branch: Git branches (main, develop, feature/xyz)
- issue: GitHub issues (#123 or issue references)
- pull_request: PRs (PR #456 or pull request references)

Context: {context}

Events:
{events}

Response format (JSON):
{
  "entities": [
    {
      "entity_type": "type from above",
      "name": "entity name",
      "context": "supporting context excerpt",
      "confidence": 0.0-1.0,
      "relationships": [
        {
          "related_to": "other entity name",
          "relationship_type": "used_by|depends_on|owns|belongs_to|references"
        }
      ],
      "evidence": ["conversation excerpt"]
    }
  ]
}