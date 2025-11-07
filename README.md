# ☁️ PMA Weather Assessment (Full Stack)

This repository contains a full-stack technical assessment submission, implementing a robust, decoupled API using **Python (FastAPI)** and a modern client using **React** (to be built in a later milestone).

The architecture is designed for scalability and maintainability, strictly adhering to principles of separation of concerns (API, Services, Models, Configuration).

---

## ✅ Task Completion Log: Backend (Milestone 1)

This log tracks the successful completion of all mandatory and highly recommended features for Tech Assessment #2.

### **Group 1: Core Utilities & Foundation**

* **[COMPLETED] Professional Architecture:** Implemented a multi-layer structure (`core/`, `db/`, `schemas/`, `services/`) for clarity and maintainability.
* **[COMPLETED] Decoupled Configuration:** Uses `pydantic-settings` to load all settings securely from the `.env` file.
* **[COMPLETED] Database Utility:** Configured SQLAlchemy engine and `get_db` dependency for file-based persistence (SQLite).

### **Group 2: Data Contracts & Logic**

* **[COMPLETED] Data Contracts (Models & Schemas):** Defined `WeatherSearch` model and necessary Pydantic schemas, including fields for date range input, range-wide summaries, and future API integrations (Google/YouTube).
* **[COMPLETED] Advanced Service Logic:** Implemented highly complex logic to support:
    * **Historical Ranges:** Dynamically loops through the `history.json` API endpoint for multi-day historical searches.
    * **Fuzzy Match/Validation:** Uses the `/search.json` endpoint to validate and normalize user location input.
    * **Range Summaries:** Calculates range-wide average temperature, humidity, and max wind speed for easy data retrieval.

### **Group 3: CRUD & Production Readiness**

* **[COMPLETED] CRUD Endpoints:** All mandatory CRUD functionality (`POST`, `GET`, `PUT`, `DELETE`) is exposed via asynchronous FastAPI routes (`endpoints/weather.py`).
* **[COMPLETED] Complex UPDATE Logic:** The `PUT` endpoint is robust, automatically triggering a **full API data refresh and re-validation** if the user attempts to update the location or date range.
* **[COMPLETED] Data Export (TA 2.3):** Implemented the `/weather/export/` endpoint and service logic to stream data as **JSON** or **CSV** files.
* **[COMPLETED] Asynchronous & Observability:** Upgraded all external HTTP calls to non-blocking **`httpx`** and integrated structured logging for server-side error diagnostics.

### **Group 4: Quality Assurance**

* **[COMPLETED] Automated Testing:** Implemented a complete suite of **unit and integration tests** using `pytest` and `pytest-mock` to verify service logic and API flow without hitting external networks.

---
### **Group 5: Advanced Features (To Stand Apart)**

* **[COMPLETED] API Integration (TA 2.2):** Implemented YouTube Data API (v3) for video searches. Added a resilient Google Maps link fallback using latitude/longitude from the core weather response, bypassing billing requirements for the Geocoding API.

---

## 🛠️ Setup Instructions (Backend)

To set up and run the fully functional backend:

#### **A. Environment Setup**

1.  **Create and Activate Environment:**

    ```bash
    conda create -n pma-weather python=3.10
    conda activate pma-weather
    ```

2.  **Install Dependencies:**
    Navigate to the `backend/` directory and install the packages:

    ```bash
    cd backend
    pip install -r requirements.txt
    cd ..
    ```

#### **B. Configuration**

1.  **Create `.env` File:**
    ```bash
    cp backend/.env.example backend/.env
    ```

2.  **Configure API Keys:** Open `backend/.env` and configure your keys:
    * `WEATHERAPI_API_KEY="YOUR_WEATHERAPI_KEY"`
    * `GOOGLE_API_KEY="YOUR_GOOGLE_CLOUD_KEY_FOR_YOUTUBE"`

#### **C. Run the Server**

1.  Start the application from the project root:

    ```bash
    uvicorn backend.main:app --reload
    ```
    *The interactive documentation will be available at `http://127.0.0.1:8000/docs`.*

---

## ⏭️ Next Steps

The backend is feature-complete for the assessment. The next step is to build the **Frontend (Tech Assessment 1)**.