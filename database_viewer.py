import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import os

class WeatherDatabaseViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Database Viewer & Manager")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f0f0')
        
        self.db_path = 'weather_forecast_real.db'
        
        self.create_widgets()
        self.refresh_all_data()
        
    def create_widgets(self):
        """Create the database viewer interface"""
        
        # Title and database info
        title_frame = tk.Frame(self.root, bg='#2196f3', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🗄️ Weather Database Viewer & Manager",
            font=("Arial", 24, "bold"),
            bg='#2196f3',
            fg='white'
        )
        title_label.pack(expand=True)
        
        # Database status frame
        status_frame = tk.LabelFrame(
            self.root,
            text="Database Status",
            font=("Arial", 12, "bold"),
            bg='#f0f0f0',
            fg='#333'
        )
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="",
            font=("Arial", 11),
            bg='#f0f0f0',
            justify='left',
            anchor='w'
        )
        self.status_label.pack(fill='x', padx=10, pady=10)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(fill='x', padx=20, pady=10)
        
        # Left side buttons
        left_buttons = tk.Frame(control_frame, bg='#f0f0f0')
        left_buttons.pack(side='left')
        
        tk.Button(
            left_buttons,
            text="🔄 Refresh All",
            command=self.refresh_all_data,
            bg='#4caf50',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            left_buttons,
            text="📊 Export All CSV",
            command=self.export_all_csv,
            bg='#2196f3',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            left_buttons,
            text="🗑️ Clear History",
            command=self.clear_history,
            bg='#f44336',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            left_buttons,
            text="🗑️ Clear Forecasts",
            command=self.clear_forecasts,
            bg='#ff9800',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        # Right side buttons
        right_buttons = tk.Frame(control_frame, bg='#f0f0f0')
        right_buttons.pack(side='right')
        
        tk.Button(
            right_buttons,
            text="➕ Add Sample Data",
            command=self.add_sample_data,
            bg='#9c27b0',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            right_buttons,
            text="🔍 SQL Query",
            command=self.open_sql_query,
            bg='#607d8b',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Weather History Tab
        self.create_history_tab()
        
        # Weather Forecast Tab
        self.create_forecast_tab()
        
        # Statistics Tab
        self.create_statistics_tab()
        
        # Database Schema Tab
        self.create_schema_tab()
        
    def create_history_tab(self):
        """Create weather history tab"""
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="📈 Weather History")
        
        # Search frame
        search_frame = tk.Frame(self.history_frame, bg='white')
        search_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(search_frame, text="🔍 Search City:", font=("Arial", 10, "bold"), bg='white').pack(side='left', padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 10), width=20)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<KeyRelease>', self.filter_history)
        
        tk.Button(
            search_frame,
            text="Clear Filter",
            command=self.clear_filter,
            bg='#757575',
            fg='white',
            font=("Arial", 9),
            padx=10
        ).pack(side='left', padx=5)
        
        # History treeview
        history_columns = (
            'ID', 'City', 'Country', 'Temperature', 'Condition', 'Description',
            'Humidity', 'Wind Speed', 'Pressure', 'Feels Like', 'Visibility', 'Search Date'
        )
        
        self.history_tree = ttk.Treeview(self.history_frame, columns=history_columns, show='headings', height=20)
        
        # Configure columns
        column_widths = {
            'ID': 50, 'City': 100, 'Country': 60, 'Temperature': 80, 'Condition': 80,
            'Description': 120, 'Humidity': 70, 'Wind Speed': 80, 'Pressure': 70,
            'Feels Like': 80, 'Visibility': 70, 'Search Date': 150
        }
        
        for col in history_columns:
            self.history_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.history_tree, c))
            self.history_tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        # Scrollbars for history
        history_v_scroll = ttk.Scrollbar(self.history_frame, orient='vertical', command=self.history_tree.yview)
        history_h_scroll = ttk.Scrollbar(self.history_frame, orient='horizontal', command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=history_v_scroll.set, xscrollcommand=history_h_scroll.set)
        
        # Pack history components
        self.history_tree.pack(side='left', fill='both', expand=True)
        history_v_scroll.pack(side='right', fill='y')
        history_h_scroll.pack(side='bottom', fill='x')
        
        # History context menu
        self.history_menu = tk.Menu(self.root, tearoff=0)
        self.history_menu.add_command(label="Delete Selected", command=self.delete_history_record)
        self.history_menu.add_command(label="View Details", command=self.view_history_details)
        
        self.history_tree.bind("<Button-3>", self.show_history_context_menu)
        
    def create_forecast_tab(self):
        """Create weather forecast tab"""
        self.forecast_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forecast_frame, text="📅 7-Day Forecasts")
        
        # Forecast filter frame
        filter_frame = tk.Frame(self.forecast_frame, bg='white')
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(filter_frame, text="🏙️ Filter by City:", font=("Arial", 10, "bold"), bg='white').pack(side='left', padx=5)
        
        self.forecast_filter = ttk.Combobox(filter_frame, font=("Arial", 10), width=20, state='readonly')
        self.forecast_filter.pack(side='left', padx=5)
        self.forecast_filter.bind('<<ComboboxSelected>>', self.filter_forecasts)
        
        tk.Button(
            filter_frame,
            text="Show All",
            command=self.show_all_forecasts,
            bg='#4caf50',
            fg='white',
            font=("Arial", 9),
            padx=10
        ).pack(side='left', padx=5)
        
        # Forecast treeview
        forecast_columns = (
            'ID', 'City', 'Day', 'Date', 'High Temp', 'Low Temp', 'Condition',
            'Description', 'Humidity', 'Wind Speed', 'Precipitation %', 'Created At'
        )
        
        self.forecast_tree = ttk.Treeview(self.forecast_frame, columns=forecast_columns, show='headings', height=20)
        
        # Configure forecast columns
        forecast_widths = {
            'ID': 50, 'City': 100, 'Day': 60, 'Date': 100, 'High Temp': 80,
            'Low Temp': 80, 'Condition': 80, 'Description': 120, 'Humidity': 70,
            'Wind Speed': 80, 'Precipitation %': 100, 'Created At': 150
        }
        
        for col in forecast_columns:
            self.forecast_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.forecast_tree, c))
            self.forecast_tree.column(col, width=forecast_widths.get(col, 100), minwidth=50)
        
        # Scrollbars for forecast
        forecast_v_scroll = ttk.Scrollbar(self.forecast_frame, orient='vertical', command=self.forecast_tree.yview)
        forecast_h_scroll = ttk.Scrollbar(self.forecast_frame, orient='horizontal', command=self.forecast_tree.xview)
        self.forecast_tree.configure(yscrollcommand=forecast_v_scroll.set, xscrollcommand=forecast_h_scroll.set)
        
        # Pack forecast components
        self.forecast_tree.pack(side='left', fill='both', expand=True)
        forecast_v_scroll.pack(side='right', fill='y')
        forecast_h_scroll.pack(side='bottom', fill='x')
        
        # Forecast context menu
        self.forecast_menu = tk.Menu(self.root, tearoff=0)
        self.forecast_menu.add_command(label="Delete Selected", command=self.delete_forecast_record)
        self.forecast_menu.add_command(label="Delete All for City", command=self.delete_city_forecasts)
        
        self.forecast_tree.bind("<Button-3>", self.show_forecast_context_menu)
        
    def create_statistics_tab(self):
        """Create statistics tab"""
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📊 Statistics")
        
        # Statistics text widget
        self.stats_text = tk.Text(
            self.stats_frame,
            font=("Courier New", 11),
            bg='white',
            fg='#333',
            wrap='word'
        )
        
        stats_scroll = ttk.Scrollbar(self.stats_frame, orient='vertical', command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scroll.set)
        
        self.stats_text.pack(side='left', fill='both', expand=True)
        stats_scroll.pack(side='right', fill='y')
        
    def create_schema_tab(self):
        """Create database schema tab"""
        self.schema_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.schema_frame, text="🏗️ Database Schema")
        
        # Schema text widget
        self.schema_text = tk.Text(
            self.schema_frame,
            font=("Courier New", 11),
            bg='#f8f8f8',
            fg='#333',
            wrap='word'
        )
        
        schema_scroll = ttk.Scrollbar(self.schema_frame, orient='vertical', command=self.schema_text.yview)
        self.schema_text.configure(yscrollcommand=schema_scroll.set)
        
        self.schema_text.pack(side='left', fill='both', expand=True)
        schema_scroll.pack(side='right', fill='y')
        
    def refresh_all_data(self):
        """Refresh all data from database"""
        self.update_database_status()
        self.load_history_data()
        self.load_forecast_data()
        self.update_statistics()
        self.update_schema_info()
        self.update_forecast_filter()
        
    def update_database_status(self):
        """Update database status information"""
        if not os.path.exists(self.db_path):
            status_text = f"❌ Database file '{self.db_path}' not found!\n"
            status_text += "💡 Run the weather app first to create the database."
            self.status_label.config(text=status_text, fg='red')
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get file info
            size = os.path.getsize(self.db_path)
            size_kb = size / 1024
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM weather_history")
            history_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM weather_forecast")
            forecast_count = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute("SELECT MIN(searched_at), MAX(searched_at) FROM weather_history WHERE searched_at IS NOT NULL")
            date_range = cursor.fetchone()
            
            status_text = f"✅ Database: {self.db_path} | Size: {size_kb:.1f} KB | "
            status_text += f"History: {history_count} records | Forecasts: {forecast_count} records"
            
            if date_range[0]:
                status_text += f" | Range: {date_range[0][:10]} to {date_range[1][:10]}"
            
            self.status_label.config(text=status_text, fg='green')
            conn.close()
            return True
            
        except Exception as e:
            self.status_label.config(text=f"❌ Database error: {str(e)}", fg='red')
            return False
    
    def load_history_data(self, filter_city=None):
        """Load weather history data"""
        # Clear existing data
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        if not os.path.exists(self.db_path):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if filter_city:
                cursor.execute("""
                    SELECT id, city, country, temperature, condition, description,
                           humidity, wind_speed, pressure, feels_like, visibility, searched_at
                    FROM weather_history 
                    WHERE city LIKE ?
                    ORDER BY searched_at DESC
                """, (f'%{filter_city}%',))
            else:
                cursor.execute("""
                    SELECT id, city, country, temperature, condition, description,
                           humidity, wind_speed, pressure, feels_like, visibility, searched_at
                    FROM weather_history 
                    ORDER BY searched_at DESC
                """)
            
            for row in cursor.fetchall():
                # Format the data for display
                formatted_row = list(row)
                
                # Format temperature
                if formatted_row[3]: formatted_row[3] = f"{formatted_row[3]:.1f}°C"
                if formatted_row[6]: formatted_row[6] = f"{formatted_row[6]}%"
                if formatted_row[7]: formatted_row[7] = f"{formatted_row[7]:.1f} km/h"
                if formatted_row[8]: formatted_row[8] = f"{formatted_row[8]} hPa"
                if formatted_row[9]: formatted_row[9] = f"{formatted_row[9]:.1f}°C"
                if formatted_row[10]: formatted_row[10] = f"{formatted_row[10]} km"
                
                # Format timestamp
                if formatted_row[11]:
                    try:
                        dt = datetime.fromisoformat(formatted_row[11].replace('Z', '+00:00') if 'Z' in formatted_row[11] else formatted_row[11])
                        formatted_row[11] = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                self.history_tree.insert('', 'end', values=formatted_row)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading history data: {str(e)}")
    
    def load_forecast_data(self, filter_city=None):
        """Load forecast data"""
        # Clear existing data
        for item in self.forecast_tree.get_children():
            self.forecast_tree.delete(item)
        
        if not os.path.exists(self.db_path):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if filter_city:
                cursor.execute("""
                    SELECT id, city, day_name, forecast_date, high_temp, low_temp, condition,
                           description, humidity, wind_speed, precipitation_chance, created_at
                    FROM weather_forecast 
                    WHERE city = ?
                    ORDER BY city, forecast_date
                """, (filter_city,))
            else:
                cursor.execute("""
                    SELECT id, city, day_name, forecast_date, high_temp, low_temp, condition,
                           description, humidity, wind_speed, precipitation_chance, created_at
                    FROM weather_forecast 
                    ORDER BY city, forecast_date
                """)
            
            for row in cursor.fetchall():
                # Format the data for display
                formatted_row = list(row)
                
                # Format temperatures
                if formatted_row[4]: formatted_row[4] = f"{formatted_row[4]:.1f}°C"
                if formatted_row[5]: formatted_row[5] = f"{formatted_row[5]:.1f}°C"
                if formatted_row[8]: formatted_row[8] = f"{formatted_row[8]}%"
                if formatted_row[9]: formatted_row[9] = f"{formatted_row[9]:.1f} km/h"
                if formatted_row[10]: formatted_row[10] = f"{formatted_row[10]}%"
                
                # Format timestamps
                if formatted_row[11]:
                    try:
                        dt = datetime.fromisoformat(formatted_row[11].replace('Z', '+00:00') if 'Z' in formatted_row[11] else formatted_row[11])
                        formatted_row[11] = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                self.forecast_tree.insert('', 'end', values=formatted_row)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading forecast data: {str(e)}")
    
    def update_statistics(self):
        """Update statistics display"""
        self.stats_text.delete(1.0, tk.END)
        
        if not os.path.exists(self.db_path):
            self.stats_text.insert(tk.END, "❌ Database not found. Run the weather app first.")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = "📊 WEATHER DATABASE STATISTICS\n"
            stats += "=" * 60 + "\n\n"
            
            # History statistics
            cursor.execute("SELECT COUNT(*) FROM weather_history")
            total_searches = cursor.fetchone()[0]
            stats += f"📈 WEATHER HISTORY:\n"
            stats += f"   Total Searches: {total_searches}\n"
            
            if total_searches > 0:
                cursor.execute("SELECT COUNT(DISTINCT city) FROM weather_history")
                unique_cities = cursor.fetchone()[0]
                stats += f"   Unique Cities: {unique_cities}\n"
                
                cursor.execute("SELECT AVG(temperature), MIN(temperature), MAX(temperature) FROM weather_history WHERE temperature IS NOT NULL")
                temp_stats = cursor.fetchone()
                if temp_stats[0]:
                    stats += f"   Temperature - Avg: {temp_stats[0]:.1f}°C, Min: {temp_stats[1]:.1f}°C, Max: {temp_stats[2]:.1f}°C\n"
                
                cursor.execute("SELECT AVG(humidity), AVG(wind_speed), AVG(pressure) FROM weather_history WHERE humidity IS NOT NULL")
                other_stats = cursor.fetchone()
                if other_stats[0]:
                    stats += f"   Avg Humidity: {other_stats[0]:.1f}%, Avg Wind: {other_stats[1]:.1f} km/h, Avg Pressure: {other_stats[2]:.0f} hPa\n"
                
                # Most searched cities
                cursor.execute("""
                    SELECT city, COUNT(*) as search_count 
                    FROM weather_history 
                    GROUP BY city 
                    ORDER BY search_count DESC 
                    LIMIT 10
                """)
                
                stats += f"\n🏆 TOP 10 MOST SEARCHED CITIES:\n"
                for i, (city, count) in enumerate(cursor.fetchall(), 1):
                    stats += f"   {i:2d}. {city:<20} {count:3d} searches\n"
                
                # Weather conditions distribution
                cursor.execute("""
                    SELECT condition, COUNT(*) as count 
                    FROM weather_history 
                    WHERE condition IS NOT NULL
                    GROUP BY condition 
                    ORDER BY count DESC
                """)
                
                stats += f"\n🌤️  WEATHER CONDITIONS:\n"
                conditions = cursor.fetchall()
                for condition, count in conditions:
                    percentage = (count / total_searches) * 100
                    stats += f"   {condition:<15} {count:3d} ({percentage:5.1f}%)\n"
            
            # Forecast statistics
            cursor.execute("SELECT COUNT(*) FROM weather_forecast")
            total_forecasts = cursor.fetchone()[0]
            stats += f"\n📅 FORECAST DATA:\n"
            stats += f"   Total Forecast Records: {total_forecasts}\n"
            
            if total_forecasts > 0:
                cursor.execute("SELECT COUNT(DISTINCT city) FROM weather_forecast")
                forecast_cities = cursor.fetchone()[0]
                stats += f"   Cities with Forecasts: {forecast_cities}\n"
                
                cursor.execute("SELECT AVG(high_temp), AVG(low_temp), MIN(low_temp), MAX(high_temp) FROM weather_forecast WHERE high_temp IS NOT NULL")
                forecast_temps = cursor.fetchone()
                if forecast_temps[0]:
                    stats += f"   Forecast Temps - Avg High: {forecast_temps[0]:.1f}°C, Avg Low: {forecast_temps[1]:.1f}°C\n"
                    stats += f"   Temperature Range: {forecast_temps[2]:.1f}°C to {forecast_temps[3]:.1f}°C\n"
                
                # Forecast by city
                cursor.execute("""
                    SELECT city, COUNT(*) as forecast_count 
                    FROM weather_forecast 
                    GROUP BY city 
                    ORDER BY forecast_count DESC
                """)
                
                stats += f"\n🏙️  FORECASTS BY CITY:\n"
                for city, count in cursor.fetchall():
                    stats += f"   {city:<20} {count:2d} days\n"
            
            # Recent activity
            cursor.execute("""
                SELECT city, searched_at 
                FROM weather_history 
                WHERE searched_at IS NOT NULL
                ORDER BY searched_at DESC 
                LIMIT 5
            """)
            
            stats += f"\n🕒 RECENT SEARCHES:\n"
            recent = cursor.fetchall()
            if recent:
                for city, timestamp in recent:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00') if 'Z' in timestamp else timestamp)
                        time_str = dt.strftime("%Y-%m-%d %H:%M")
                        stats += f"   {city:<20} {time_str}\n"
                    except:
                        stats += f"   {city:<20} {timestamp}\n"
            else:
                stats += "   No recent searches found\n"
            
            conn.close()
            self.stats_text.insert(tk.END, stats)
            
        except Exception as e:
            self.stats_text.insert(tk.END, f"❌ Error generating statistics: {str(e)}")
    
    def update_schema_info(self):
        """Update database schema information"""
        self.schema_text.delete(1.0, tk.END)
        
        if not os.path.exists(self.db_path):
            self.schema_text.insert(tk.END, "❌ Database not found.")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            schema_info = "🏗️  DATABASE SCHEMA INFORMATION\n"
            schema_info += "=" * 60 + "\n\n"
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table_name, in tables:
                schema_info += f"📋 TABLE: {table_name.upper()}\n"
                schema_info += "-" * 40 + "\n"
                
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                schema_info += f"{'Column':<20} {'Type':<15} {'Null':<8} {'Default':<15} {'PK'}\n"
                schema_info += "-" * 70 + "\n"
                
                for col in columns:
                    cid, name, col_type, notnull, default_val, pk = col
                    null_str = "NOT NULL" if notnull else "NULL"
                    default_str = str(default_val) if default_val else ""
                    pk_str = "YES" if pk else ""
                    
                    schema_info += f"{name:<20} {col_type:<15} {null_str:<8} {default_str:<15} {pk_str}\n"
                
                # Get record count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                schema_info += f"\nRecord Count: {count}\n\n"
            
            # Get indexes
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
            indexes = cursor.fetchall()
            
            if indexes:
                schema_info += "📊 INDEXES:\n"
                schema_info += "-" * 20 + "\n"
                for name, sql in indexes:
                    schema_info += f"{name}: {sql}\n"
                schema_info += "\n"
            
            # Database file info
            schema_info += "📁 FILE INFORMATION:\n"
            schema_info += "-" * 20 + "\n"
            size = os.path.getsize(self.db_path)
            schema_info += f"File Path: {os.path.abspath(self.db_path)}\n"
            schema_info += f"File Size: {size:,} bytes ({size/1024:.1f} KB)\n"
            schema_info += f"Last Modified: {datetime.fromtimestamp(os.path.getmtime(self.db_path)).strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            conn.close()
            self.schema_text.insert(tk.END, schema_info)
            
        except Exception as e:
            self.schema_text.insert(tk.END, f"❌ Error loading schema: {str(e)}")
    
    def update_forecast_filter(self):
        """Update forecast filter dropdown with available cities"""
        if not os.path.exists(self.db_path):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT city FROM weather_forecast ORDER BY city")
            cities = [row[0] for row in cursor.fetchall()]
            
            self.forecast_filter['values'] = cities
            
            conn.close()
            
        except Exception as e:
            print(f"Error updating forecast filter: {e}")
    
    def filter_history(self, event=None):
        """Filter history by city name"""
        filter_text = self.search_entry.get().strip()
        if filter_text:
            self.load_history_data(filter_text)
        else:
            self.load_history_data()
    
    def clear_filter(self):
        """Clear history filter"""
        self.search_entry.delete(0, tk.END)
        self.load_history_data()
    
    def filter_forecasts(self, event=None):
        """Filter forecasts by selected city"""
        selected_city = self.forecast_filter.get()
        if selected_city:
            self.load_forecast_data(selected_city)
    
    def show_all_forecasts(self):
        """Show all forecasts"""
        self.forecast_filter.set('')
        self.load_forecast_data()
    
    def sort_treeview(self, tree, col):
        """Sort treeview by column"""
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        
        # Try to sort numerically if possible
        try:
            data.sort(key=lambda x: float(x[0].replace('°C', '').replace('%', '').replace(' km/h', '').replace(' hPa', '').replace(' km', '')))
        except:
            data.sort()
        
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
    
    def export_all_csv(self):
        """Export all data to CSV files"""
        try:
            if not os.path.exists(self.db_path):
                messagebox.showerror("Error", "Database not found!")
                return
            
            # Ask for directory
            directory = filedialog.askdirectory(title="Select directory to save CSV files")
            if not directory:
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Export history
            cursor.execute("SELECT * FROM weather_history ORDER BY searched_at DESC")
            history_data = cursor.fetchall()
            
            history_file = os.path.join(directory, 'weather_history.csv')
            with open(history_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'ID', 'City', 'Country', 'Temperature', 'Condition', 'Description',
                    'Humidity', 'Wind Speed', 'Pressure', 'Feels Like', 'Visibility', 'UV Index', 'Search Date'
                ])
                writer.writerows(history_data)
            
            # Export forecast
            cursor.execute("SELECT * FROM weather_forecast ORDER BY city, forecast_date")
            forecast_data = cursor.fetchall()
            
            forecast_file = os.path.join(directory, 'weather_forecast.csv')
            with open(forecast_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    'ID', 'City', 'Day Name', 'Forecast Date', 'High Temp', 'Low Temp',
                    'Condition', 'Description', 'Humidity', 'Wind Speed', 'Precipitation Chance', 'Created At'
                ])
                writer.writerows(forecast_data)
            
            conn.close()
            
            messagebox.showinfo(
                "Export Complete",
                f"Data exported successfully!\n\n"
                f"Files created:\n"
                f"• {history_file}\n"
                f"• {forecast_file}\n\n"
                f"History records: {len(history_data)}\n"
                f"Forecast records: {len(forecast_data)}"
            )
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def clear_history(self):
        """Clear all weather history"""
        if not messagebox.askyesno("Confirm", "Are you sure you want to clear ALL weather history?\n\nThis action cannot be undone!"):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM weather_history")
            count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM weather_history")
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Cleared {count} weather history records!")
            self.refresh_all_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear history: {str(e)}")
    
    def clear_forecasts(self):
        """Clear all forecast data"""
        if not messagebox.askyesno("Confirm", "Are you sure you want to clear ALL forecast data?\n\nThis action cannot be undone!"):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM weather_forecast")
            count = cursor.fetchone()[0]
            
            cursor.execute("DELETE FROM weather_forecast")
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Cleared {count} forecast records!")
            self.refresh_all_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear forecasts: {str(e)}")
    
    def add_sample_data(self):
        """Add sample data to database for testing"""
        if not messagebox.askyesno("Confirm", "Add sample weather data to the database?"):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sample history data
            sample_history = [
                ('New York', 'US', 21.5, 'Clear', 'Clear Sky', 45, 12.3, 1013, 23.1, 10, None),
                ('London', 'GB', 15.2, 'Clouds', 'Broken Clouds', 78, 8.7, 1008, 14.8, 8, None),
                ('Tokyo', 'JP', 18.9, 'Rain', 'Light Rain', 85, 6.2, 1005, 19.5, 5, None),
                ('Paris', 'FR', 12.4, 'Clouds', 'Overcast Clouds', 72, 11.8, 1012, 11.9, 9, None),
                ('Sydney', 'AU', 25.7, 'Clear', 'Clear Sky', 52, 15.4, 1018, 27.2, 15, None),
                ('Mumbai', 'IN', 32.1, 'Clouds', 'Few Clouds', 68, 9.3, 1009, 35.8, 7, None)
            ]
            
            for data in sample_history:
                cursor.execute('''
                    INSERT INTO weather_history 
                    (city, country, temperature, condition, description, humidity, 
                     wind_speed, pressure, feels_like, visibility, uv_index)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
            
            # Sample forecast data
            cities = ['New York', 'London', 'Tokyo', 'Paris']
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            conditions = ['Clear', 'Clouds', 'Rain', 'Snow']
            
            import random
            for city in cities:
                for i, day in enumerate(days):
                    high = random.randint(15, 30)
                    low = high - random.randint(5, 10)
                    condition = random.choice(conditions)
                    forecast_date = datetime.now().date() + timedelta(days=i)
                    
                    cursor.execute('''
                        INSERT INTO weather_forecast 
                        (city, day_name, forecast_date, high_temp, low_temp, condition, 
                         description, humidity, wind_speed, precipitation_chance)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (city, day, forecast_date, high, low, condition, condition, 
                          random.randint(40, 80), random.uniform(5, 20), random.randint(0, 60)))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", f"Added sample data:\n• {len(sample_history)} history records\n• {len(cities) * len(days)} forecast records")
            self.refresh_all_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add sample data: {str(e)}")
    
    def open_sql_query(self):
        """Open SQL query window"""
        SQLQueryWindow(self.root, self.db_path)
    
    def show_history_context_menu(self, event):
        """Show context menu for history tree"""
        item = self.history_tree.selection()[0] if self.history_tree.selection() else None
        if item:
            self.history_menu.post(event.x_root, event.y_root)
    
    def show_forecast_context_menu(self, event):
        """Show context menu for forecast tree"""
        item = self.forecast_tree.selection()[0] if self.forecast_tree.selection() else None
        if item:
            self.forecast_menu.post(event.x_root, event.y_root)
    
    def delete_history_record(self):
        """Delete selected history record"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = self.history_tree.item(item)['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete history record ID {record_id}?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM weather_history WHERE id = ?", (record_id,))
                conn.commit()
                conn.close()
                
                self.load_history_data()
                self.update_statistics()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete record: {str(e)}")
    
    def delete_forecast_record(self):
        """Delete selected forecast record"""
        selection = self.forecast_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        record_id = self.forecast_tree.item(item)['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete forecast record ID {record_id}?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM weather_forecast WHERE id = ?", (record_id,))
                conn.commit()
                conn.close()
                
                self.load_forecast_data()
                self.update_statistics()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete record: {str(e)}")
    
    def delete_city_forecasts(self):
        """Delete all forecasts for selected city"""
        selection = self.forecast_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        city = self.forecast_tree.item(item)['values'][1]
        
        if messagebox.askyesno("Confirm", f"Delete ALL forecast records for {city}?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM weather_forecast WHERE city = ?", (city,))
                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", f"Deleted {deleted_count} forecast records for {city}")
                self.load_forecast_data()
                self.update_statistics()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete records: {str(e)}")
    
    def view_history_details(self):
        """View detailed information for selected history record"""
        selection = self.history_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.history_tree.item(item)['values']
        
        details = f"Weather History Details\n{'='*30}\n\n"
        labels = ['ID', 'City', 'Country', 'Temperature', 'Condition', 'Description',
                 'Humidity', 'Wind Speed', 'Pressure', 'Feels Like', 'Visibility', 'Search Date']
        
        for label, value in zip(labels, values):
            details += f"{label}: {value}\n"
        
        detail_window = tk.Toplevel(self.root)
        detail_window.title("Weather Details")
        detail_window.geometry("400x500")
        
        text_widget = tk.Text(detail_window, font=("Courier", 11), wrap='word')
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        text_widget.insert('1.0', details)
        text_widget.config(state='disabled')

class SQLQueryWindow:
    def __init__(self, parent, db_path):
        self.db_path = db_path
        
        self.window = tk.Toplevel(parent)
        self.window.title("SQL Query Tool")
        self.window.geometry("800x600")
        
        # Query input
        query_frame = tk.LabelFrame(self.window, text="SQL Query", font=("Arial", 12, "bold"))
        query_frame.pack(fill='x', padx=10, pady=5)
        
        self.query_text = tk.Text(query_frame, height=8, font=("Courier", 11))
        self.query_text.pack(fill='x', padx=5, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(button_frame, text="Execute Query", command=self.execute_query, 
                 bg='#4caf50', fg='white', font=("Arial", 10, "bold")).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="Clear", command=self.clear_query, 
                 bg='#757575', fg='white', font=("Arial", 10, "bold")).pack(side='left', padx=5)
        
        # Sample queries
        sample_frame = tk.Frame(button_frame)
        sample_frame.pack(side='right')
        
        tk.Label(sample_frame, text="Sample Queries:", font=("Arial", 10, "bold")).pack(side='left')
        
        samples = [
            ("All History", "SELECT * FROM weather_history ORDER BY searched_at DESC;"),
            ("Cities by Temperature", "SELECT city, AVG(temperature) as avg_temp FROM weather_history GROUP BY city ORDER BY avg_temp DESC;"),
            ("Recent Searches", "SELECT city, searched_at FROM weather_history ORDER BY searched_at DESC LIMIT 10;")
        ]
        
        for name, query in samples:
            tk.Button(sample_frame, text=name, command=lambda q=query: self.load_sample_query(q),
                     bg='#2196f3', fg='white', font=("Arial", 9)).pack(side='left', padx=2)
        
        # Results
        result_frame = tk.LabelFrame(self.window, text="Query Results", font=("Arial", 12, "bold"))
        result_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.result_text = tk.Text(result_frame, font=("Courier", 10))
        result_scroll = tk.Scrollbar(result_frame, command=self.result_text.yview)
        self.result_text.config(yscrollcommand=result_scroll.set)
        
        self.result_text.pack(side='left', fill='both', expand=True)
        result_scroll.pack(side='right', fill='y')
    
    def execute_query(self):
        """Execute the SQL query"""
        query = self.query_text.get('1.0', tk.END).strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a SQL query")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                column_names = [description[0] for description in cursor.description]
                
                # Format results
                output = f"Query executed successfully!\n"
                output += f"Rows returned: {len(results)}\n"
                output += "=" * 60 + "\n\n"
                
                if results:
                    # Column headers
                    header = " | ".join(f"{col:<15}" for col in column_names)
                    output += header + "\n"
                    output += "-" * len(header) + "\n"
                    
                    # Data rows
                    for row in results:
                        row_str = " | ".join(f"{str(val):<15}" for val in row)
                        output += row_str + "\n"
                else:
                    output += "No results found.\n"
            else:
                conn.commit()
                output = f"Query executed successfully!\nRows affected: {cursor.rowcount}"
            
            conn.close()
            
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', output)
            
        except Exception as e:
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert('1.0', f"Error executing query:\n{str(e)}")
    
    def clear_query(self):
        """Clear the query text"""
        self.query_text.delete('1.0', tk.END)
        self.result_text.delete('1.0', tk.END)
    
    def load_sample_query(self, query):
        """Load a sample query"""
        self.query_text.delete('1.0', tk.END)
        self.query_text.insert('1.0', query)

def main():
    print("🗄️ Starting Weather Database Viewer...")
    print("📊 Advanced SQLite Database Management Tool")
    print("🔍 View, analyze, and manage your weather data")
    
    root = tk.Tk()
    app = WeatherDatabaseViewer(root)
    
    print("✅ Database Viewer started successfully!")
    print("💡 Use this tool to explore your weather database")
    
    root.mainloop()

if __name__ == "__main__":
    main()