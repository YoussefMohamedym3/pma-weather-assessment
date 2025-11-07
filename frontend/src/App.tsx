// This is your entire frontend/src/App.tsx file

/* This is a simple <style> block for CSS.
   We add it here to keep everything in one file.
*/
const responsiveStyles = `
  /* --- Base Container --- */
  .app-container {
    padding: 20px;
    font-family: sans-serif;
    max-width: 900px; /* Widen max-width slightly for desktop */
    margin: auto;
  }

  /* --- Form Styling --- */
  .search-form {
    margin-bottom: 20px;
    border: 1px solid #ccc;
    padding: 15px;
  }
  .form-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap; /* This already helps */
  }
  .form-group {
    flex: 1 1 150px; /* Base size */
    display: flex;
    flex-direction: column;
  }
  .form-group-location {
    flex: 1 1 300px; /* Location input is wider */
  }
  .form-group label {
    margin-bottom: 4px;
    font-size: 0.9em;
  }
  .form-input {
    padding: 9px;
    font-size: 1rem;
    width: 100%;
    box-sizing: border-box;
  }

  /* --- Forecast Styling --- */
  .forecast-grid {
    display: flex;
    justify-content: space-between;
    gap: 10px;
  }
  .forecast-day {
    border: 1px solid #eee;
    padding: 10px;
    text-align: center;
    flex: 1; /* Each box takes equal space */
    min-width: 100px; /* Min width before wrapping */
  }

  /* --- List Table Styling --- */
  .search-table {
    width: 100%;
    border-collapse: collapse;
  }
  .search-table th, .search-table td {
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #ccc;
  }
  .search-table th {
    border-bottom-width: 2px;
  }
  .search-table-actions {
    display: flex;
    gap: 5px;
    flex-wrap: wrap; /* Allow buttons to wrap on small screens */
  }

  /* --- Modal Styling --- */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  .modal-content {
    background-color: #fff;
    padding: 20px;
    border-radius: 5px;
    width: 90%;
    max-width: 500px;
    color: #333;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
  }
  .modal-body {
    overflow-y: auto;
    max-height: 60vh;
  }
  .modal-input {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
    margin-bottom: 10px;
  }
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
    padding-top: 10px;
    border-top: 1px solid #eee;
  }
  .modal-button {
    background: none;
    border: 1px solid #ccc;
    padding: 8px 12px;
    cursor: pointer;
  }
  .modal-button-primary {
    background: blue;
    color: white;
    border: none;
    padding: 8px 12px;
    cursor: pointer;
  }

  /* --- ‼️ RWD: On screens 600px or less (phones) ‼️ --- */
  @media (max-width: 600px) {
    .app-container {
      padding: 10px; /* Tighter padding on mobile */
    }

    .forecast-grid {
      flex-direction: column; /* Stack forecast days vertically */
    }

    /* This is the magic for the table */
    .search-table thead {
      /* Hide the table header */
      display: none;
    }
    .search-table tr {
      /* Make each row look like a "card" */
      display: block;
      margin-bottom: 15px;
      border: 1px solid #ccc;
    }
    .search-table td {
      display: block; /* Stack cells vertically */
      text-align: right; /* Align data to the right */
      border-bottom: 1px solid #eee;
    }
    .search-table td:last-child {
      border-bottom: none;
    }
    /* Add the "Header" as a label before the data */
    .search-table td::before {
      content: attr(data-label); /* Use the data-label attribute */
      float: left;
      font-weight: bold;
      text-align: left;
    }
  }
`;

import React, { useState, useEffect } from "react";

// --- Type Definitions ---

type WeatherData = {
  id: number;
  location_name: string;
  search_date_from: string;
  search_date_to: string;
  user_note: string | null;
  summary_avg_temp_c: number;
  summary_condition_text: string;
  summary_avg_humidity: number;
  summary_max_wind_kph: number;
  raw_forecast_data: {
    forecast: {
      forecastday: ForecastDay[];
    };
  };
  google_maps_url: string | null;
  youtube_video_ids: string[] | null;
};

type ForecastDay = {
  date: string;
  date_epoch: number;
  day: {
    maxtemp_c: number;
    mintemp_c: number;
    avgtemp_c: number;
    maxwind_kph: number;
    avghumidity: number;
    condition: {
      text: string;
      icon: string;
    };
  };
};

const API_BASE_URL = "http://localhost:8000";

// --- Helper functions to get dates ---
const getToday = () => new Date().toISOString().split("T")[0];
const getPlusFourDays = () => {
  const futureDate = new Date();
  futureDate.setDate(futureDate.getDate() + 4);
  return futureDate.toISOString().split("T")[0];
};

