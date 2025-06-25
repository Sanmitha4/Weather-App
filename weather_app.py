import tkinter as tk
from tkinter import ttk, messagebox, font
import sqlite3
from datetime import datetime, timedelta
import requests
import json
import random

class WeatherForecastApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Forecasting App")
        self.root.geometry("1400x1000")  # Increased window size
        self.root.configure(bg='#e3f2fd')
        
        # OpenWeather API Configuration
        self.api_key = "   "  # Replace with your actual API key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Initialize database
        self.init_database()
        
        # Current active tab
        self.active_tab = "Home"
        
        self.create_widgets()
        
        # Load initial data with sample forecast
        self.load_initial_data()
        
    def init_database(self):
        """Initialize SQLite database for historical data"""
        self.conn = sqlite3.connect('weather_forecast_real.db')
        self.cursor = self.conn.cursor()
        
        # Create weather_history table matching your SQL structure
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                temperature REAL NOT NULL,
                condition TEXT NOT NULL,
                humidity INTEGER,
                wind_speed REAL,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create forecast table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_forecast (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                day_name TEXT NOT NULL,
                forecast_date DATE,
                high_temp REAL NOT NULL,
                low_temp REAL NOT NULL,
                condition TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        print("✅ Database initialized successfully!")
        
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        
        # Header Frame - Clean without slogans
        header_frame = tk.Frame(self.root, bg='white', height=90)  # Increased height
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Header content
        header_content = tk.Frame(header_frame, bg='white')
        header_content.pack(expand=True, fill='both', padx=50, pady=25)
        
        # App title - Clean and simple
        title_label = tk.Label(
            header_content,
            text="Weather Forecasting App",
            font=("Arial", 26, "bold"),  # Increased font size
            bg='white',
            fg='#333'
        )
        title_label.pack(side='left')
        
        # API Status indicator
        self.api_status = tk.Label(
            header_content,
            text="🔴 Demo Mode" if self.api_key == "YOUR_API_KEY_HERE" else "🟢 Live Data",
            font=("Arial", 12),  # Increased font size
            bg='white',
            fg='#ff5722' if self.api_key == "YOUR_API_KEY_HERE" else '#4caf50'
        )
        self.api_status.pack(side='right', padx=(0, 30))
        
        # Navigation tabs
        nav_frame = tk.Frame(header_content, bg='white')
        nav_frame.pack(side='right', padx=(0, 30))
        
        tabs = ["Home", "Search", "History"]
        self.tab_buttons = {}
        
        for tab in tabs:
            btn = tk.Button(
                nav_frame,
                text=tab,
                font=("Arial", 16),  # Increased font size
                bg='white' if tab != self.active_tab else '#2196f3',
                fg='#666' if tab != self.active_tab else 'white',
                relief='flat',
                padx=25,  # Increased padding
                pady=10,
                command=lambda t=tab: self.switch_tab(t)
            )
            btn.pack(side='left', padx=8)
            self.tab_buttons[tab] = btn
        
        # Main content frame
        self.main_frame = tk.Frame(self.root, bg='#e3f2fd')
        self.main_frame.pack(fill='both', expand=True, padx=50, pady=25)
        
        # Create content for different tabs
        self.create_home_content()
        self.create_search_content()
        self.create_history_content()
        
        # Show home content initially
        self.show_content("Home")
        
    def create_home_content(self):
        """Create home tab content with current weather and forecast"""
        self.home_content = tk.Frame(self.main_frame, bg='#e3f2fd')
        
        # Current Weather Section
        self.create_current_weather_section(self.home_content)
        
        # 7-Day Forecast Section (Always visible on home)
        self.create_forecast_section(self.home_content)
        
    def create_search_content(self):
        """Create search tab content"""
        self.search_content = tk.Frame(self.main_frame, bg='#e3f2fd')
        
        # Search title
        search_title = tk.Label(
            self.search_content,
            text="Search Weather",
            font=("Arial", 36, "bold"),
            bg='#e3f2fd',
            fg='#333'
        )
        search_title.pack(pady=(50, 30))
        
        # Large search section
        search_frame = tk.Frame(self.search_content, bg='white', relief='solid', bd=2)
        search_frame.pack(fill='x', pady=(0, 40), ipady=25)
        
        search_content_frame = tk.Frame(search_frame, bg='white')
        search_content_frame.pack(expand=True, fill='x', padx=40)
        
        # Search icon
        search_icon = tk.Label(
            search_content_frame,
            text="🔍",
            font=("Arial", 20),
            bg='white',
            fg='#666'
        )
        search_icon.pack(side='left', padx=(0, 15))
        
        # Search entry
        self.search_entry = tk.Entry(
            search_content_frame,
            font=("Arial", 18),
            bg='white',
            relief='flat',
            fg='#666'
        )
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.insert(0, "Search for a city...")
        self.search_entry.bind('<FocusIn>', self.on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self.on_search_focus_out)
        self.search_entry.bind('<Return>', self.search_weather)
        
        # Search button
        search_btn = tk.Button(
            search_content_frame,
            text="Search",
            command=self.search_weather,
            bg='#2196f3',
            fg='white',
            font=("Arial", 14, "bold"),
            padx=30,
            pady=5,
            relief='flat'
        )
        search_btn.pack(side='right', padx=(15, 0))
        
        # Current weather display for search results
        self.search_weather_card = tk.Frame(self.search_content, bg='white', relief='solid', bd=2)
        self.search_weather_card.pack(fill='x', pady=(0, 30), ipady=40)
        
        # Initially hidden
        self.search_weather_card.pack_forget()
        
    def create_history_content(self):
        """Create history tab content - Only shows search history"""
        self.history_content = tk.Frame(self.main_frame, bg='#e3f2fd')
        
        # History title
        history_title = tk.Label(
            self.history_content,
            text="Search History",
            font=("Arial", 36, "bold"),
            bg='#e3f2fd',
            fg='#333'
        )
        history_title.pack(pady=(50, 30))
        
        # History cards frame
        self.history_frame = tk.Frame(self.history_content, bg='#e3f2fd')
        self.history_frame.pack(fill='both', expand=True)
        
    def create_current_weather_section(self, parent):
        """Create the current weather section"""
        # Current Weather Title
        current_title = tk.Label(
            parent,
            text="Current Weather",
            font=("Arial", 36, "bold"),
            bg='#e3f2fd',
            fg='#333'
        )
        current_title.pack(pady=(0, 30))
        
        # Weather Display Card - Larger size
        self.weather_card = tk.Frame(parent, bg='white', relief='solid', bd=2)
        self.weather_card.pack(fill='x', pady=(0, 40), ipady=40)
        
        weather_content = tk.Frame(self.weather_card, bg='white')
        weather_content.pack(expand=True, fill='both', padx=50, pady=30)
        
        # Left side - Weather icon
        left_frame = tk.Frame(weather_content, bg='white')
        left_frame.pack(side='left', padx=(0, 50))
        
        self.weather_icon = tk.Label(
            left_frame,
            text="🌤️",
            font=("Arial", 100),  # Increased icon size
            bg='white'
        )
        self.weather_icon.pack()
        
        # Right side - Weather info
        right_frame = tk.Frame(weather_content, bg='white')
        right_frame.pack(side='left', fill='both', expand=True)
        
        # City name
        self.city_label = tk.Label(
            right_frame,
            text="New York",
            font=("Arial", 40, "bold"),  # Increased font size
            bg='white',
            fg='#333'
        )
        self.city_label.pack(anchor='w')
        
        # Temperature
        self.temp_label = tk.Label(
            right_frame,
            text="22°C",
            font=("Arial", 80, "bold"),  # Increased font size
            bg='white',
            fg='#333'
        )
        self.temp_label.pack(anchor='w')
        
        # Condition
        self.condition_label = tk.Label(
            right_frame,
            text="Partly Cloudy",
            font=("Arial", 28),  # Increased font size
            bg='white',
            fg='#333'
        )
        self.condition_label.pack(anchor='w')
        
        # Date
        self.date_label = tk.Label(
            right_frame,
            text=datetime.now().strftime("%A, %B %d"),
            font=("Arial", 18),  # Increased font size
            bg='white',
            fg='#666'
        )
        self.date_label.pack(anchor='w', pady=(10, 30))
        
        # Weather details - Larger grid
        details_frame = tk.Frame(right_frame, bg='white')
        details_frame.pack(anchor='w', fill='x')
        
        # Create details labels with larger fonts
        self.humidity_label = tk.Label(details_frame, text="Humidity: 65%", font=("Arial", 16), bg='white', fg='#333')
        self.humidity_label.grid(row=0, column=0, sticky='w', padx=(0, 60), pady=5)
        
        self.wind_label = tk.Label(details_frame, text="Wind: 12 km/h", font=("Arial", 16), bg='white', fg='#333')
        self.wind_label.grid(row=0, column=1, sticky='w', padx=(0, 60), pady=5)
        
        self.high_label = tk.Label(details_frame, text="High: 25°C", font=("Arial", 16), bg='white', fg='#333')
        self.high_label.grid(row=1, column=0, sticky='w', padx=(0, 60), pady=5)
        
        self.low_label = tk.Label(details_frame, text="Low: 18°C", font=("Arial", 16), bg='white', fg='#333')
        self.low_label.grid(row=1, column=1, sticky='w', pady=5)
        
    def create_forecast_section(self, parent):
        """Create the 7-day forecast section - More prominent"""
        # Forecast title - Larger and more prominent
        forecast_title = tk.Label(
            parent,
            text="7-Day Forecast",
            font=("Arial", 36, "bold"),
            bg='#e3f2fd',
            fg='#333'
        )
        forecast_title.pack(pady=(0, 30))
        
        # Forecast cards frame with better spacing
        self.forecast_frame = tk.Frame(parent, bg='#e3f2fd')
        self.forecast_frame.pack(fill='x', pady=(0, 40))
        
        # Create 7 forecast cards - Larger size
        self.forecast_cards = []
        
        for i in range(7):
            card = tk.Frame(self.forecast_frame, bg='white', relief='solid', bd=2, width=180, height=220)  # Increased size
            card.pack(side='left', padx=12, pady=8)  # Increased spacing
            card.pack_propagate(False)
            
            # Day name
            day_label = tk.Label(card, text="Mon", font=("Arial", 16, "bold"), bg='white', fg='#333')
            day_label.pack(pady=(20, 15))
            
            # Weather icon - Larger
            icon_label = tk.Label(card, text="🌤️", font=("Arial", 36), bg='white')
            icon_label.pack(pady=8)
            
            # High temperature
            high_label = tk.Label(card, text="25°C", font=("Arial", 18, "bold"), bg='white', fg='#333')
            high_label.pack(pady=2)
            
            # Low temperature
            low_label = tk.Label(card, text="18°C", font=("Arial", 16), bg='white', fg='#666')
            low_label.pack(pady=2)
            
            # Condition
            condition_label = tk.Label(card, text="Sunny", font=("Arial", 12), bg='white', fg='#666')
            condition_label.pack(pady=(8, 20))
            
            self.forecast_cards.append({
                'frame': card,
                'day': day_label,
                'icon': icon_label,
                'high': high_label,
                'low': low_label,
                'condition': condition_label
            })
    
    def show_content(self, tab):
        """Show content for the selected tab"""
        # Hide all content frames
        self.home_content.pack_forget()
        self.search_content.pack_forget()
        self.history_content.pack_forget()
        
        # Show selected content
        if tab == "Home":
            self.home_content.pack(fill='both', expand=True)
        elif tab == "Search":
            self.search_content.pack(fill='both', expand=True)
        elif tab == "History":
            self.history_content.pack(fill='both', expand=True)
            # Refresh history when showing history tab
            self.create_history_cards()
    
    def generate_sample_forecast(self):
        """Generate sample forecast data for initial display"""
        forecast = []
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        conditions = [
            ('Clear', '☀️'),
            ('Clouds', '☁️'),
            ('Rain', '🌧️'),
            ('Snow', '❄️'),
            ('Partly Cloudy', '🌤️')
        ]
        
        for i, day in enumerate(days):
            condition, icon = random.choice(conditions)
            high = random.randint(18, 32)
            low = high - random.randint(5, 12)
            
            forecast.append({
                'day': day,
                'date': datetime.now().date() + timedelta(days=i),
                'high': high,
                'low': low,
                'condition': condition,
                'icon': icon
            })
        
        return forecast
    
    def fetch_current_weather(self, city):
        """Fetch current weather from OpenWeather API or generate mock data"""
        if self.api_key == "YOUR_API_KEY_HERE":
            return self.generate_mock_weather(city)
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'city': data['name'],
                    'temperature': round(data['main']['temp'], 1),
                    'condition': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'].title(),
                    'humidity': data['main']['humidity'],
                    'wind_speed': round(data['wind']['speed'] * 3.6, 1),
                    'high': round(data['main']['temp_max'], 1),
                    'low': round(data['main']['temp_min'], 1),
                    'icon': data['weather'][0]['icon']
                }
            else:
                raise Exception(f"API Error: {response.status_code}")
                
        except Exception as e:
            print(f"API Error: {e}, using mock data")
            return self.generate_mock_weather(city)
    
    def fetch_forecast(self, city):
        """Fetch 7-day forecast from OpenWeather API or generate mock data"""
        if self.api_key == "YOUR_API_KEY_HERE":
            return self.generate_sample_forecast()
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                forecast_list = []
                
                # Group by day and get daily high/low
                daily_data = {}
                for item in data['list']:
                    date = datetime.fromtimestamp(item['dt']).date()
                    day_name = date.strftime('%a')
                    
                    if date not in daily_data:
                        daily_data[date] = {
                            'day': day_name,
                            'date': date,
                            'temps': [],
                            'conditions': []
                        }
                    
                    daily_data[date]['temps'].append(item['main']['temp'])
                    daily_data[date]['conditions'].append(item['weather'][0]['main'])
                
                # Convert to forecast format
                for date, day_data in list(daily_data.items())[:7]:
                    condition = max(set(day_data['conditions']), key=day_data['conditions'].count)
                    forecast_list.append({
                        'day': day_data['day'],
                        'date': date,
                        'high': round(max(day_data['temps']), 1),
                        'low': round(min(day_data['temps']), 1),
                        'condition': condition,
                        'icon': self.get_weather_icon(condition)
                    })
                
                return forecast_list
            else:
                raise Exception(f"API Error: {response.status_code}")
                
        except Exception as e:
            print(f"Forecast API Error: {e}, using sample data")
            return self.generate_sample_forecast()
    
    def get_weather_icon(self, condition):
        """Get weather icon based on condition"""
        condition = condition.lower()
        
        if 'clear' in condition or 'sun' in condition:
            return "☀️"
        elif 'cloud' in condition:
            return "☁️"
        elif 'rain' in condition or 'drizzle' in condition:
            return "🌧️"
        elif 'snow' in condition:
            return "❄️"
        elif 'thunder' in condition:
            return "⛈️"
        elif 'mist' in condition or 'fog' in condition:
            return "🌫️"
        else:
            return "🌤️"
    
    def search_weather(self, event=None):
        """Search for weather data"""
        city = self.search_entry.get().strip()
        if not city or city == "Search for a city...":
            messagebox.showwarning("Input Required", "Please enter a city name")
            return
        
        try:
            # Show loading state
            self.city_label.config(text="Loading...")
            self.root.update()
            
            # Fetch current weather
            weather_data = self.fetch_current_weather(city)
            
            # Fetch forecast
            forecast_data = self.fetch_forecast(city)
            
            # Update display
            self.update_current_weather(weather_data)
            self.update_forecast(forecast_data)
            
            # Save to database
            self.save_weather_data(weather_data)
            self.save_forecast_data(city, forecast_data)
            
            # Switch to home tab to show results
            self.switch_tab("Home")
            
            # Clear search entry
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, "Search for a city...")
            self.search_entry.config(fg='#666')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch weather data:\n{str(e)}")
            self.city_label.config(text="Error loading data")
    
    def generate_mock_weather(self, city):
        """Generate mock weather data"""
        conditions = ["Clear", "Clouds", "Rain", "Snow", "Thunderstorm"]
        condition = random.choice(conditions)
        temp = random.randint(5, 35)
        
        return {
            'city': city.title(),
            'temperature': temp,
            'condition': condition,
            'description': condition,
            'humidity': random.randint(30, 80),
            'wind_speed': round(random.uniform(5, 25), 1),
            'high': temp + random.randint(2, 8),
            'low': temp - random.randint(2, 8),
            'icon': '01d'
        }
    
    def update_current_weather(self, data):
        """Update current weather display"""
        self.city_label.config(text=data['city'])
        self.temp_label.config(text=f"{data['temperature']}°C")
        self.condition_label.config(text=data['description'])
        
        self.humidity_label.config(text=f"Humidity: {data['humidity']}%")
        self.wind_label.config(text=f"Wind: {data['wind_speed']} km/h")
        self.high_label.config(text=f"High: {data['high']}°C")
        self.low_label.config(text=f"Low: {data['low']}°C")
        
        # Update weather icon
        icon = self.get_weather_icon(data['condition'])
        self.weather_icon.config(text=icon)
    
    def update_forecast(self, forecast_data):
        """Update 7-day forecast display"""
        for i, (card, data) in enumerate(zip(self.forecast_cards, forecast_data)):
            card['day'].config(text=data['day'])
            card['high'].config(text=f"{data['high']}°C")
            card['low'].config(text=f"{data['low']}°C")
            card['condition'].config(text=data['condition'])
            
            icon = data.get('icon', self.get_weather_icon(data['condition']))
            card['icon'].config(text=icon)
    
    def save_weather_data(self, data):
        """Save weather data to database"""
        try:
            self.cursor.execute('''
                INSERT INTO weather_history 
                (city, temperature, condition, humidity, wind_speed)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                data['city'], data['temperature'], data['condition'],
                data['humidity'], data['wind_speed']
            ))
            self.conn.commit()
            print(f"✅ Saved {data['city']} weather data to database")
        except Exception as e:
            print(f"❌ Error saving weather data: {e}")
    
    def save_forecast_data(self, city, forecast_data):
        """Save forecast data to database"""
        try:
            # Clear old forecast for this city
            self.cursor.execute('DELETE FROM weather_forecast WHERE city = ?', (city,))
            
            # Insert new forecast
            for data in forecast_data:
                self.cursor.execute('''
                    INSERT INTO weather_forecast 
                    (city, day_name, forecast_date, high_temp, low_temp, condition)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    city, data['day'], data['date'], data['high'], data['low'], data['condition']
                ))
            
            self.conn.commit()
            print(f"✅ Saved {city} forecast data to database")
        except Exception as e:
            print(f"❌ Error saving forecast data: {e}")
    
    def create_history_cards(self):
        """Create history cards from database - Only shown on History tab"""
        # Clear existing cards
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        try:
            self.cursor.execute('''
                SELECT city, temperature, condition, searched_at
                FROM weather_history
                ORDER BY searched_at DESC
                LIMIT 12
            ''')
            history_data = self.cursor.fetchall()
        except:
            history_data = []
        
        if not history_data:
            no_data_label = tk.Label(
                self.history_frame,
                text="No search history yet. Search for a city to get started!",
                font=("Arial", 18),
                bg='#e3f2fd',
                fg='#666'
            )
            no_data_label.pack(pady=50)
            return
        
        # Create a grid layout for history cards
        history_grid = tk.Frame(self.history_frame, bg='#e3f2fd')
        history_grid.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Display cards in a 3x4 grid
        for i, (city, temp, condition, date) in enumerate(history_data):
            row = i // 3
            col = i % 3
            
            card = tk.Frame(history_grid, bg='white', relief='solid', bd=2, width=220, height=140)  # Larger cards
            card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
            card.pack_propagate(False)
            
            content = tk.Frame(card, bg='white')
            content.pack(expand=True, fill='both', padx=20, pady=20)
            
            # City name
            city_label = tk.Label(content, text=city, font=("Arial", 16, "bold"), bg='white', fg='#333')
            city_label.pack(anchor='w')
            
            # Condition
            condition_label = tk.Label(content, text=condition, font=("Arial", 12), bg='white', fg='#666')
            condition_label.pack(anchor='w')
            
            # Date
            try:
                date_obj = datetime.fromisoformat(date.replace('Z', '+00:00') if 'Z' in date else date)
                date_str = date_obj.strftime("%m/%d %H:%M")
            except:
                date_str = "Recent"
            
            date_label = tk.Label(content, text=date_str, font=("Arial", 10), bg='white', fg='#999')
            date_label.pack(anchor='w')
            
            # Bottom frame for icon and temperature
            bottom_frame = tk.Frame(content, bg='white')
            bottom_frame.pack(side='bottom', fill='x', pady=(15, 0))
            
            # Weather icon
            icon = self.get_weather_icon(condition)
            icon_label = tk.Label(bottom_frame, text=icon, font=("Arial", 20), bg='white')
            icon_label.pack(side='left')
            
            # Temperature
            temp_label = tk.Label(bottom_frame, text=f"{temp}°C", font=("Arial", 18, "bold"), bg='white', fg='#333')
            temp_label.pack(side='right')
            
            # Make card clickable
            def on_click(city=city):
                self.search_entry.delete(0, tk.END)
                self.search_entry.insert(0, city)
                self.search_weather()
            
            card.bind("<Button-1>", lambda e, city=city: on_click(city))
            for child in self.get_all_children(card):
                child.bind("<Button-1>", lambda e, city=city: on_click(city))
        
        # Configure grid weights for responsive layout
        for i in range(3):
            history_grid.columnconfigure(i, weight=1)
    
    def get_all_children(self, widget):
        """Get all child widgets recursively"""
        children = [widget]
        for child in widget.winfo_children():
            children.extend(self.get_all_children(child))
        return children
    
    def switch_tab(self, tab):
        """Switch between navigation tabs"""
        self.active_tab = tab
        for tab_name, button in self.tab_buttons.items():
            if tab_name == tab:
                button.config(bg='#2196f3', fg='white')
            else:
                button.config(bg='white', fg='#666')
        
        # Show appropriate content
        self.show_content(tab)
    
    def on_search_focus_in(self, event):
        """Handle search entry focus in"""
        if self.search_entry.get() == "Search for a city...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg='#333')
    
    def on_search_focus_out(self, event):
        """Handle search entry focus out"""
        if not self.search_entry.get():
            self.search_entry.insert(0, "Search for a city...")
            self.search_entry.config(fg='#666')
    
    def load_initial_data(self):
        """Load initial display with sample data"""
        # Show sample current weather for New York
        sample_weather = {
            'city': 'New York',
            'temperature': 22,
            'condition': 'Clear',
            'description': 'Clear Sky',
            'humidity': 65,
            'wind_speed': 12,
            'high': 25,
            'low': 18
        }
        self.update_current_weather(sample_weather)
        
        # Load sample forecast data to show on front page
        sample_forecast = self.generate_sample_forecast()
        self.update_forecast(sample_forecast)
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    print("🌤️ Starting Weather Forecasting App...")
    print("📊 SQLite Database Storage")
    print("🎯 Sample Data Mode (Configure API key for live data)")
    
    root = tk.Tk()
    app = WeatherForecastApp(root)
    
    print("✅ App started successfully!")
    print("💡 7-Day forecast prominently visible on home page")
    print("🔍 Search history only visible on History tab")
    
    root.mainloop()

if __name__ == "__main__":
    main()
