# RecruitGenie – AI-Powered Resume Screening & Candidate Insights

>An end-to-end full-stack recruitment intelligence platform built with FastAPI, Next.js, and AI-driven scoring engines.
RecruitGenie automates resume parsing, scoring, shortlisting, interview question generation, and analytics.

## Features

## AI-Driven Resume Processing

	•	Extracts candidate information (name, email, phone, skills).
	•	Computes base score, skill score, penalty, and overall score.
	•	Identifies missing skills and found skills.
	•	Generates tailored interview questions automatically.

## Resume Upload Portal

	•	Upload .pdf, .docx, or .txt resumes.
	•	Auto-processed and stored.
	•	Results instantly displayed.

## Candidate Management Dashboard

	•	View all processed candidates.
	•	Filter by job ID or status.
	•	Update status (shortlisted, review, reject) directly.
	•	Add notes per candidate.
	•	Open raw JSON detail.

## Analytics Dashboard

	•	Total candidates
	•	Average score
	•	Distribution by status
	•	Top missing skills
	•	Data visualizations (frontend)

## CSV-Based Persistence

	•	All candidate data stored in backend/assets/candidate_data.csv
	•	Auto-created if missing

## Download Uploaded Resume

	•	Backend endpoint to download original uploaded resume files

## Tech Stack

Frontend — Next.js 16 (App Router)
	•	React + TypeScript
	•	Client-side fetching
	•	Reusable pages:
/upload, /candidates, /analytics
	•	Environment-based API routing

Backend — FastAPI
	•	Async endpoints
	•	Multipart resume upload
	•	CSV-based data layer
	•	Resume parsing agent
	•	Scoring engine
	•	Interview question generator
	•	CORS enabled for Next.js

AI / Agents
	•	ResumeAgent
	•	ScoringAgent
	•	InterviewAgent
	•	DataAgent (CSV writer)

## Folder Structure

```shell
RecruitGenie/
│
├── backend/
│   ├── agents/
│   │   ├── resume_agent.py
│   │   ├── scoring_agent.py
│   │   ├── interview_agent.py
│   │   ├── data_agent.py
│   ├── assets/
│   │   ├── resumes/
│   │   ├── candidate_data.csv
│   │   └── job_description.txt
│   ├── main.py
│   ├── recruitgenie_app.py
│   ├── requirements.txt
│
├── recruitgenie-frontend/
│   ├── app/
│   │   ├── upload/page.tsx
│   │   ├── candidates/page.tsx
│   │   ├── analytics/page.tsx
│   │   ├── layout.tsx
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   └── .env
│
└── README.md
```

## Backend Setup (FastAPI)

1️⃣ Create & activate virtual environment
```shell
python3 -m venv backend/venv
source backend/venv/bin/activate
```

2️⃣ Install dependencies
```shell
pip install -r backend/requirements.txt
```

3️⃣ Run FastAPI server
```shell
uvicorn backend.main:app --reload --port 8001
```

## Frontend Setup (Next.js)

1️⃣ Navigate to frontend
```shell
cd recruitgenie-frontend
```

2️⃣ Install dependencies
```shell
npm install
```

3️⃣ Create .env file
```shell
NEXT_PUBLIC_API_BASE=http://localhost:8001
```

4️⃣ Run development server
```shell
npm run dev
```

## Key API Endpoints

▶ Upload Resume
```shell
POST /upload_resume/?job_id=JOB_01
```

▶ Get All Candidates
```shell
GET /candidates/
```

▶ Update Status
```shell
PATCH /candidates/{id}/status
```

▶ Update Notes
```shell
PATCH /candidates/{id}/notes
```

▶ Analytics Summary
```shell
GET /analytics/summary
```

▶ Download Uploaded Resume
```shell
GET /resumes/file/{filename}
```

## How Scoring Works

Each resume goes through:
	1.	ResumeAgent → Extract text + contact details
	2.	ScoringAgent →
	    •	base_score
	    •	skill_score
	    •	penalty
	    •	missing_skills
    	•	found_skills
    	•	total_score
	3.	InterviewAgent →
      Generates questions based on missing vs found skills
	4.	DataAgent →
      Writes a new row to CSV and assigns:
      shortlisted, review, or reject

## Future Enhancements

	•	OAuth2 login for recruiters
	•	Multi-job descriptions
	•	MongoDB/PostgreSQL persistence
	•	AI-powered skill extraction
	•	Resume similarity ranking
	•	PDF previewer in frontend

## Contributing

Pull requests are welcome!
For major changes, please open an issue first to discuss.

## License

Licensed under the MIT License, allowing full flexibility to reuse, modify, distribute, and integrate this project into personal or commercial applications. Attribution is required.


## Contact

If you have questions, suggestions, or collaboration ideas, feel free to reach out at:
📩 akashgpatil23.05@gmail.com
