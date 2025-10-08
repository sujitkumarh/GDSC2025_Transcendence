# 🌱 Transcendence - Green Agents of Change 🤖

## 🚀 Overview
A sophisticated AI-powered assistant ecosystem that empowers Brazilian youth to explore green jobs and learning opportunities through multi-agent orchestration, persona analysis, and intelligent guidance. Transcendence combines advanced agent routing, empathetic conversation design, and real-world relevance to deliver personalized pathways toward sustainable careers aligned with UNICEF Green Rising initiatives.

## 🎯 Challenge Context
**2025 Capgemini Global Data Science Challenge (GDSC) - Green Agents of Change**

Physical and digital barriers prevent Brazilian youth (16-24) from accessing green job opportunities and sustainability training. Limited awareness, fragmented information, and mismatched readiness levels create gaps between aspiration and action. Transcendence bridges this gap with intelligent, context-aware guidance that meets youth where they are and guides them toward meaningful next steps.

## 🧠 Multi-Agent Architecture

### Core Guidance Agents
- **🎯 Router Agent**: Intelligent task identification and agent orchestration for personalized journey mapping
- **💼 Career Agent**: Green job family mapping, junior role discovery, and skill gap analysis
- **📚 Learning Agent**: Micro-course recommendations, certification pathways, and local program discovery
- **🛤️ Guidance Agent**: Actionable step sequencing, prerequisite planning, and resource optimization
- **🛡️ Safety Agent**: Content policy enforcement, bias mitigation, and ethical guardrails

### Advanced Intelligence Agents
- **👥 Persona Agent**: Real-time youth profile analysis and readiness assessment
- **✨ Response Refiner**: Empathetic language optimization and pt-BR localization
- **📊 Analytics Agent**: Interaction tracking, recommendation effectiveness, and engagement metrics

## 🔧 Advanced Tech Stack

### Frontend & User Interface
- **Framework**: React 18 + TypeScript with Vite for lightning-fast development
- **State Management**: Zustand for lightweight, intuitive state orchestration
- **Interface**: Responsive PWA design optimized for mobile-first Brazilian youth
- **Charts**: Recharts for interactive analytics visualization
- **Styling**: Tailwind CSS for rapid, accessible UI development

### Backend & AI Infrastructure  
- **API Framework**: FastAPI with async/await support and automatic OpenAPI documentation
- **AI Models**: AWS Mistral AI integration with fallback mock mode for offline development
- **Agent Framework**: Custom lightweight orchestrator inspired by Project B patterns
- **Analytics**: Real-time persona analysis and recommendation tracking
- **Caching**: LRU cache for prompt responses and embeddings optimization

### Data & Storage
- **Personas**: JSON-based profiles with Brazilian demographic and interest attributes
- **Green Jobs**: CSV-based catalog with location, prerequisites, and growth potential
- **Learning Content**: Structured training database with cost, duration, and accessibility metadata
- **Analytics**: TinyDB for lightweight local storage with SQLite upgrade path
- **Internationalization**: English defaults with pt-BR toggle support

### AWS Integration & Cost Optimization
- **Provider**: AWS Mistral AI with environment-driven configuration
- **Caching**: Aggressive prompt reuse and response caching
- **Mock Mode**: Complete offline functionality for development and demos
- **Token Management**: Short context windows and extractive answering

## 🚀 Quick Start (3 Simple Steps)

### Prerequisites
- **Python**: 3.11+ with pip
- **Node.js**: 18+ with npm
- **Git**: For repository cloning

### Installation & Launch

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd GDSC2025_Transcendence
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Application**
   ```bash
   python main.py
   ```

That's it! The application will automatically:
- ✅ Check prerequisites (Node.js, npm)
- ✅ Create environment files
- ✅ Install frontend dependencies
- ✅ Start backend server on port 8000
- ✅ Start frontend server on port 5173

### Access Points
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Stop Application
Press `Ctrl+C` in the terminal to stop both servers.

---

## 🔧 Advanced Configuration (Optional)

## ⚙️ Configuration

### Environment Variables

**Backend (.env)**
```bash
# AWS Mistral Configuration
AWS_REGION=us-east-1
AWS_MISTRAL_MODEL=mistral.mistral-7b-instruct-v0:2
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_SESSION_TOKEN=optional_session_token

# Development Settings
MOCK_MODE=true
DEBUG=true
LOG_LEVEL=INFO
TELEMETRY_ENABLED=true

# Server Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173
```

