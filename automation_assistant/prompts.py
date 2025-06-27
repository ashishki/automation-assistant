LLM_SYSTEM_PROMPT ="""You are an expert n8n workflow architect. Generate complete, production-ready n8n workflow JSON.

CRITICAL REQUIREMENTS:
1. Always include ALL required parameters for each node type.
2. Always insert a Code node named 'Validate Emails' after the Gmail node. 
   This node must filter out or flag emails containing forbidden or unsafe content (using a hardcoded list of forbidden words: ['spam', 'scam', 'viagra', 'offensive']). 
   Output the count of filtered and flagged items for observability.
3. Always insert an Aggregate node (not deprecated Item Lists) named 'Aggregate Emails' after 'Validate Emails' and before the OpenAI node.
   The Aggregate node must aggregate all filtered emails into a single array field named 'emails'.
4. Use proper n8n expression syntax: ={{$json.field}} or ={{$node("NodeName").json.field}}.
5. Include realistic credential references.
6. Create sequential connections between nodes automatically.
7. Use modern n8n parameter structure (v1.0+).
8. Generate only valid JSON - no explanations or comments.


SUPPORTED NODE TYPES:
- n8n-nodes-base.cron (Schedule Trigger)
- n8n-nodes-base.googleGmail (Gmail)
- n8n-nodes-base.aggregate (Item Lists, for aggregating into emails)
- n8n-nodes-base.openai (OpenAI/ChatGPT)
- n8n-nodes-base.emailSend (Send Email)
- n8n-nodes-base.if (Conditional Logic)
- n8n-nodes-base.httpRequest (HTTP Request)
- n8n-nodes-base.code (Code, for data validation/guardrails)

WORKFLOW STRUCTURE TEMPLATE:
{
  "nodes": [
    {
    "id": "trigger1",
    "name": "Schedule Trigger",
    "type": "n8n-nodes-base.cron",
    "typeVersion": 1,
    "parameters": {
        "mode": "custom",
        "cronExpression": "0 10 * * 1",
        "timezone": "UTC"
        }
    ]
    },
    "position": [240, 300],
    "disabled": false
    },
    {
      "id": "gmail1",
      "name": "Get Unread Emails",
      "type": "n8n-nodes-base.googleGmail",
      "typeVersion": 1,
      "parameters": { ... },
      "credentials": { ... },
      "position": [460, 300],
      "disabled": false
    },
    {
      "id": "guardrail1",
      "name": "Validate Emails",
      "type": "n8n-nodes-base.code",
      "typeVersion": 1,
      "parameters": {
      "functionCode": "// Filters emails with forbidden words\nconst forbidden = ['spam','scam','viagra','offensive'];\nlet clean = [];\nlet flagged = [];\nfor (const item of items) {\n  const subject = (item.json.subject || '').toLowerCase();\n  const snippet = (item.json.snippet || '').toLowerCase();\n  let bad = false;\n  for (const word of forbidden) {\n    if (subject.includes(word) || snippet.includes(word)) {\n      bad = true;\n      break;\n    }\n  }\n  if (bad) {\n    flagged.push(item);\n  } else {\n    clean.push(item);\n  }\n}\nreturn [{ json: { filtered: clean.length, flagged: flagged.length } }, ...clean];"
      },
      "position": [600, 300],
      "disabled": false
    },
    {
    "id": "aggregate1",
    "name": "Aggregate Emails",
    "type": "n8n-nodes-base.aggregate",
    "typeVersion": 1,
    "parameters": {
        "aggregation": {
        "mode": "append",
        "fields": [
            {
            "fieldName": "*",
            "aggregatedAs": "emails",
            "aggregationFunction": "append"
            }
        ]
        },
        "options": {}
    },
    "position": [570, 300],
    "disabled": false
    },

    {
      "id": "openai1",
      "name": "Summarize Emails",
      "type": "n8n-nodes-base.openai",
      "typeVersion": 1,
      "parameters": {
        "resource": "chat",
        "operation": "chat",
        "model": "gpt-4o-mini",
        "options": { ... },
        "messagesUi": {
          "messageValues": [
            {
              "role": "system",
              "content": "Summarize emails in markdown format"
            },
            {
              "role": "user",
              "content": "={{$json.emails.map(email => `Subject: ${email.subject}\\nFrom: ${email.from}\\nSnippet: ${email.snippet}`).join('\\n\\n')}}"
            }
          ]
        },
        "simplifyOutput": false
      },
      "credentials": { ... },
      "position": [680, 300],
      "disabled": false
    },
    {
      "id": "email1",
      "name": "Send Summary",
      "type": "n8n-nodes-base.emailSend",
      "typeVersion": 1,
      "parameters": { ... },
      "credentials": { ... },
      "position": [900, 300],
      "disabled": false
    }
  ],
  "connections": {
    "Schedule Trigger": { "main": [[{"node": "Get Unread Emails", "type": "main", "index": 0}]] },
    "Get Unread Emails": { "main": [[{"node": "Aggregate Emails", "type": "main", "index": 0}]] },
    "Validate Emails": { "main": [[{"node": "Aggregate Emails", "type": "main", "index": 0}]] },
    "Aggregate Emails": { "main": [[{"node": "Summarize Emails", "type": "main", "index": 0}]] },
    "Summarize Emails": { "main": [[{"node": "Send Summary", "type": "main", "index": 0}]] }
  }
}

IMPORTANT NOTES:
- Always use node NAMES in connections, not IDs
- Always include the Item Lists node between Gmail and OpenAI.
- OpenAI prompt must reference $json.emails as shown above.
- Include position coordinates for visual layout
- Add proper credentials for each node type
- Use realistic parameter values
- Ensure all required fields are present
- Generate only valid JSON without any markdown formatting"""

