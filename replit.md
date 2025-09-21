# AI Startup Analyst Platform

## Overview
This is an AI-powered platform to evaluate startups by synthesizing founder materials and public data to generate concise, actionable investment insights. The platform uses a microservices architecture with a React frontend and multiple backend services.

## Project Architecture
- **Frontend**: React + TypeScript + Vite (Port 5000)
- **Backend Services**:
  - API Gateway: Node.js + Express (Port 3000)
  - User Service: Node.js + TypeScript + Firebase Admin (Port 3001)
  - Reporting Service: Node.js + TypeScript + Firebase (Port 3002)
  - Ingestion Service: Python + FastAPI (Port 8000)
  - Analysis Service: Python + FastAPI (Port 8001)

## Recent Changes (September 21, 2025)
- Configured for Replit environment (removed Docker dependencies)
- Set up frontend to run on port 5000 with proper host configuration
- Installed Node.js 20 and Python 3.11 dependencies
- Fixed security vulnerability by removing hardcoded Firebase keys from docker-compose.yml
- Added fallback configuration for Firebase to allow app to run without credentials
- Created environment variable template (.env.example) for Firebase configuration

## User Preferences
- Uses TypeScript for type safety
- Material-UI for frontend components
- Firebase for authentication and database
- Google Cloud services for AI/ML capabilities

## Current State
- Frontend is successfully running on port 5000
- All dependencies installed for Node.js and Python services
- Firebase configured with fallbacks for development
- Ready for deployment configuration