**Frontend (.env)**
```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_DEFAULT_LANGUAGE=en
VITE_ENABLE_ANALYTICS=true
VITE_MOCK_MODE=true
```

### Feature Flags
- **Mock Mode**: Disable AWS calls for offline development
- **Analytics**: Toggle interaction tracking and metrics
- **Language**: Switch between English and pt-BR interfaces
- **Debug Mode**: Enhanced logging and error details

## 📊 Data & Personas

### Persona Attributes
Brazilian youth profiles include:
- **Demographics**: Age (16-24), location (states/regions), education level
- **Digital Access**: Device types, internet connectivity, tech comfort
- **Interests**: Green domains (solar, wind, waste management, sustainable agriculture, EVs, forestry, ESG)
- **Readiness**: Skill level, time availability, financial constraints
- **Goals**: Career exploration, immediate employment, skill development, awareness building

### Dataset Management
- **Location**: `backend/app/data/`
- **Format**: JSON files with CSV imports for bulk data
- **Editing**: Admin UI for persona creation and dataset updates
- **Sources**: All datasets include citation fields and licensing notes

## 🤖 Agent System

### Architecture Summary
Lightweight in-process orchestration inspired by Project B patterns:
- **Request Routing**: Intelligent agent selection based on user intent
- **Context Sharing**: Shared persona and conversation state across agents
- **Response Synthesis**: Multi-agent input combination with conflict resolution
- **Safety Layers**: Content filtering and bias detection at multiple levels

### Prompt Templates
Located in `docs/prompts.md` with examples:
- **System Prompts**: Agent personality and behavior guidelines
- **Few-Shot Examples**: Empathetic pt-BR interactions
- **Safety Guidelines**: Bias mitigation and inclusive language patterns
- **Context Templates**: Persona integration and cultural sensitivity

## 📈 Analytics & Monitoring

### Dashboard Views
- **Interaction Funnel**: Persona creation → Assistant engagement → Recommendation acceptance
- **Interest Analysis**: Popular green job categories and regional preferences
- **Recommendation Effectiveness**: Click-through and completion rates
- **Language Preferences**: pt-BR adoption and satisfaction metrics

### API Endpoints
- `GET /v1/analytics/summary` - Overview KPIs and trends
- `GET /v1/analytics/persona/{id}` - Individual persona journey analysis
- `GET /v1/analytics/events` - Paginated interaction logs
- `GET /v1/analytics/recommendations` - Recommendation performance metrics

## 💰 Cost Optimization

### Token Management
- **Prompt Compression**: Few-shot optimization and context summarization
- **Response Caching**: LRU cache for repeated queries and embeddings
- **Extractive Answering**: Prefer information extraction over generation
- **Batch Processing**: Group similar requests to reduce API calls

### Development Strategies
- **Mock Mode**: Complete offline functionality for development
- **Graceful Degradation**: Fallback responses when APIs are unavailable
- **Minimal Dependencies**: Lightweight libraries and pinned versions
- **Local Storage**: JSON/TinyDB for development, SQLite for production readiness

## 🧪 Testing

### Backend Tests
```powershell
cd tests/backend
python -m pytest test_agents.py -v
python -m pytest test_services.py -v
python -m pytest test_recommendations.py -v
```

### Frontend Tests
```powershell
cd tests/frontend
npm test
npm run test:coverage
```

### Integration Tests
```powershell
# Full system test with mock mode
.\scripts\test-integration.ps1
```

## 📋 Limitations (POC Scope)

### Current Scope
- **Deployment**: Localhost only, no containerization
- **Data**: File-based storage, limited scalability
- **Security**: Basic rate limiting, development-grade auth
- **Internationalization**: English + pt-BR only
- **Analytics**: Local storage, no cloud aggregation

### Known Constraints
- **Offline Assumptions**: Limited real-time data integration
- **Mock Dependencies**: AWS Mistral requires manual configuration
- **Windows Focus**: PowerShell scripts prioritized over cross-platform
- **POC Performance**: Not optimized for production load

## 🗺️ Roadmap & Production Expansion

