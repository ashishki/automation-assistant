# 🦾 Automation Assistant: AI-Generated n8n Workflows

<div align="center">
  <img src="https://via.placeholder.com/150x150/FF6B35/FFFFFF?text=🦾" alt="Automation Assistant Logo" width="150"/>
  
  <p align="center">
    <strong>Transform natural language into production-ready n8n automation workflows</strong>
  </p>
  
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#quickstart">Quick Start</a> •
    <a href="#usage">Usage</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#contributing">Contributing</a>
  </p>
  
  <p align="center">
    <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version"/>
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"/>
    <img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="Build Status"/>
    <img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python"/>
    <img src="https://img.shields.io/badge/docker-ready-blue.svg" alt="Docker"/>
  </p>
</div>

---

## 🌟 Overview

This project is a containerized assistant for **generating, validating, and deploying n8n automation workflows** from simple natural language prompts. It leverages LLMs (OpenAI, etc.), enforces smart guardrails, and ships with a modern DevOps toolchain for enterprise-ready automation.

> **Example**: "Every Monday at 10:00 AM, send me a summary of unread Gmail emails." → Complete n8n workflow deployed and ready to run.

## 🚀 Features

- 🧠 **Natural Language to Workflow**  
  Transform plain English descriptions into fully functional n8n workflows with proper scheduling and integrations

- 🛡️ **Built-in Guardrails**  
  Email content moderation, forbidden content filtering, and customizable validation rules

- ⚙️ **Smart Parameter Generation**  
  Automatically generates correct, modern n8n parameters (v1+) with intelligent aggregation and validation

- 🔄 **Auto-Deploy to n8n**  
  Seamlessly communicates with your n8n server to upload and activate workflows

- 🔧 **Highly Extensible**  
  All prompt engineering and node configurations centralized in `promptspy.py` for easy business customization

- 🐳 **Full Containerization**  
  Complete Docker setup with docker-compose and CI/CD via GitHub Actions

- 📊 **Production Ready**  
  Comprehensive testing, monitoring, and deployment pipeline included

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Runtime** | Python 3.12 + Poetry | Core application and dependency management |
| **AI/ML** | OpenAI API (swappable) | Natural language processing and workflow generation |
| **Automation** | n8n (Docker) | Workflow execution platform |
| **Testing** | Pytest | Unit and integration testing |
| **Containerization** | Docker + Docker Compose | Service orchestration |
| **CI/CD** | GitHub Actions | Automated testing and deployment |

## 🏁 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key (or alternative LLM provider)
- n8n instance (can be local via Docker)

### 1. Clone & Configure

```bash
# Clone the repository
git clone https://github.com/your-org/automation-assistant.git
cd automation-assistant

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 2. Start Services

```bash
# Launch the complete stack
docker-compose up --build

# Services will be available at:
# - n8n: http://localhost:5678
# - Assistant: CLI container ready
```

### 3. Generate Your First Workflow

```bash
# Generate workflow from natural language
docker-compose run --rm \
  -e PROMPT="Every Monday at 10:00 AM, send me a summary of unread Gmail emails." \
  automation-assistant
```

**What happens:**
1. 🧠 Your prompt is processed by the LLM
2. ✅ Workflow is validated and optimized
3. 🚀 Ready workflow is deployed to n8n
4. 📋 Workflow ID and management links are provided

### 4. Run Tests

```bash
# Local development
poetry install
poetry run pytest

# Or via Docker
docker-compose run --rm automation-assistant pytest
```

## 💡 Usage Examples

### Basic Email Automation
```bash
PROMPT="Send me a daily digest of new GitHub issues at 9 AM"
```

### Multi-step Workflow
```bash
PROMPT="When a new customer signs up, add them to Mailchimp, create a Slack notification, and log to Google Sheets"
```

### Conditional Logic
```bash
PROMPT="Monitor RSS feed every hour, if new post contains 'AI' or 'automation', post to Twitter and send Telegram notification"
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Prompt   │───▶│  LLM Processing  │───▶│  n8n Workflow   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Guardrails &   │
                       │   Validation     │
                       └──────────────────┘
```

### Core Components

- **`prompts.py`** - Prompt engineering and node parameter configurations
- **`llm_parser.py`** - LLM integration and system prompt management
- **`workflow_builder.py`** - n8n node and connection logic
- **`guardrails.py`** - Content moderation and validation
- **`main.py`** - CLI entrypoint and orchestration

## 📁 Project Structure

```
automation-assistant/
├── automation_assistant/
│   ├── prompts.py          # 🧠 Prompt engineering & configs
│   ├── llm_parser.py       # 🤖 LLM integration
│   ├── workflow_builder.py # 🔧 n8n workflow construction
│   ├── guardrails.py       # 🛡️ Validation & moderation
│   └── main.py            # 🚀 CLI entrypoint
├── tests/                  # 🧪 Unit & integration tests
├── docker-compose.yml      # 🐳 Service orchestration
├── Dockerfile             # 📦 Container definition
├── .github/workflows/     # ⚙️ CI/CD pipelines
└── pyproject.toml         # 📋 Python dependencies
```

## 🧪 Testing & CI/CD

### Automated Testing
- **Unit Tests**: Individual component validation
- **Integration Tests**: End-to-end workflow generation
- **GitHub Actions**: Automated testing on every commit and PR

### Quality Assurance
```bash
# Run full test suite
poetry run pytest --cov=automation_assistant

# Lint and format
poetry run black .
poetry run flake8
```

## 🗺️ Roadmap

### ✅ Current (MVP)
- [x] Natural language → n8n workflow generation
- [x] Full containerization with Docker
- [x] Basic guardrails and validation
- [x] CI/CD with GitHub Actions

### 🚧 In Progress
- [ ] Extended node type support (Slack, Notion, Telegram, HTTP APIs)
- [ ] Advanced validation and error handling
- [ ] Performance optimization and caching

### 🔮 Future
- [ ] Multi-frontend support (Telegram bot, web dashboard)
- [ ] User/project management with persistence
- [ ] LLM orchestration with fallback logic
- [ ] Vector database integration for prompt retrieval
- [ ] Enterprise features (SSO, audit logs, advanced permissions)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors & Contributors

- **[Your Name]** - *Initial work* - [@yourusername](https://github.com/ashishki)
- **[Contributors]** - See [contributors](https://github.com/ashishki/automation-assistant/contributors)

## 🆘 Support

- 📚 [Documentation](https://docs.example.com)
- 🐛 [Report Bug](https://github.com/ashishki/automation-assistant/issues)
- 💡 [Request Feature](https://github.com/ashishki/automation-assistant/issues)
- 💬 [Discussions](https://github.com/ashishki/automation-assistant/discussions)

---

<div align="center">
  <p>Made with ❤️ by the Automation Assistant team</p>
  <p>
    <a href="https://github.com/ashishki/automation-assistant">⭐ Star us on GitHub</a> •
    <a href="https://twitter.com/yourhandle">🐦 Follow on Twitter</a>
  </p>
</div>