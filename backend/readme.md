# Backend - Nigeria Tax Q&A Assistant

## Setup
1. Install requirements
2. Set environment variables
3. Run Using: 
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend:$(pwd)/ai_engine
uvicorn backend.app.main:app --reload


## API Documentation
GET /health - Health check
POST /api/chat - Send message

## Architecture
- FastAPI for HTTP API
- AI Engine integration
- Session management




# NOTE
 There must be an ai_engine folder present and a backend folder , install all necessary requirements,add your api key to .env file, also add this database url (DATABASE_URL = mysql+pymysql://root:Ademsbbb@localhost:3306/tax_reform
) to your .env file,   then run the code above in terminal.



.env file must contain
GEMINI_API_KEY = "AIzaSyDoDIE159Xet3bEiO5FI7JCgZ9f5FR39yE"

DATABASE_URL = mysql+pymysql://root:Ademsbbb@localhost:3306/tax_reform