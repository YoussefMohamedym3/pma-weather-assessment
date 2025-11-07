# ☁️ PMA Weather Assessment (Full Stack)

This repository contains a full-stack technical assessment submission, implementing:
1.  A robust, decoupled API using **Python (FastAPI)**.
2.  A responsive, single-page client using **React (Vite + TypeScript)**.

The architecture is designed for scalability and maintainability, with a clean separation of concerns.

---

## 🚀 How to Run the Full-Stack Application

You will need two terminals.

### Terminal 1: Run the Backend (API)

1.  **Environment Setup (First-time only):**
    ```bash
    conda create -n pma-weather python=3.10
    conda activate pma-weather
    pip install -r backend/requirements.txt
    ```

2.  **Configuration (First-time only):**
    ```bash
    # Create the .env file
    cp backend/.env.example backend/.env
    ```
    Now, open `backend/.env` and add your API keys.

3.  **Run the Backend Server:**
    ```bash
    # From the project root
    uvicorn backend.main:app --reload
    ```
    *The backend will run at `http://127.0.0.1:8000`.*

### Terminal 2: Run the Frontend (React App)

1.  **Environment Setup (First-time only):**
    ```bash
    cd frontend
    npm install
    ```

2.  **Run the Frontend Server:**
    ```bash
    # From the 'frontend' directory
    npm run dev
    ```
    *The frontend will run at `http://localhost:5173` and automatically open in your browser.*

---

## ✅ Task Completion Log

### Backend (Tech Assessment #2)

* **[COMPLETED] Foundation:** Professional architecture (`core/`, `db/`, `schemas/`, `services/`), SQLAlchemy setup, and Pydantic settings management.
* **[COMPLETED] Advanced Logic:** Implemented fuzzy location matching (`/search.json`), historical date range looping (`/history.json`), and validation to prevent "mixed" date (past/future) requests.
* **[COMPLETED] Full CRUD Endpoints:** All `POST`, `GET`, `PUT`, and `DELETE` endpoints are functional.
* **[COMPLETED] Complex UPDATE:** The `PUT` endpoint robustly handles full data refreshes if location/dates are changed.
* **[COMPLETED] API Integration (TA 2.2):** Backend service fetches Google Maps URLs and YouTube video IDs.
* **[COMPLETED] Data Export (TA 2.3):** Backend provides `/export` endpoint for both **JSON** and **CSV** downloads.
* **[COMPLETED] Quality:** All services are asynchronous (`httpx`) and the API is fully documented via OpenAPI.

### Frontend (Tech Assessment #1)

* **[COMPLETED] Location Input:** User can search by location name, zip, or GPS coordinates.
* **[COMPLETED] Current Location:** "Get My Location" button uses browser Geolocation.
* **[COMPLETED] 5-Day Forecast:** App correctly queries for a 5-day range and displays it in a horizontal grid.
* **[COMPLETED] Weather Icons:** Icons are fetched from the API and displayed.
* **[COMPLETED] Full CRUD Interface:**
    * **Create:** Main search form with date pickers.
    * **Read:** "Previous Searches" list loads on start. A "Details" modal shows full data.
    * **Update:** "Edit" modal allows for a full update of location, dates, or notes.
    * **Delete:** "Delete" button removes records.
* **[COMPLETED] API/Export Links:** Frontend displays links for Google Maps, YouTube, and data export downloads.
* **[COMPLETED] Error Handling:** All API errors (e.g., location not found, invalid dates) are caught and shown to the user.
* **[COMPLETED] Responsive Design:** The app is fully responsive, using CSS media queries to stack elements and reformat the data table on mobile devices.
* **[COMPLETED] Submission Info:** App includes the required developer name and PMA description footer.