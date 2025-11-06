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

### **Current Task**

* **[IN PROGRESS] Data Contracts:** Define the SQLAlchemy Model (`app/db/models/weather.py`) and Pydantic Schemas (`app/schemas/weather.py`).

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