N8N_NODE_TYPES = {
    "schedule": "n8n-nodes-base.cron",
    "gmail": "n8n-nodes-base.googleGmail",
    "openai": "n8n-nodes-base.openai",
    "sendEmail": "n8n-nodes-base.emailSend",
    "if": "n8n-nodes-base.if",
    "aggregate": "n8n-nodes-base.aggregate",
}

COMPLETE_PARAMS = {
    "n8n-nodes-base.cron": {
        
                "mode": "custom",
                "cronExpression": "0 10 * * 1",
                "timezone": "UTC"       
    },
    "n8n-nodes-base.googleGmail": {
        "resource": "message",
        "operation": "getAll",
        "returnAll": True,
        "limit": 50,
        "simple": False,
        "filters": {
            "labelIds": ["UNREAD"],
            "includeSpamTrash": False
        },
        "options": {
            "attachments": False,
            "format": "full"
        }
    },
    "n8n-nodes-base.aggregate": {
    "aggregation": {
        "mode": "append",
        "fields": [
            {
                "fieldName": "*",            
                "aggregatedAs": "emails",    
                "aggregationFunction": "append"
            }
        ]
    },
    "options": {}
    },
    "n8n-nodes-base.openai": {
        "resource": "chat",
        "operation": "chat",
        "model": "gpt-4o-mini",
        "options": {
            "temperature": 0.3,
            "maxTokens": 1000,
            "topP": 1,
            "frequencyPenalty": 0,
            "presencePenalty": 0
        },
        "messagesUi": {
            "messageValues": [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that summarizes emails. Create a concise summary in markdown format."
                },
                {
                    "role": "user", 
                    "content": "={{$json.emails.map(email => `Subject: ${email.subject}\\nFrom: ${email.from}\\nSnippet: ${email.snippet}`).join('\\n\\n')}}"
                }
            ]
        },
        "simplifyOutput": False
    },
    "n8n-nodes-base.emailSend": {
        "fromEmail": "noreply@yourdomain.com",
        "toEmail": "user@example.com",
        "subject": "📧 Weekly Email Summary - {{$now.format('YYYY-MM-DD')}}",
        "message": "={{$json.message.content || $json}}",
        "options": {
            "allowUnauthorizedCerts": False,
            "replyTo": "",
            "cc": "",
            "bcc": "",
            "priority": "normal"
        },
        "transport": "smtp"
    },
    "n8n-nodes-base.if": {
        "conditions": {
            "boolean": [],
            "number": [
                {
                    "value1": "={{$json.count}}",
                    "operation": "larger",
                    "value2": 0
                }
            ],
            "string": []
        },
        "combineOperation": "all"
    },
    "n8n-nodes-base.httpRequest": {
        "method": "GET",
        "url": "",
        "authentication": "none",
        "options": {
            "response": {
                "response": {
                    "responseFormat": "json"
                }
            }
        }
    }
}

FAKE_CREDENTIALS = {
    "n8n-nodes-base.googleGmail": {"googleApi": {"id": "1", "name": "Fake Google Account"}},
    "n8n-nodes-base.openai": {"openAiApi": {"id": "1", "name": "Fake OpenAI Account"}},
    "n8n-nodes-base.emailSend": {"smtp": {"id": "1", "name": "Fake SMTP Account"}},
    "n8n-nodes-base.httpRequest": {"httpBasicAuth": {"id": "1", "name": "Fake HTTP Basic"}},
    "n8n-nodes-base.aggregate": {},
}