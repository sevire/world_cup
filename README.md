# World Cup Project

A monorepo for the World Cup project.

## Getting Started

1. **Backend dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
2. **Database:**
   ```bash
   docker compose up -d
   ```
3. **Migrations:**
   ```bash
   cd backend && python manage.py migrate
   ```
4. **Django server:**
   ```bash
   python manage.py runserver
   ```
5. **Frontend:**
   ```bash
   cd frontend && npm install && npm run dev
   ```

## Project Structure
- `backend/`: Django project named "config" with apps "users" and "tournaments".
- `frontend/`: Vue 3 + TypeScript + Vite project.
- `docker-compose.yml`: Postgres database service.
- `.env.example`: Template for environment variables.
