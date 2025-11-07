# ☁️ PMA Weather Assessment (Full Stack)

This repository contains a full-stack technical assessment submission, implementing a robust, decoupled API using **Python (FastAPI)** and a modern client using **React** (to be built in a later milestone).

The architecture is designed for scalability and maintainability, strictly adhering to principles of separation of concerns (API, Services, Models, Configuration).

---

## ✅ Task Completion Log

This section tracks completed tasks for **Milestone 1: The Backend** (Tech Assessment #2).

### **Task Group 1: Core Utilities (`feat/backend-core`)**

* **[COMPLETED] Professional Project Structure:** Implemented a multi-layer architecture for clarity (e.g., separating core configuration, database, and future API logic).
* **[COMPLETED] Decoupled Configuration (`app/core/config.py`):** Uses **`pydantic-settings`** to load all application settings (API keys, database URLs, etc.) from a local `.env` file, enforcing a strict "no hard-coding" rule.
* **[COMPLETED] Database Utility (`app/core/database.py`):** Configured the SQLAlchemy engine and created the professional `get_db` dependency for managing database sessions. The code is ready for both SQLite (default) and external databases (like Postgres).
* **[COMPLETED] Dependency Management:** Defined all core packages with pinned versions in `backend/requirements.txt` for guaranteed environment reproducibility.

### **Task Group 2: Data Contracts (`feat/data-models`)**

* **[COMPLETED] Data Contracts:** Defined the complete data layer, including the **SQLAlchemy Model** (`WeatherSearch`) and all necessary **Pydantic Schemas**.
    * **Architecture Detail:** The model is designed to handle the **CREATE with Date Range** requirement and includes fields for **Milestone 3 API Integration** (YouTube, Google Maps).

### **Task Group 3: Business Logic & Validation (`feat/service-external-api` / `feat/service-weather-crud`)**

* **[COMPLETED] External API Integration:** Implemented robust logic in `external_apis.py` to securely call the WeatherAPI, handle all HTTP/API errors, and **dynamically retrieve data** by correctly looping through the `history.json` endpoint for historical date ranges.
* **[COMPLETED] Core Service Logic:** Implemented **all mandatory CRUD functions** (`create_weather_search`, `get_all_searches`, `update_weather_search`, `delete_weather_search`) in the Service Layer.
    * **Advanced Validation:** Implemented strict date range checks and explicit **location validation (fuzzy match)** using the `/search.json` endpoint before fetching data.
    * **Complex Update Logic:** The `UPDATE` function is fully compliant, triggering a **full data refresh and re-validation** if a user attempts to modify the location or date range.
* **[COMPLETED] Architectural Refinement:** Refactored the Service Layer into dedicated sub-modules (`weather_crud.py`, `weather_extraction.py`) to keep the main `weather_service.py` file thin and focused on orchestration, maintaining the highest standards of maintainability.

---

## 🛠️ Setup Instructions

To prepare the backend for development, follow these steps:

#### **A. Environment Setup**

1.  **Create and Activate Environment:**

    ```bash
    # Ensure you are using Python 3.10 or later
    conda create -n pma-weather python=3.10
    conda activate pma-weather
    ```

2.  **Install Dependencies:**
    Navigate to the `backend/` directory and install the pinned packages:

    ```bash
    cd backend
    pip install -r requirements.txt
    cd ..
    ```

#### **B. Configuration**

1.  **Create `.env` File:**
    Copy the configuration template to your local environment file:

    ```bash
    cp backend/.env.example backend/.env
    ```

2.  **Configure API Key:**
    Open the newly created `backend/.env` file and replace `"YOUR_API_KEY_GOES_HERE"` with your actual API key for WeatherAPI.

---

## ⏭️ Next Steps

The next task, **`feat/endpoints-weather-crud`**, will focus on creating the FastAPI routers and endpoints to expose the completed Service Layer logic to the client.

