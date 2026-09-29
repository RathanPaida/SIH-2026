# 🇮🇳 Manak Mitra — AI Recommendations for Indian Standards

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016-black.svg?style=flat&logo=next.js)](https://nextjs.org)
[![TailwindCSS](https://img.shields.io/badge/Styling-TailwindCSS%20v4-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=docker)](https://docker.com)

> **Smart India Hackathon (SIH 2026) Prototype**  
> Problem Statement: SIH26108 - AI Powered Recommendation Engine for Identifying Applicable Indian Standards for Procurement Specifications
> Tagline: "Standards for Smarter Procurement"

## 🌟 Key Features
- **12-Stage AI Analysis Pipeline**: Extracts requirements, maps them to the BIS graph, validates QCOs, checks lifecycles, and flags gaps/conflicts.
- **Two-Pane Workspace**: Review requirements and recommendations side-by-side with the original tender document.
- **Compliance Audit Trail**: Every AI action and human approval/rejection is permanently logged.
- **Multilingual UI**: Gov-Tech design system available in 6 Indian languages.
- **Docker Ready**: Run the entire stack locally with a single command.

## 🚀 Getting Started

### Method 1: Docker (Recommended)
You can start the entire application using Docker Compose:
```bash
docker compose up --build -d
```
The website will be available at **http://localhost:3000** and the backend at **http://localhost:8000**.

### Method 2: Manual Start

**1. Start Backend (Terminal 1)**
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
*Note: On the very first run, it will automatically build the FAISS index and seed the SQLite database (`manak_mitra.db`).*

**2. Start Frontend (Terminal 2)**
```powershell
cd frontend
npm install
npm run dev
```
Open **http://localhost:3000** in your browser.

## 📖 How to Operate (Workflow)
1. **Dashboard**: View your past analyses. Click "+ New Analysis".
2. **New Analysis**: Paste your tender text or upload a document. Select a Domain Hint, toggle the Cross-Encoder for higher accuracy, and click Start.
3. **Loading Status**: Watch the 12-stage pipeline execute in real-time.
4. **Results Workspace**: 
   - **Requirements Tab**: Review each extracted requirement. Approve or Reject the recommended standards. Pay attention to red **QCO** chips (mandatory standards).
   - **Coverage Tab**: Review the Gap Analysis to see what standard categories you missed in your tender.
   - **Conflicts Tab**: See if you referenced outdated standards.
   - **Audit Tab**: Review the system's decisions.
5. **Finalize**: Generate the procurement compliance report.

For a deeper dive into the system architecture and evaluation metrics, read [WEBSITE_AND_WORKING_EXPLAINER.md](./WEBSITE_AND_WORKING_EXPLAINER.md).
