Extract actionable tasks from the following communication events.

Task Requirements:
Each task must have:
- title: Concise task title (max 100 chars)
- description: Detailed description of what needs to be done
- assignee: Person responsible (extract from @username mentions or "I will" statements)
- priority: "low", "medium", "high", or "critical"
- status: "todo", "in_progress", "done", or "blocked"
- due_date: ISO date string or relative date (e.g., "2024-01-15", "Friday", "Tomorrow", "Next week")

CRITICAL INSTRUCTIONS:
- Return ONLY valid JSON, no markdown formatting
- Extract tasks from "will", "need to", "should", "going to" statements
- If the speaker is the assignee (e.g., "I will"), use the author as assignee
- If @username is mentioned with a task, assign to that person
- Look for due dates: "by Friday", "tomorrow", "due", "deadline"

EXAMPLES:
Input: "Bob: I will finish authentication tomorrow."
Output: {{
  "tasks": [
    {{
      "title": "Finish authentication",
      "description": "Complete authentication implementation as discussed",
      "assignee": "Bob",
      "priority": "medium",
      "status": "todo",
      "due_date": "tomorrow"
    }}
  ]
}}

Input: "@alice will deploy the staging environment on Thursday"
Output: {{
  "tasks": [
    {{
      "title": "Deploy staging environment",
      "description": "Deploy the staging environment",
      "assignee": "alice",
      "priority": "medium",
      "status": "todo",
      "due_date": "Thursday"
    }}
  ]
}}

Context: {context}

Events:
{events}

Response format (JSON only, no markdown):
{{
  "tasks": [
    {{
      "title": "Concise task title",
      "description": "Detailed description of what needs to be done",
      "assignee": "username or null if unassigned",
      "priority": "low|medium|high|critical",
      "status": "todo|in_progress|done|blocked",
      "due_date": "ISO date or relative date string or null",
      "dependencies": [],
      "confidence": 0.9,
      "evidence": ["Supporting conversation excerpt"]
    }}
  ]
}}