#🌤️ Weather Forecasting App

A comprehensive Python desktop application for weather forecasting with real-time data, 7-day forecasts, and intelligent search history management.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)
![OpenWeather](https://img.shields.io/badge/API-OpenWeather-yellow.svg)

### 🏠 **Main Weather App**
- **Current Weather Display** - Real-time weather data with detailed metrics
- **7-Day Forecast** - Prominent weekly weather outlook with visual cards
- **Tab-Based Interface** - Clean navigation between Home, Search, and History
- **Search Functionality** - Find weather for any city worldwide
- **SQLite Database** - Automatic storage of search history and forecasts
- **Responsive Design** - Large, readable interface with improved box sizes
  
  ### 📊 **Database Management Tools**
- **Database Viewer** - Advanced GUI tool for data exploration
- **Statistics Dashboard** - Comprehensive weather data analytics
- **Export Functionality** - CSV export for data analysis
- **SQL Query Tool** - Execute custom database queries
- **Data Integrity Checks** - Automated database health monitoring

  ### 🔧 **Utility Tools**
- **Database Checker** - Comprehensive database analysis and validation
- **Schema Viewer** - Explore database structure and relationships

 ### **Preview**
  ![image](https://github.com/user-attachments/assets/e3c32ff1-c660-44fb-8de3-d813ecfeee07)
![image](https://github.com/user-attachments/assets/cec5307c-f0dd-49b3-9f70-af33db63b035)

### Installation

**Install dependencies**
   ```bash
   pip install requests
   ```

**Get OpenWeather API Key** (Optional for live data)
   - Visit [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up for a free account
   - Get your API key
   - Replace `YOUR_API_KEY_HERE` in the code
     
**Run the application**
   ```bash
   python weather_app.py
   ```

## 📱 Application Components
- **Home Tab**: Current weather + 7-day forecast
- **Search Tab**: Dedicated city search interface  
- **History Tab**: Complete search history in grid layout
- **Demo Mode**: Works without API key using sample data

  ### 🗄️ Database Viewer
```bash
python database_viewer.py
```
- View and manage all weather data
- Export data to CSV format
- Execute custom SQL queries
- Generate detailed statistics
- Database schema exploration

### 🔍 Database Checker
```bash
python database_checker.py
```
- Comprehensive database analysis
- Data integrity validation
- Performance metrics
- Automatic database creation

## 🗃️ Database Schema

### Weather History Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| city | TEXT | City name |
| temperature | REAL | Temperature in Celsius |
| condition | TEXT | Weather condition |
| humidity | INTEGER | Humidity percentage |
| wind_speed | REAL | Wind speed in km/h |
| searched_at | TIMESTAMP | Search timestamp |

### Weather Forecast Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| city | TEXT | City name |
| day_name | TEXT | Day of week |
| forecast_date | DATE | Forecast date |
| high_temp | REAL | High temperature |
| low_temp | REAL | Low temperature |
| condition | TEXT | Weather condition |
| created_at | TIMESTAMP | Creation timestamp |

## 🎯 Usage Examples

### Basic Weather Search
1. Launch the main application
2. Navigate to the **Search** tab
3. Enter a city name
4. View results on the **Home** tab
5. Check **History** tab for past searches

### Database Management
1. Run the database viewer tool
2. Explore data in different tabs
3. Export data using the "Export All CSV" button
4. Use SQL Query tool for custom analysis

### Data Analysis
1. Use the database checker for comprehensive analysis
2. View statistics in the database viewer
3. Export data for external analysis tools

## 🔧 Configuration

### API Configuration
Edit the main application file and replace:
```python
self.api_key = "YOUR_API_KEY_HERE"
```
### Database Location
The SQLite database is created as `weather_forecast_real.db` in the application directory.

### Project Structure
```
weather-forecasting-app/
├── weather_app.py          # Main application
├── database_viewer.py       # Database management tool
├── database_checker.py        # Database checker utility
├── weather_forecast_real.db           # SQLite database (auto-created)
├── README.md                          # This file
└── requirements.txt                   # Python dependencies
```
## 📄 License

This project is open source and available under the [MIT License](LICENSE).

##  Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) for weather data API
- Python tkinter for the GUI framework
- SQLite for reliable data storage


  
