Extract actionable tasks from the following communication events.

Identify who is responsible for each task, infer priority, status, and provide supporting evidence.

Context: {context}

Events:
{events}

Response format (JSON):
{
  "tasks": [
    {
      "title": "Concise task title",
      "description": "Detailed description of what needs to be done",
      "assignee": "@username or null if unassigned",
      "priority": "low|medium|high|critical",
      "status": "todo|in_progress|done|blocked",
      "due_date": "ISO date string or null",
      "dependencies": ["other task title if dependent"],
      "confidence": 0.0-1.0,
      "evidence": ["Supporting conversation excerpt"]
    }
  ]
}