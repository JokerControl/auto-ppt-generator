# AutoPPT Generator - Backend API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "api_key_configured": true
}
```

---

### 2. Generate PPT Outline
**POST** `/api/ppt/outline`

Generate a PPT outline without creating the file.

**Request Body:**
```json
{
  "topic": "人工智能在教育中的应用",
  "pages": 10,
  "language": "zh",
  "theme": "education"
}
```

**Response:**
```json
{
  "topic": "人工智能在教育中的应用",
  "total_pages": 10,
  "outline": [
    {
      "page_num": 1,
      "title": "标题",
      "content": "内容描述",
      "bullets": ["要点1", "要点2", "要点3"]
    }
  ],
  "theme": "education",
  "language": "zh"
}
```

---

### 3. Generate PPT (Async)
**POST** `/api/ppt/generate`

Generate PPT file asynchronously.

**Request Body:**
```json
{
  "topic": "人工智能在教育中的应用",
  "description": "包括AI辅导、个性化学习、智能评估等方面",
  "pages": 15,
  "theme": "education",
  "language": "zh"
}
```

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "pending",
  "message": "PPT generation started. Use task_id to check status."
}
```

---

### 4. Check Task Status
**GET** `/api/ppt/task/{task_id}`

Check the status of a PPT generation task.

**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "message": "PPT generated successfully!",
  "file_url": "/api/ppt/download/ppt_uuid.pptx",
  "created_at": "2024-01-01T00:00:00",
  "completed_at": "2024-01-01T00:01:00"
}
```

---

### 5. Download PPT
**GET** `/api/ppt/download/{filename}`

Download the generated PPT file.

---

### 6. List Tasks
**GET** `/api/ppt/tasks`

List all generation tasks.

**Response:**
```json
{
  "total": 10,
  "tasks": [
    {
      "task_id": "uuid-string",
      "topic": "主题",
      "status": "completed",
      "created_at": "2024-01-01T00:00:00",
      "completed_at": "2024-01-01T00:01:00"
    }
  ]
}
```

---

### 7. Execute MCP Skill
**POST** `/api/ppt/mcp/execute`

Execute an MCP skill.

**Request Body:**
```json
{
  "skill_name": "ppt.optimize",
  "parameters": {
    "outline": [...],
    "max_bullets_per_slide": 6
  }
}
```

---

### 8. List MCP Skills
**GET** `/api/ppt/mcp/skills`

List available MCP skills.

---

## MCP Skills

| Skill Name | Description |
|------------|-------------|
| `ppt.structure` | Analyze and validate PPT structure |
| `ppt.content` | Generate detailed content for PPT pages |
| `ppt.design` | Apply design templates and themes |
| `ppt.export` | Process export formats and options |
| `ppt.validate` | Validate PPT file and content |
| `ppt.optimize` | Optimize content for better presentation |

---

## Error Responses

**400 Bad Request**
```json
{
  "detail": "Error message here"
}
```

**404 Not Found**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error"
}
```

**503 Service Unavailable**
```json
{
  "detail": "MiniMax API key not configured"
}
```
