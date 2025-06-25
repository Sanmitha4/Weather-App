import sqlite3
import os
from datetime import datetime

def check_weather_database():
    """Comprehensive database checker for weather_forecast_real.db"""
    
    db_path = 'weather_forecast_real.db'
    
    print("🔍 WEATHER DATABASE COMPREHENSIVE CHECKER")
    print("=" * 60)
    print(f"📁 Checking database: {db_path}")
    print("=" * 60)
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print("❌ DATABASE FILE NOT FOUND!")
        print(f"   Expected location: {os.path.abspath(db_path)}")
        print("\n💡 TO CREATE THE DATABASE:")
        print("   1. Run: python weather-forecast-app-*.py")
        print("   2. Search for a few cities")
        print("   3. The database will be created automatically")
        print("\n🔧 OR CREATE MANUALLY:")
        print("   Run: python create_database.py")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # File information
        size = os.path.getsize(db_path)
        modified = datetime.fromtimestamp(os.path.getmtime(db_path))
        
        print("✅ DATABASE FILE FOUND!")
        print(f"   📁 Path: {os.path.abspath(db_path)}")
        print(f"   💾 Size: {size:,} bytes ({size/1024:.1f} KB)")
        print(f"   📅 Last Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📊 TABLES FOUND: {len(tables)}")
        print("-" * 40)
        
        expected_tables = ['weather_history', 'weather_forecast']
        
        for table_name, in tables:
            print(f"📋 Table: {table_name}")
            
            # Check if it's an expected table
            if table_name in expected_tables:
                print("   ✅ Expected table")
                expected_tables.remove(table_name)
            else:
                print("   ⚠️  Unexpected table")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"   📝 Columns: {len(columns)}")
            
            for col in columns:
                cid, name, col_type, notnull, default_val, pk = col
                pk_str = " (PRIMARY KEY)" if pk else ""
                null_str = " NOT NULL" if notnull else ""
                default_str = f" DEFAULT {default_val}" if default_val else ""
                print(f"      • {name}: {col_type}{pk_str}{null_str}{default_str}")
            
            # Count records
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📈 Records: {count:,}")
            
            # Show sample data if exists
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                samples = cursor.fetchall()
                print(f"   🔍 Sample data (first 3 records):")
                for i, sample in enumerate(samples, 1):
                    print(f"      {i}. {sample}")
            
            print()
        
        # Check for missing expected tables
        if expected_tables:
            print("❌ MISSING EXPECTED TABLES:")
            for missing_table in expected_tables:
                print(f"   • {missing_table}")
            print()
        
        # Detailed analysis for weather_history table
        if 'weather_history' in [t[0] for t in tables]:
            print("📈 WEATHER HISTORY ANALYSIS:")
            print("-" * 30)
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM weather_history")
            total_records = cursor.fetchone()[0]
            print(f"   Total Records: {total_records:,}")
            
            if total_records > 0:
                # Unique cities
                cursor.execute("SELECT COUNT(DISTINCT city) FROM weather_history")
                unique_cities = cursor.fetchone()[0]
                print(f"   Unique Cities: {unique_cities}")
                
                # Date range
                cursor.execute("SELECT MIN(searched_at), MAX(searched_at) FROM weather_history WHERE searched_at IS NOT NULL")
                date_range = cursor.fetchone()
                if date_range[0]:
                    print(f"   Date Range: {date_range[0]} to {date_range[1]}")
                
                # Temperature stats
                cursor.execute("SELECT MIN(temperature), MAX(temperature), AVG(temperature) FROM weather_history WHERE temperature IS NOT NULL")
                temp_stats = cursor.fetchone()
                if temp_stats[0] is not None:
                    print(f"   Temperature Range: {temp_stats[0]:.1f}°C to {temp_stats[1]:.1f}°C (Avg: {temp_stats[2]:.1f}°C)")
                
                # Most searched cities
                cursor.execute("""
                    SELECT city, COUNT(*) as searches 
                    FROM weather_history 
                    GROUP BY city 
                    ORDER BY searches DESC 
                    LIMIT 5
                """)
                top_cities = cursor.fetchall()
                print("   Top 5 Searched Cities:")
                for i, (city, searches) in enumerate(top_cities, 1):
                    print(f"      {i}. {city}: {searches} searches")
            
            print()
        
        # Detailed analysis for weather_forecast table
        if 'weather_forecast' in [t[0] for t in tables]:
            print("📅 WEATHER FORECAST ANALYSIS:")
            print("-" * 30)
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM weather_forecast")
            total_forecasts = cursor.fetchone()[0]
            print(f"   Total Forecast Records: {total_forecasts:,}")
            
            if total_forecasts > 0:
                # Cities with forecasts
                cursor.execute("SELECT COUNT(DISTINCT city) FROM weather_forecast")
                forecast_cities = cursor.fetchone()[0]
                print(f"   Cities with Forecasts: {forecast_cities}")
                
                # Forecast temperature range
                cursor.execute("SELECT MIN(low_temp), MAX(high_temp), AVG(high_temp), AVG(low_temp) FROM weather_forecast WHERE high_temp IS NOT NULL")
                forecast_temps = cursor.fetchone()
                if forecast_temps[0] is not None:
                    print(f"   Temperature Range: {forecast_temps[0]:.1f}°C to {forecast_temps[1]:.1f}°C")
                    print(f"   Average High: {forecast_temps[2]:.1f}°C, Average Low: {forecast_temps[3]:.1f}°C")
                
                # Forecasts by city
                cursor.execute("""
                    SELECT city, COUNT(*) as forecast_days 
                    FROM weather_forecast 
                    GROUP BY city 
                    ORDER BY forecast_days DESC
                """)
                forecast_by_city = cursor.fetchall()
                print("   Forecasts by City:")
                for city, days in forecast_by_city:
                    print(f"      • {city}: {days} days")
            
            print()
        
        # Database integrity checks
        print("🔧 DATABASE INTEGRITY CHECKS:")
        print("-" * 30)
        
        # Check for foreign key violations (if any foreign keys exist)
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        if fk_violations:
            print("   ❌ Foreign key violations found:")
            for violation in fk_violations:
                print(f"      {violation}")
        else:
            print("   ✅ No foreign key violations")
        
        # Check for duplicate records in history
        cursor.execute("""
            SELECT city, temperature, condition, searched_at, COUNT(*) as duplicates
            FROM weather_history 
            GROUP BY city, temperature, condition, searched_at
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"   ⚠️  Found {len(duplicates)} potential duplicate records in weather_history")
        else:
            print("   ✅ No duplicate records found in weather_history")
        
        # Check for NULL values in important fields
        cursor.execute("SELECT COUNT(*) FROM weather_history WHERE city IS NULL OR temperature IS NULL")
        null_important = cursor.fetchone()[0]
        if null_important > 0:
            print(f"   ⚠️  Found {null_important} records with NULL city or temperature")
        else:
            print("   ✅ No NULL values in critical fields")
        
        print()
        
        # Performance analysis
        print("⚡ PERFORMANCE ANALYSIS:")
        print("-" * 25)
        
        # Check for indexes
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
        indexes = cursor.fetchall()
        if indexes:
            print(f"   📊 Custom Indexes: {len(indexes)}")
            for name, sql in indexes:
                print(f"      • {name}")
        else:
            print("   ⚠️  No custom indexes found (may affect query performance)")
        
        # Database page size and other settings
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        
        print(f"   📄 Page Size: {page_size} bytes")
        print(f"   📄 Page Count: {page_count:,}")
        print(f"   💾 Database Size: {page_size * page_count:,} bytes")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE CHECK COMPLETED SUCCESSFULLY!")
        print("💡 Use 'python database_viewer.py' for advanced database management")
        print("=" * 60)
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def create_database_if_missing():
    """Create the database with proper structure if it doesn't exist"""
    
    db_path = 'weather_forecast_real.db'
    
    if os.path.exists(db_path):
        print("✅ Database already exists!")
        return True
    
    print("🔧 Creating new weather database...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create weather_history table
        cursor.execute('''
            CREATE TABLE weather_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                country TEXT,
                temperature REAL NOT NULL,
                condition TEXT NOT NULL,
                description TEXT,
                humidity INTEGER,
                wind_speed REAL,
                pressure INTEGER,
                feels_like REAL,
                visibility INTEGER,
                uv_index REAL,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create weather_forecast table
        cursor.execute('''
            CREATE TABLE weather_forecast (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                day_name TEXT NOT NULL,
                forecast_date DATE,
                high_temp REAL NOT NULL,
                low_temp REAL NOT NULL,
                condition TEXT NOT NULL,
                description TEXT,
                humidity INTEGER,
                wind_speed REAL,
                precipitation_chance INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create useful indexes
        cursor.execute('CREATE INDEX idx_weather_history_city ON weather_history(city)')
        cursor.execute('CREATE INDEX idx_weather_history_date ON weather_history(searched_at)')
        cursor.execute('CREATE INDEX idx_weather_forecast_city ON weather_forecast(city)')
        cursor.execute('CREATE INDEX idx_weather_forecast_date ON weather_forecast(forecast_date)')
        
        conn.commit()
        conn.close()
        
        print("✅ Database created successfully!")
        print(f"📁 Location: {os.path.abspath(db_path)}")
        print("📊 Tables created: weather_history, weather_forecast")
        print("📈 Indexes created for better performance")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def main():
    print("🌤️ Weather Database Checker & Creator")
    print("=" * 50)
    
    # Check if database exists and analyze it
    if not check_weather_database():
        print("\n" + "=" * 50)
        create_choice = input("Would you like to create the database now? (y/n): ")
        if create_choice.lower() == 'y':
            if create_database_if_missing():
                print("\n" + "=" * 50)
                print("🔄 Re-checking the newly created database...")
                check_weather_database()
    
    print("\n🛠️  AVAILABLE TOOLS:")
    print("1. python weather-forecast-app-*.py  - Main weather app")
    print("2. python database_viewer.py         - Advanced database manager")
    print("3. python database_checker.py        - This checker tool")
    print("\n💡 TIP: Use the database viewer for comprehensive data management!")

if __name__ == "__main__":
    main()