# Splitwise Agent

A scalable backend service that uses AI agents to process receipt images and interact with Splitwise API. The service can automatically read receipts, extract relevant information, and create expense entries in Splitwise.

## Features

- REST API for interacting with Splitwise
- Multi-agent system for processing receipts
- Multi-modal model integration for receipt OCR
- Automated expense entry creation
- Scalable architecture

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Splitwise API credentials
   ```
4. Run the service:
   ```bash
   python -m src.main
   ```

## API Documentation

The service exposes RESTful endpoints for:
- Receipt image upload and processing
- Direct Splitwise interactions
- Agent status monitoring

Detailed API documentation is available at `/docs` when running the service.

## Architecture

The service uses:
- FastAPI for REST API
- CrewAI for multi-agent orchestration
- Splitwise SDK for API integration
- Multi-modal models for receipt processing

## License

MIT License
