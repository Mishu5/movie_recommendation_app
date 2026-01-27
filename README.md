**Group Movie Recommendation App**
A cross-platform application that supports a group of users in selecting a movie or TV series for collective viewing. Users rate titles, join rooms, and receive group recommendations generated using the KNN algorithm based on IMDb data.

**Key Features**
- Recommendations generated using KNN (scikit-learn)
- Real-time group rooms using Socket.io
- Cross-platform frontend (Expo / React Native — web and mobile)
- Flask backend with JWT authentication

**PostgreSQL database populated with IMDb dataset**
Docker support for deployment

**Technology Stack**
Frontend: Expo (React Native), TypeScript, Socket.io-client
Backend: Python Flask, SQLAlchemy, Flask-SocketIO, scikit-learn
Database: PostgreSQL (IMDb TSV dataset)
External API: OMDb API (metadata and posters)
DevOps: Docker, Docker Compose

**Setup**
1. Clone repository
git clone https://github.com/USER/movie-recommendation-app.git
cd movie-recommendation-app

2. Run with Docker
docker-compose up --build

**Default ports:**
Service	Port
Backend	5000
Frontend	19006
Database	5432

**IMDb Database Source**

This system uses bulk TSV files from the official IMDb dataset. Files can be downloaded from:

https://datasets.imdbws.com/

Required at minimum:
title.basics.tsv
title.ratings.tsv

Files should be placed inside:
backend/


Data loading and filtering logic is handled by:
backend/data/get_data.py

No API key is required for IMDb because the dataset is file-based.
OMDb External API (for metadata and posters)
For additional information such as posters, plot summaries or cast, the application uses the OMDb API:
https://www.omdbapi.com/

**How to obtain the API key:**
1. Open the OMDb website.
2. Select the "API Key" section.
3. Register with an email address.
4. Receive a personal API key via email.

**Configuration (example .env):**
OMDB_API_KEY=your_api_key