function App() {
  // --- State Variables ---
  const [location, setLocation] = useState<string>("");
  const [dateFrom, setDateFrom] = useState<string>(getToday());
  const [dateTo, setDateTo] = useState<string>(getPlusFourDays());

  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [allSearches, setAllSearches] = useState<WeatherData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // --- State for Edit Modal ---
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editLocation, setEditLocation] = useState<string>("");
  const [editDateFrom, setEditDateFrom] = useState<string>("");
  const [editDateTo, setEditDateTo] = useState<string>("");
  const [editNote, setEditNote] = useState<string>("");

  // --- State for Details Modal ---
  const [viewingDetails, setViewingDetails] = useState<WeatherData | null>(
    null
  );

  // --- Data Fetching Functions (CRUD) ---

  // READ (All)
  const fetchAllSearches = async () => {
    try {
      setError(null);
      const response = await fetch(`${API_BASE_URL}/weather/`);
      if (!response.ok) throw new Error("Failed to fetch search history.");
      const data: WeatherData[] = await response.json();
      setAllSearches(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchAllSearches();
  }, []);

  // CREATE
  const performWeatherSearch = async (
    locationQuery: string,
    searchFrom: string,
    searchTo: string
  ) => {
    setIsLoading(true);
    setError(null);
    setWeatherData(null);

    try {
      const response = await fetch(`${API_BASE_URL}/weather/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location_name: locationQuery,
          search_date_from: searchFrom,
          search_date_to: searchTo,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Error: ${response.statusText}`);
      }

      const data: WeatherData = await response.json();
      setWeatherData(data);
      await fetchAllSearches();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // DELETE
  const handleDelete = async (searchId: number) => {
    if (!window.confirm("Are you sure you want to delete this search?")) return;

    try {
      const response = await fetch(`${API_BASE_URL}/weather/${searchId}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to delete search.");
      }
      await fetchAllSearches();
    } catch (err: any) {
      setError(err.message);
    }
  };

  // --- UPDATE Functions (for Edit Modal) ---

  const handleOpenEdit = (search: WeatherData) => {
    setEditingId(search.id);
    setEditLocation(search.location_name);
    setEditDateFrom(search.search_date_from);
    setEditDateTo(search.search_date_to);
    setEditNote(search.user_note || "");
  };

  const handleCloseEdit = () => {
    setEditingId(null);
    setEditLocation("");
    setEditDateFrom("");
    setEditDateTo("");
    setEditNote("");
    setError(null);
  };

  const handleUpdateSave = async () => {
    if (!editingId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/weather/${editingId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location_name: editLocation,
          search_date_from: editDateFrom,
          search_date_to: editDateTo,
          user_note: editNote,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to update search.");
        throw new Error(errorData.detail);
      }

      await fetchAllSearches();
      handleCloseEdit();
    } catch (err: any) {
      console.error("Update failed:", err.message);
    }
  };

  // --- Event Handlers ---

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (location) {
      performWeatherSearch(location, dateFrom, dateTo);
    }
  };

  const handleMyLocationClick = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setWeatherData(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const locationQuery = `${latitude},${longitude}`;
        const today = getToday();
        const futureDate = getPlusFourDays();
        performWeatherSearch(locationQuery, today, futureDate);
      },
      (err) => {
        setError(`Failed to get location: ${err.message}`);
        setIsLoading(false);
      }
    );
  };

  // --- Helper variables for rendering ---
  const todayWeather =
    weatherData?.raw_forecast_data?.forecast?.forecastday?.[0];
  const forecastDays =
    weatherData?.raw_forecast_data?.forecast?.forecastday?.slice(1);

  // --- JSX (What Renders to the Page) ---
  return (
    <div className="app-container">
      {/* --- Inject our styles into the page --- */}
      <style>{responsiveStyles}</style>

      <header>
        <h1>Weather App</h1>
        <p>
          Enter a location and date range, or get your local 5-day forecast.
        </p>
      </header>

      {/* --- Search Form --- */}
      <form onSubmit={handleFormSubmit} className="search-form">
        <div className="form-row">
          <div className="form-group form-group-location">
            <label htmlFor="location">Location</label>
            <input
              id="location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., 'London' or '90210'"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="date-from">From</label>
            <input
              id="date-from"
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="date-to">To</label>
            <input
              id="date-to"
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="form-input"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: "10px",
            fontSize: "1rem",
            marginTop: "10px",
            cursor: "pointer",
          }}
        >
          {isLoading ? "Loading..." : "Get Weather"}
        </button>
      </form>

      {/* --- "My Location" Button --- */}
      <div style={{ marginBottom: "20px" }}>
        <button
          type="button"
          onClick={handleMyLocationClick}
          disabled={isLoading}
          style={{ padding: "10px", fontSize: "1rem", cursor: "pointer" }}
        >
          {isLoading ? "Loading..." : "Get My Location 5-Day Forecast"}
        </button>
      </div>

      {/* --- Error Display --- */}
      {error && !editingId && !viewingDetails && (
        <div
          style={{
            color: "red",
            border: "1px solid red",
            padding: "10px",
            marginBottom: "20px",
          }}
        >
          <strong>Error:</strong>
          <p>{error}</p>
        </div>
      )}

      {/* --- Main Weather Display --- */}
      {weatherData && todayWeather && (
        <div style={{ marginBottom: "30px" }}>
          <div style={{ border: "1px solid #ccc", padding: "15px" }}>
            <h2>
              Weather for {weatherData.location_name} on {todayWeather.date}
            </h2>

            {weatherData.google_maps_url && (
              <p style={{ margin: "5px 0" }}>
                <a
                  href={weatherData.google_maps_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on Google Maps
                </a>
              </p>
            )}

            <img
              src={`https:${todayWeather.day.condition.icon}`}
              alt={todayWeather.day.condition.text}
              style={{ float: "right", width: "64px", height: "64px" }}
            />
            <p>
              <strong>Temperature:</strong>{" "}
              {todayWeather.day.avgtemp_c.toFixed(1)}°C
            </p>
            <p>
              <strong>Condition:</strong> {todayWeather.day.condition.text}
            </p>
            <p>
              <strong>Humidity:</strong>{" "}
              {todayWeather.day.avghumidity.toFixed(0)}%
            </p>
            <p>
              <strong>Wind:</strong> {todayWeather.day.maxwind_kph.toFixed(1)}{" "}
              kph
            </p>
          </div>

          {/* --- Forecast Grid --- */}
          {forecastDays && forecastDays.length > 0 && (
            <div style={{ marginTop: "20px" }}>
              <h3>Forecast for following days</h3>
              <div className="forecast-grid">
                {forecastDays.map((day: ForecastDay) => (
                  <div key={day.date_epoch} className="forecast-day">
                    <p>
                      <strong>
                        {new Date(day.date).toLocaleDateString("en-US", {
                          weekday: "short",
                        })}
                      </strong>
                    </p>
                    <img
                      src={`https:${day.day.condition.icon}`}
                      alt={day.day.condition.text}
                      style={{ width: "48px", height: "48px" }}
                    />
                    <p style={{ fontSize: "0.9em" }}>
                      {day.day.condition.text}
                    </p>
                    <p style={{ fontSize: "0.9em" }}>
                      <strong>High:</strong> {day.day.maxtemp_c.toFixed(0)}°C
                    </p>
                    <p style={{ fontSize: "0.9em" }}>
                      <strong>Low:</strong> {day.day.mintemp_c.toFixed(0)}°C
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* --- Debug --- */}
          <details style={{ marginTop: "15px", clear: "both" }}>
            <summary>Show Raw JSON Response (for debugging)</summary>
            <pre
              style={{
                backgroundColor: "#f4f4f4",
                padding: "10px",
                overflowX: "auto",
              }}
            >
              {JSON.stringify(weatherData, null, 2)}
            </pre>
          </details>
        </div>
      )}

      {/* --- Data Export Section --- */}
      <hr style={{ margin: "30px 0" }} />
      <div>
        <h2>Data Export</h2>
        <p>Download all previous search data as a file.</p>
        <div style={{ display: "flex", gap: "10px" }}>
          <a
            href={`${API_BASE_URL}/weather/export/?format=csv`}
            download="weather_searches.csv"
            style={{
              padding: "10px 15px",
              textDecoration: "none",
              color: "white",
              backgroundColor: "green",
              borderRadius: "5px",
            }}
          >
            Download CSV
          </a>
          <a
            href={`${API_BASE_URL}/weather/export/?format=json`}
            download="weather_searches.json"
            style={{
              padding: "10px 15px",
              textDecoration: "none",
              color: "white",
              backgroundColor: "orange",
              borderRadius: "5px",
            }}
          >
            Download JSON
          </a>
        </div>
      </div>

      {/* --- Previous Searches List --- */}
      <hr style={{ margin: "30px 0" }} />
      <div>
        <h2>Previous Searches</h2>
        {allSearches.length === 0 ? (
          <p>No previous searches found.</p>
        ) : (
          <table className="search-table">
            <thead>
              <tr style={{ borderBottom: "2px solid #333" }}>
                <th>Location</th>
                <th>Date Range</th>
                <th>Note</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {allSearches.map((search) => (
                <tr key={search.id}>
                  <td data-label="Location">{search.location_name}</td>
                  <td data-label="Date Range">
                    {search.search_date_from} to {search.search_date_to}
                  </td>
                  <td data-label="Note">{search.user_note || "N/A"}</td>

                  <td data-label="Actions" className="search-table-actions">
                    <button
                      onClick={() => setViewingDetails(search)}
                      style={{
                        color: "green",
                        background: "none",
                        border: "1px solid green",
                        cursor: "pointer",
                        padding: "4px 8px",
                      }}
                    >
                      Details
                    </button>
                    <button
                      onClick={() => handleOpenEdit(search)}
                      style={{
                        color: "blue",
                        background: "none",
                        border: "1px solid blue",
                        cursor: "pointer",
                        padding: "4px 8px",
                      }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(search.id)}
                      style={{
                        color: "red",
                        background: "none",
                        border: "1px solid red",
                        cursor: "pointer",
                        padding: "4px 8px",
                      }}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* --- Edit Modal --- */}
      {editingId !== null && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Edit Search (ID: {editingId})</h2>
            <div className="modal-body">
              {error && (
                <div
                  style={{
                    color: "red",
                    background: "#ffeeee",
                    border: "1px solid red",
                    padding: "10px",
                    marginBottom: "10px",
                  }}
                >
                  <strong>Error:</strong> {error}
                </div>
              )}
              <div>
                <label htmlFor="edit-location">Location</label>
                <input
                  id="edit-location"
                  type="text"
                  value={editLocation}
                  onChange={(e) => setEditLocation(e.target.value)}
                  className="modal-input"
                />
              </div>
              <div>
                <label htmlFor="edit-date-from">Date From</label>
                <input
                  id="edit-date-from"
                  type="date"
                  value={editDateFrom}
                  onChange={(e) => setEditDateFrom(e.target.value)}
                  className="modal-input"
                />
              </div>
              <div>
                <label htmlFor="edit-date-to">Date To</label>
                <input
                  id="edit-date-to"
                  type="date"
                  value={editDateTo}
                  onChange={(e) => setEditDateTo(e.target.value)}
                  className="modal-input"
                />
              </div>
              <div>
                <label htmlFor="edit-note">Note</label>
                <textarea
                  id="edit-note"
                  value={editNote}
                  onChange={(e) => setEditNote(e.target.value)}
                  className="modal-input"
                  style={{ minHeight: "60px" }}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button onClick={handleCloseEdit} className="modal-button">
                Cancel
              </button>
              <button
                onClick={handleUpdateSave}
                className="modal-button modal-button-primary"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- Details Modal --- */}
      {viewingDetails && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Details for {viewingDetails.location_name}</h2>
            <div className="modal-body">
              <p>
                <strong>Date Range:</strong> {viewingDetails.search_date_from}{" "}
                to {viewingDetails.search_date_to}
              </p>
              <p>
                <strong>Note:</strong> {viewingDetails.user_note || "N/A"}
              </p>

              <hr style={{ margin: "15px 0" }} />
              <h4>External Links</h4>
              {viewingDetails.google_maps_url ? (
                <p style={{ margin: "5px 0" }}>
                  <a
                    href={viewingDetails.google_maps_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View on Google Maps
                  </a>
                </p>
              ) : (
                <p style={{ margin: "5px 0" }}>
                  <em>Google Maps link not available.</em>
                </p>
              )}

              {viewingDetails.youtube_video_ids &&
              viewingDetails.youtube_video_ids.length > 0 ? (
                <div>
                  <strong>Related YouTube Videos:</strong>
                  <ul style={{ marginTop: "5px", paddingLeft: "20px" }}>
                    {viewingDetails.youtube_video_ids.map((videoId) => (
                      <li key={videoId} style={{ marginBottom: "5px" }}>
                        <a
                          href={`https://www.youtube.com/watch?v=${videoId}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {`https://www.youtube.com/watch?v=${videoId}`}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : (
                <p style={{ margin: "5px 0" }}>
                  <em>No YouTube videos found.</em>
                </p>
              )}

              <hr style={{ margin: "15px 0" }} />
              <h4>Overall Summary</h4>
              <p style={{ margin: "5px 0" }}>
                <strong>Avg. Temp:</strong>{" "}
                {viewingDetails.summary_avg_temp_c.toFixed(1)}°C
              </p>
              <p style={{ margin: "5px 0" }}>
                <strong>Avg. Humidity:</strong>{" "}
                {viewingDetails.summary_avg_humidity.toFixed(0)}%
              </p>
              <p style={{ margin: "5px 0" }}>
                <strong>Max Wind:</strong>{" "}
                {viewingDetails.summary_max_wind_kph.toFixed(1)} kph
              </p>

              <hr style={{ margin: "15px 0" }} />
              <h4>Day-by-Day Forecast</h4>
              {viewingDetails.raw_forecast_data.forecast.forecastday.map(
                (day: ForecastDay) => (
                  <div
                    key={day.date_epoch}
                    style={{
                      borderBottom: "1px solid #f4f4f4",
                      paddingBottom: "10px",
                      marginBottom: "10px",
                      display: "flex",
                      gap: "10px",
                      alignItems: "center",
                    }}
                  >
                    <img
                      src={`https:${day.day.condition.icon}`}
                      alt={day.day.condition.text}
                      style={{ width: "48px", height: "48px" }}
                    />
                    <div style={{ flex: 1 }}>
                      <strong style={{ fontSize: "1.1em" }}>{day.date}</strong>
                      <p style={{ margin: "4px 0", fontSize: "0.9em" }}>
                        {day.day.condition.text}
                      </p>
                    </div>
                    <div style={{ textAlign: "right", fontSize: "0.9em" }}>
                      <p style={{ margin: "4px 0" }}>
                        <strong>High:</strong> {day.day.maxtemp_c.toFixed(0)}°C
                      </p>
                      <p style={{ margin: "4px 0" }}>
                        <strong>Low:</strong> {day.day.mintemp_c.toFixed(0)}°C
                      </p>
                    </div>
                  </div>
                )
              )}
            </div>
            <div className="modal-footer">
              <button
                onClick={() => setViewingDetails(null)}
                className="modal-button"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- ‼️ NEW: Submission Info Footer ‼️ --- */}
      <hr style={{ margin: "30px 0" }} />
      <footer style={{ color: "#555", fontSize: "0.9em", textAlign: "center" }}>
        <p>
          <strong>Created by:</strong> Youssef Mohammed
          <a
            href="https://www.linkedin.com/in/youssef-mohammed-abdelal"
            target="_blank"
            rel="noopener noreferrer"
          >
            Youssef Mohammed LinkedIn
          </a>
        </p>
        <p>
          <strong>About Product Manager Accelerator (PMA):</strong>
          <br />
          The Product Manager Accelerator Program is designed to support PM
          professionals through every stage of their careers. From students
          looking for entry-level jobs to Directors looking to take on a
          leadership role, our program has helped over hundreds of students
          fulfill their career aspirations. Our Product Manager Accelerator
          community are ambitious and committed. Through our program they have
          learnt, honed and developed new PM and leadership skills, giving them
          a strong foundation for their future endeavors. Here are the examples
          of services we offer. Check out our website (link under my profile) to
          learn more about our services. 🚀 PMA Pro End-to-end product manager
          job hunting program that helps you master FAANG-level Product
          Management skills, conduct unlimited mock interviews, and gain job
          referrals through our largest alumni network. 25% of our offers came
          from tier 1 companies and get paid as high as $800K/year. 🚀 AI PM
          Bootcamp Gain hands-on AI Product Management skills by building a
          real-life AI product with a team of AI Engineers, data scientists, and
          designers. We will also help you launch your product with real user
          engagement using our 100,000+ PM community and social media channels.
          🚀 PMA Power Skills Designed for existing product managers to sharpen
          their product management skills, leadership skills, and executive
          presentation skills 🚀 PMA Leader We help you accelerate your product
          management career, get promoted to Director and product executive
          levels, and win in the board room. 🚀 1:1 Resume Review We help you
          rewrite your killer product manager resume to stand out from the
          crowd, with an interview guarantee.Get started by using our FREE
          killer PM resume template used by over 14,000 product managers.
          https://www.drnancyli.com/pmresume 🚀 We also published over 500+ free
          training and courses. Please go to my YouTube channel
          https://www.youtube.com/c/drnancyli and Instagram @drnancyli to start
          learning for free today.
          <br />
          <a
            href="https://www.linkedin.com/school/productmanagerinterview/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Visit PMA on LinkedIn
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
