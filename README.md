🚀 Social Network Engagement Bot

A FastAPI-based service for tracking social media follower changes and engagement

📌 Project Overview

This project is a RESTFul API that enables users to monitor follower changes on social media platforms (Instagram, Twitter) and analyze engagement rates over time.

✅ Key Features:

Register and manage social media profiles for tracking

Periodically check follower changes and store them in the database

Send Telegram alerts when follower milestones are reached

Analyze engagement rate based on changes in the last 24 hours

Store user sessions with Redis for enhanced security

Configure follower check intervals dynamically via config
Fully asynchronous implementation for scalability and efficiency

🛠 Technologies & Frameworks

FastAPI: API framework with async support and OpenAPI integration

PostgreSQL: Database for storing user and follower data

Redis: Caching and session management

SQLAlchemy + Alembic : ORM and database migrations

aiohttp : Async HTTP requests for social media APIs & Telegram

Pydantic :Data validation and serialization

Docker & Docker Compose : Containerized deployment



📦 Getting Started
1. Get the Project
git clone https://github.com/captainmohsen/social_network_engagement_bot.git
cd social-engagement-bot


2. Run the project with Docker Compose
docker compose up --build


Running server swagger is :
http://localhost:8000/api/v1/docs#/

