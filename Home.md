# Welcome to the Recaller Wiki

**Recaller** is a privacy-first, open-source personal assistant application designed to help you manage your finances, communications, social activities, belongings, and recurring payments—all powered by on-device/self-hosted AI.

## 📚 Documentation Overview

### Getting Started
- [Installation Guide](Installation-Guide) - Setup and deployment instructions
- [Quick Start Tutorial](Quick-Start-Tutorial) - Get up and running in minutes
- [Development Environment](Development-Environment) - Local development setup

### Architecture & Design
- [System Architecture](System-Architecture) - High-level system design
- [Database Schema](Database-Schema) - Data models and relationships
- [API Documentation](API-Documentation) - REST API endpoints and usage
- [MCP Integration Guide](MCP-Integration-Guide) - LLM integration via Model Context Protocol

### Features & Modules
- [Financial Management System](Financial-Management-System) - Complete financial tracking solution
- [Task Management](Task-Management) - Task and reminder system
- [Contact Management](Contact-Management) - Personal and professional contacts
- [Analytics System](Analytics-System) - Insights and reporting
- [MCP Integration Guide](MCP-Integration-Guide) - LLM integration and AI features

### Development
- [Contributing Guidelines](Contributing-Guidelines) - How to contribute to the project
- [Code Standards](Code-Standards) - Coding conventions and best practices
- [Testing Guide](Testing-Guide) - Testing strategies and implementation
- [Deployment Guide](Deployment-Guide) - Production deployment instructions

### Advanced Topics
- [Multi-Tenant Architecture](Multi-Tenant-Architecture) - Tenant isolation and management
- [Background Tasks](Background-Tasks) - Automated processing and notifications
- [Security & Privacy](Security-Privacy) - Data protection and privacy features
- [Performance Optimization](Performance-Optimization) - Scaling and optimization
- [MCP Integration Guide](MCP-Integration-Guide) - LLM integration and configuration

## 🚀 Key Features

### Financial Management
- **Transaction Tracking**: Credit/debit transactions with categorization
- **Recurring Payments**: Automated EMIs, salary, and subscription management
- **Budget Management**: Spending limits and alerts
- **Multi-Currency Support**: International transaction handling
- **Financial Analytics**: Insights and reporting

### Personal Assistant
- **Task Management**: To-dos, reminders, and recurring tasks
- **Contact Management**: Personal and professional relationships
- **Event Tracking**: Social activities and appointments
- **Belongings Management**: Inventory and asset tracking
- **AI Integration**: LLM-powered assistance via MCP server

### Privacy & Security
- **On-Device AI**: No data sent to third-party services
- **Self-Hosted**: Complete control over your data
- **Multi-Tenant**: Secure isolation for organizations
- **Open Source**: Transparent and extensible
- **MCP Protocol**: Standardized LLM integration with privacy-first design

## 🏗️ Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for session and task management
- **Background Tasks**: Celery for automated processing
- **Authentication**: JWT-based with multi-tenant support

### Frontend
- **Framework**: React 19+ with TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Headless UI, Heroicons
- **HTTP Client**: Axios with interceptors
- **State Management**: React Context and hooks

### Infrastructure
- **Containerization**: Docker and Docker Compose
- **Database Migrations**: Alembic
- **API Documentation**: OpenAPI/Swagger
- **Background Processing**: Celery + Redis
- **Email Notifications**: SMTP integration
- **MCP Server**: Model Context Protocol for LLM integration

## 📈 Recent Updates

### MCP Server Integration (August 2025)
- **Model Context Protocol**: Standardized LLM integration with MCP v1 compliance
- **Multi-Backend Support**: Ollama, HuggingFace, OpenAI-compatible APIs
- **Privacy-First AI**: On-device processing with zero external data sharing
- **Tenant Isolation**: Complete model access control per tenant
- **Extensible Architecture**: Plugin-based system for custom backends

### Financial Transactions Management System (August 2025)
- Complete financial management module with 6 database tables
- Advanced transaction categorization and subcategorization
- Automated recurring transaction processing
- Budget tracking with alerts and notifications
- Multi-currency support and analytics
- Email reminders for upcoming payments

### Multi-Tenant Architecture
- Tenant-based data isolation
- User access control within tenants
- API-level tenant filtering
- Background task tenant isolation

## 🤝 Community & Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/Nexlified/Recaller/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/Nexlified/Recaller/discussions)
- **Contributing**: See our [Contributing Guidelines](Contributing-Guidelines)
- **License**: AGPLv3 - Open source and community-driven

## 🔗 Quick Links

- [Project Repository](https://github.com/Nexlified/Recaller)
- [Live Demo](https://demo.recaller.app) *(coming soon)*
- [API Documentation](https://api.recaller.app/docs) *(coming soon)*
- [Community Chat](https://discord.gg/recaller) *(coming soon)*

---

*Last updated: August 13, 2025*
*Built with ❤️ for privacy and productivity.*