| Area | Prototype (this repo) | Production Expansion |
|------|----------------------|---------------------|
| **Deploy** | Localhost, no Docker | CI/CD pipelines, IaC (Terraform), managed container runtimes |
| **Data** | JSON/TinyDB local | Managed PostgreSQL, automated backups, CDC pipelines |
| **LLM** | AWS Mistral mock/real | Central prompt management, evaluation harness, token budgeting |
| **Agents** | In-process, minimal | Orchestrator with queues, distributed tracing, fault tolerance |
| **Analytics** | File/SQLite | Data warehouse + BI tools, event schema, privacy controls |
| **Security** | .env, basic rate limit | Secrets manager, OAuth/SAML, audit trails, DLP policies |
| **i18n** | en + pt-BR | Full localization pipeline, content operations, regional adaptation |
| **Observability** | Console + basic logs | Metrics dashboards, distributed tracing, intelligent alerting |
| **Content** | Seed datasets | Curated content sources, periodic refresh jobs, quality scoring |
| **Infrastructure** | Local development | Auto-scaling, load balancing, disaster recovery, multi-region |
| **Compliance** | Development-grade | LGPD/GDPR compliance, data residency, audit frameworks |
| **Integration** | Mock external APIs | Real-time job boards, training providers, government databases |

## 📝 Generated Files Summary

This repository includes:

### Core Infrastructure
- ✅ **README.md** - Complete project documentation with production roadmap
- ✅ **LICENSE** - MIT license for open development
- ✅ **.env.example** - Environment template with AWS Mistral placeholders
- ✅ **.gitignore** - Comprehensive ignore patterns for Python/Node.js

### Setup Scripts
- ✅ **scripts/setup.ps1** - Windows PowerShell automated setup
- ✅ **scripts/setup.sh** - Cross-platform bash setup alternative
- ✅ **scripts/seed.ps1** - Data population for Windows
- ✅ **scripts/seed.sh** - Data population for Unix systems

### Backend API (FastAPI)
- ✅ **main.py** - Application entry point with CORS and routing
- ✅ **settings.py** - Environment-driven configuration management
- ✅ **requirements.txt** - Minimal, pinned Python dependencies
- ✅ **app/api/** - v1 REST endpoints for personas, assistance, analytics
- ✅ **app/agents/** - Agent definitions, routing, and prompt templates
- ✅ **app/models/** - Pydantic schemas for all data structures
- ✅ **app/services/** - AWS Mistral client, ranking engine, persistence
- ✅ **app/data/** - Seed JSON files for personas, jobs, training, content

### Frontend App (React + Vite)
- ✅ **package.json** - Dependencies and build scripts
- ✅ **vite.config.ts** - Vite configuration with proxy setup
- ✅ **tsconfig.json** - TypeScript configuration
- ✅ **index.html** - Application entry point
- ✅ **src/pages/** - Home, Personas, Assistant, Analytics, Admin views
- ✅ **src/components/** - Reusable UI components and charts
- ✅ **src/store/** - Zustand state management
- ✅ **src/services/** - API client and WebSocket integration

### Documentation
- ✅ **docs/architecture.md** - System design with Mermaid diagrams
- ✅ **docs/personas.md** - Brazilian youth persona definitions
- ✅ **docs/prompts.md** - Agent prompts and empathetic examples
- ✅ **docs/datasets.md** - Data sources and licensing information

### Testing Suite
- ✅ **tests/backend/** - Agent and service unit tests
- ✅ **tests/frontend/** - Component and integration tests
- ✅ **pytest.ini** - Test configuration and coverage settings

## 🎯 Next Steps

### Immediate Actions
1. **Configure AWS Credentials**: Update `backend/.env` with your Mistral AI access keys
2. **Run Setup Scripts**: Execute `.\scripts\setup.ps1` for automated installation
3. **Explore Personas**: Navigate to http://localhost:5173/personas to see Brazilian youth profiles
4. **Test Assistant**: Engage with the green jobs guidance system
5. **Review Analytics**: Monitor interaction patterns and recommendation effectiveness

### Development Workflow
1. **Backend Changes**: Modify agents and APIs, tests auto-reload with FastAPI
2. **Frontend Updates**: Component changes hot-reload with Vite dev server
3. **Data Updates**: Edit JSON files in `backend/app/data/` and restart services
4. **New Features**: Follow Project B patterns for consistency and maintainability

### Production Preparation
1. **Security Hardening**: Implement proper authentication and secrets management
2. **Performance Optimization**: Add caching layers and database optimization
3. **Monitoring Integration**: Connect to APM tools and logging aggregation
4. **Content Expansion**: Integrate real Brazilian green job and training APIs
5. **User Testing**: Conduct accessibility and usability validation with target demographics

---

**Built with 💚 for Brazilian Youth and Green Future Careers**  
*Empowering the next generation of environmental changemakers through AI-guided pathways*