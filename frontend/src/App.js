import React, { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [url, setUrl] = useState("");
  const [images, setImages] = useState([]);
  const [importSource, setImportSource] = useState("google_drive");
  const [filterSource, setFilterSource] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const fetchImages = async () => {
    try {
      const endpoint =
        filterSource === "all"
          ? `${API_URL}/images`
          : `${API_URL}/images/source/${filterSource}`;

      const res = await axios.get(endpoint);
      setImages(res.data || []);
    } catch (err) {
      setError("Failed to load images");
    }
  };

  useEffect(() => {
    fetchImages();
  }, [filterSource]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!url.trim()) {
      setError("Please enter a valid folder URL");
      return;
    }

    try {
      setLoading(true);

      const endpoint =
        importSource === "google_drive"
          ? `${API_URL}/import/google-drive`
          : `${API_URL}/import/dropbox`;

          // ✅ send URL as query param

        await axios.post(
         `${endpoint}?url=${encodeURIComponent(url)}`,
          {}, // empty body
          { headers: { "Content-Type": "application/json" } }
   );

      setSuccess("Import started successfully");
      setUrl("");
      fetchImages();
    } catch (err) {
      setError("Import failed. Please check URL or backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>📥 Image Importer</h1>

      <form className="card" onSubmit={handleSubmit}>
        <div className="row">
          <select
            value={importSource}
            onChange={(e) => setImportSource(e.target.value)}
          >
            <option value="google_drive">Google Drive</option>
            <option value="dropbox">Dropbox</option>
          </select>

          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste folder URL here"
          />

          <button disabled={loading}>
            {loading ? "Importing..." : "Import"}
          </button>
        </div>

        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}
      </form>

      <div className="card">
        <h2>🖼 Imported Images</h2>

        <select
          value={filterSource}
          onChange={(e) => setFilterSource(e.target.value)}
        >
          <option value="all">All</option>
          <option value="google_drive">Google Drive</option>
          <option value="dropbox">Dropbox</option>
        </select>

        <div className="grid">
          {images.length === 0 && <p>No images found</p>}

          {images.map((img) => (
            <div className="image-card" key={img.id}>
              <img src={img.storage_path} alt={img.name} />
              <p>{img.name}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
