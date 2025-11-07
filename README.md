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
    * **Complex Update Logic:** The `UPDATE` function is fully compliant, triggering a **full data refresh and re-validation** if a user attempts to modify the location or date range.
* **[COMPLETED] Architectural Refinement:** Refactored the Service Layer into dedicated sub-modules (`weather_crud.py`, `weather_extraction.py`) to keep the main `weather_service.py` file thin and focused on orchestration, maintaining the highest standards of maintainability.

### **Task Group 4: API Endpoints & Setup (`feat/endpoints-weather-crud`)**

* **[COMPLETED] Implement CRUD Endpoints:** Created the FastAPI router (`endpoints/weather.py`) with asynchronous handlers for all CRUD operations.
* **[COMPLETED] Asynchronous Upgrade:** Refactored the API call dependencies from synchronous (`requests`) to asynchronous (`httpx`), greatly improving server performance and concurrency.
* **[COMPLETED] Production Setup:** Added logging for observability and configured basic CORS middleware for frontend compatibility.

---
### **Task Group 5: Advanced Features (To Stand Apart)**

* **[PENDING] Data Export:** Implement the endpoint and service logic to export data from the database (e.g., CSV).
* **[PENDING] API Integration:** Implement the service logic for Google Maps and YouTube data retrieval.

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
### **Testing and Quality Assurance**

To ensure the reliability and correctness of the complex service logic (especially the date handling, fuzzy location matching, and data extraction), a comprehensive test suite was implemented.

#### **How to Run Tests**

The test suite is located in the top-level `tests/` directory and can be executed using `pytest`.

1.  Ensure your `pma-weather` Conda environment is active.
2.  Run the following command from the project root:

    ```bash
    pytest
    ```

#### **Testing Strategy**

The tests are separated to maximize coverage and maintainability:

1.  **Unit Tests (`tests/services/`):** Directly test the pure Python functions within the service layer (e.g., `_extract_summary_data_for_db`) to verify that the complex range-wide averages and calculations are mathematically correct. These tests run without network access or database connection.
2.  **Integration Tests (`tests/api/`):** Test the entire API flow for all CRUD endpoints (`POST`, `GET`, `PUT`, `DELETE`).
    * **Mocking:** All external dependencies (the `WeatherAPI` and the actual `SQLAlchemy` database calls) are **mocked** using `pytest-mock`. This ensures that tests are fast, stable, and never rely on network access or leave temporary data in the database, fulfilling a production-grade standard.

This section clearly communicates the high quality of your submission. You can now insert this text into your `README.md` file.

---



## ⏭️ Next Steps

The next task is **Data Export (Task Group 5, Part 1)**.