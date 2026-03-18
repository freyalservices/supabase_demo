# agents.md

## Project: InfraSight --- AI-powered Infrared Small Target Detection Platform

### Overview

InfraSight is an AI-powered platform designed to detect small targets in
infrared images using classical image processing techniques such as
Dual-Window Local Contrast Method (DW-LCM) and Multiscale Window
Infrared Patch-Image Model (MW-IPI).

The system is built using a microservices architecture with FastAPI,
Supabase for backend services, a modern Vue.js frontend, and GitHub
Actions for CI/CD automation.

------------------------------------------------------------------------

## 🧠 Project Idea

The platform allows users to: - Upload infrared images - Process images
using detection algorithms - View highlighted detection results - Store
and retrieve processed outputs through a clean, interactive UI

This project demonstrates real-world backend engineering, frontend
design, system architecture, and DevOps practices.

------------------------------------------------------------------------

## 🎨 Frontend (Vue.js)

A modern and visually appealing frontend built with Vue.js will provide:

-   Clean dashboard UI
-   Image upload interface (drag & drop)
-   Real-time processing status
-   Visualization of detection results (highlighted targets)
-   History of uploaded images and results

### Suggested Stack:

-   Vue 3
-   Vite
-   Tailwind CSS (for beautiful UI)
-   Axios (API calls)

------------------------------------------------------------------------

## 🧱 Architecture

### Services

1.  **Frontend (Vue.js)**
    -   User interface and interaction
    -   Communicates with API Gateway
2.  **API Gateway (FastAPI)**
    -   Handles client requests and routing
    -   Authenticates users via Supabase
    -   Sends images to processing service
3.  **Processing Service (FastAPI)**
    -   Implements:
        -   Dual-Window Local Contrast Method (DW-LCM)
        -   Multiscale Window Infrared Patch-Image Model (MW-IPI)
    -   Returns processed images and detected target coordinates
4.  **Supabase**
    -   PostgreSQL database (stores metadata and results)
    -   Authentication (JWT-based login/signup)
    -   Storage (infrared images and outputs)

------------------------------------------------------------------------

## ⚙️ Tech Stack

-   Frontend: Vue.js, Tailwind CSS
-   Backend: FastAPI
-   Supabase (PostgreSQL, Auth, Storage)
-   Python 3.11+
-   Docker & Docker Compose
-   GitHub Actions (CI/CD)
-   OpenCV / NumPy (for image processing)

------------------------------------------------------------------------

## 📁 Project Structure

    project/
    │
    ├── frontend/
    │   ├── src/
    │   └── public/
    │
    ├── gateway-service/
    │   ├── main.py
    │   └── routes/
    │
    ├── processing-service/
    │   ├── main.py
    │   └── algorithms/
    │
    ├── docker-compose.yml
    ├── .github/workflows/ci.yml
    └── agents.md

------------------------------------------------------------------------

## 🚀 Setup Instructions

### 1. Clone Repo

``` bash
git clone <repo-url>
cd project
```

### 2. Run with Docker

``` bash
docker-compose up --build
```

### 3. Run Frontend

``` bash
cd frontend
npm install
npm run dev
```

### 4. Environment Variables

Create `.env` file:

    SUPABASE_URL=your_url
    SUPABASE_KEY=your_key

------------------------------------------------------------------------

## 🔄 System Workflow

1.  User logs in via Supabase Auth\
2.  Uploads infrared image via frontend UI\
3.  API Gateway receives request\
4.  Gateway forwards image to Processing Service\
5.  Processing Service applies DW-LCM / MW-IPI\
6.  Results stored in Supabase\
7.  Frontend displays processed image and detection results

------------------------------------------------------------------------

## 🔁 CI/CD (GitHub Actions)

GitHub Repository: https://github.com/freyalservices/supabase_demo

Pipeline includes: - Install dependencies - Run tests (pytest) - Lint
code (ruff/flake8) - Build Docker images - Optional deployment
(backend + frontend)

------------------------------------------------------------------------

## 🧪 Testing

``` bash
pytest
```

------------------------------------------------------------------------

## 📌 Notes

-   Keep services minimal (2--3 backend services)
-   Focus on UI/UX quality for frontend
-   Use Tailwind for rapid and beautiful design
-   Optimize image processing for performance

------------------------------------------------------------------------

## 🎯 Goal

Build a production-style system showcasing: - Microservices
architecture - AI-based image processing - Beautiful frontend using
Vue.js - Backend engineering with FastAPI - Cloud integration with
Supabase - DevOps practices using CI/CD
