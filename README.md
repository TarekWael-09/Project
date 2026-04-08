# 🌤️ Weather Data Pipeline System

An **ETL Pipeline project** for collecting, processing, and analyzing weather data using the **OpenWeatherMap API**.  
The system automatically fetches weather information for multiple cities, validates the data, stores it in a database, and generates reports and alerts.

---

# 📁 Project Structure

```
weather_pipeline/
├── config.py          # Configuration (API Key, cities, alert thresholds)
├── database.py        # SQLite database setup and connection
├── api_client.py      # Communication with OpenWeatherMap API
├── validator.py       # Data quality validation
├── etl_pipeline.py    # Main ETL pipeline logic
├── reporter.py        # Reports and statistics generator
├── monitor.py         # System health monitoring
├── scheduler.py       # Automatic scheduling for pipeline runs
├── main.py            # Main entry point
├── requirements.txt   # Required Python libraries
├── database/          # Database files
├── logs/              # Log files
└── reports/           # Generated reports
```

---

# 🚀 How to Run the Project

## 1️⃣ Install Dependencies

Make sure Python is installed, then run:

```bash
pip install -r requirements.txt
```

---

## 2️⃣ Add Your API Key

Open the file:

```
config.py
```

Replace this line:

```python
API_KEY = "YOUR_API_KEY_HERE"
```

with your **OpenWeatherMap API Key**.

### Alternative (Environment Variable)

```bash
export OPENWEATHER_API_KEY="your_key_here"
```

---

## 3️⃣ Run the Application

### Interactive Menu

```bash
python main.py
```

### Direct Commands

Run the pipeline once:

```bash
python main.py run
```

Generate a weather report:

```bash
python main.py report
```

Check system health:

```bash
python main.py monitor
```

Start automatic scheduling:

```bash
python main.py schedule
```

---

# 🗄️ Database Schema

The system uses **SQLite** with the following tables:

| Table | Description |
|------|-------------|
| cities | List of monitored cities |
| weather_data | Stored weather records |
| alerts | Generated weather alerts |
| pipeline_runs | Logs of pipeline executions |

---

# ⚙️ Configuration (config.py)

You can customize the pipeline behavior inside `config.py`.

Example:

```python
CITIES = ["Cairo", "Dubai", "London"]

COLLECTION_INTERVAL_MINUTES = 30

ALERTS = {
    "high_temp": 35,
    "high_humidity": 90
}
```

### Configuration Options

| Setting | Description |
|-------|-------------|
| CITIES | Cities to collect weather data for |
| COLLECTION_INTERVAL_MINUTES | Time between each pipeline run |
| ALERTS | Thresholds for generating alerts |

---

# 📊 ETL Pipeline Stages

The system follows the **ETL process**:

### 1️⃣ Extract
Fetch weather data from the **OpenWeatherMap API**.

### 2️⃣ Transform
Clean the data and validate its structure and values.

### 3️⃣ Load
Store the processed data in the **SQLite database** and check for alerts.

---

# 📈 Features

- Automated **weather data collection**
- **ETL pipeline architecture**
- **Data validation**
- **SQLite database storage**
- **Weather alert system**
- **System monitoring**
- **Scheduled data collection**
- **Report generation**

---

# 🔑 How to Get a Free API Key

1. Go to  
https://openweathermap.org

2. Create an account.

3. Navigate to **API Keys** in your dashboard.

4. Copy your key and paste it into `config.py`.

5. Wait **10–15 minutes** for activation.

---

# 📌 Technologies Used

- Python
- SQLite
- OpenWeatherMap API
- Logging
- Scheduling
- ETL Data Pipeline Architecture

---

# 📄 License

This project is for **educational and learning purposes**.