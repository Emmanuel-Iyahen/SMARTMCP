import openai
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging
from sqlalchemy import create_engine, text
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AIAnalyzerModule:
    def __init__(self):
        # Use environment variable instead of hardcoded key
        api_key = os.getenv("OPENAI_API_KEY")
        self.client_available = False
        self.client = None
        
        logger.info(f"Initializing OpenAI client with key: {api_key[:20]}...")
        
        # Check if API key is provided
        if api_key and api_key not in ['', 'your-openai-key', 'dummy-key-for-development']:
            try:
                # Initialize the new OpenAI client (v1.0+)
                self.client = openai.OpenAI(api_key=api_key)
                
                # Test with a simple request instead of models.list()
                test_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Say 'hello'"}],
                    max_tokens=5
                )
                
                self.client_available = True
                logger.info("✅ OpenAI client initialized successfully!")
                
            except openai.AuthenticationError as e:
                logger.error(f"❌ Authentication failed: {e}")
                logger.error("Please check your API key at https://platform.openai.com/api-keys")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
                logger.error(f"Error type: {type(e).__name__}")
        else:
            logger.warning("⚠️ OPENAI_API_KEY not configured")
        
        # Initialize Snowflake connection
        try:
            snowflake_user = os.getenv('SNOWFLAKE_USER')
            snowflake_password = os.getenv('SNOWFLAKE_PASSWORD')
            snowflake_account = os.getenv('SNOWFLAKE_ACCOUNT')
            
            if all([snowflake_user, snowflake_password, snowflake_account]):
                self.snowflake_engine = create_engine(
                    f"snowflake://{snowflake_user}:{snowflake_password}@"
                    f"{snowflake_account}/{os.getenv('SNOWFLAKE_DATABASE', 'MCP_PLATFORM')}/"
                    f"{os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')}"
                    f"?warehouse={os.getenv('SNOWFLAKE_WAREHOUSE', 'MCP_WAREHOUSE')}"
                )
                logger.info("✅ Snowflake engine initialized successfully")
            else:
                logger.warning("⚠️ Snowflake credentials not fully configured")
                self.snowflake_engine = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Snowflake engine: {e}")
            self.snowflake_engine = None
    
    async def analyze_data(self, prompt: str, sector: str) -> Dict[str, Any]:
        """Analyze data based on user prompt and sector"""
        try:
            logger.info(f"📊 Analyzing: '{prompt}' for {sector}")

            
            
            # Get relevant data
            data = await self._get_sector_data(sector)

            print(data)

            if sector == 'finance':
                # Get latest entry for each symbol
                limited_data = data.drop_duplicates(subset=['SYMBOL'], keep='first')
                data = limited_data


          
            # Generate insights based on whether OpenAI is available
            if self.client_available:
                logger.info("🤖 Using AI-powered analysis")
                insights = await self._generate_ai_insights(prompt, data, sector)
                recommendations = await self._generate_ai_recommendations(insights, sector)
                ai_used = True
            else:
                logger.info("📋 Using basic analysis")
                insights = self._generate_basic_insights(prompt, data, sector)
                recommendations = self._generate_basic_recommendations(sector)
                ai_used = False
            
            # Ensure data is serializable
            serializable_data = data.to_dict('records') if hasattr(data, 'to_dict') and not data.empty else []
            
            return {
                'data': serializable_data,
                'insights': insights,
                'recommendations': recommendations,
                'ai_used': ai_used,
                'sector': sector,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing data for {sector}: {e}")
            return await self._get_fallback_response(prompt, sector, str(e))
    
    async def _generate_ai_insights(self, prompt: str, data: pd.DataFrame, sector: str) -> str:
        """Generate insights using OpenAI"""
        try:
            # Prepare data sample for the AI
            if not data.empty:
                # data_sample = f"Data sample ({len(data)} records): {data.head(2).to_dict('records')}"
                data_sample = f"Complete recent data ({len(data)} lines): {data.to_dict('records')}"
            else:
                data_sample = "No data available"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"""You are a data analyst specializing in {sector} data. 
                        Provide clear, insightful analysis based on the provided data."""
                    },
                    {
                        "role": "user", 
                        "content": f"""User query: {prompt}
                        
                        {data_sample}
                        
                        Please provide a comprehensive analysis with key insights."""
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ Error generating AI insights: {e}")
            return self._generate_basic_insights(prompt, data, sector)
    
    async def _generate_ai_recommendations(self, insights: str, sector: str) -> List[str]:
        """Generate recommendations using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a business consultant specializing in {sector}.
                        Provide 3 actionable recommendations based on the insights."""
                    },
                    {
                        "role": "user",
                        "content": f"Insights: {insights}\n\nProvide 3 actionable recommendations:"
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            recommendations_text = response.choices[0].message.content
            recommendations = [
                rec.strip().lstrip('-• ') 
                for rec in recommendations_text.split('\n') 
                if rec.strip()
            ]
            return recommendations[:3]
            
        except Exception as e:
            logger.error(f"❌ Error generating AI recommendations: {e}")
            return self._generate_basic_recommendations(sector)
    
    def _generate_basic_insights(self, prompt: str, data: pd.DataFrame, sector: str) -> str:
        """Generate basic insights without AI"""
        if data.empty:
            return f"## {sector.title()} Analysis\n\nNo data available for {sector} sector."
        
        insights = []
        insights.append(f"## {sector.title()} Analysis")
        insights.append(f"**User Query:** {prompt}")
        insights.append(f"**Dataset:** {len(data)} records available")
        
        if 'timestamp' in data.columns and not data.empty:
            try:
                min_date = data['timestamp'].min()
                max_date = data['timestamp'].max()
                insights.append(f"**Time Period:** {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
            except Exception as e:
                logger.warning(f"Error processing dates: {e}")
        
        # Sector-specific insights
        if sector == 'weather':
            insights.extend(self._get_weather_insights(data))
        elif sector == 'energy':
            insights.extend(self._get_energy_insights(data))
        elif sector == 'transportation':
            insights.extend(self._get_transport_insights(data))
        elif sector == 'finance':
            insights.extend(self._get_finance_insights(data))
        
        insights.append("\n*Note: Basic analysis mode. Configure OpenAI API for AI-powered insights.*")
        
        return "\n\n".join(insights)
    
    def _get_weather_insights(self, data: pd.DataFrame) -> List[str]:
        """Generate weather-specific insights"""
        insights = []
        
        if 'temperature' in data.columns and not data.empty:
            avg_temp = data['temperature'].mean()
            insights.append(f"**Average Temperature:** {avg_temp:.1f}°C")
        
        if 'humidity' in data.columns and not data.empty:
            avg_humidity = data['humidity'].mean()
            insights.append(f"**Average Humidity:** {avg_humidity:.1f}%")
        
        return insights
    
    def _get_energy_insights(self, data: pd.DataFrame) -> List[str]:
        """Generate energy-specific insights"""
        insights = []
        if 'price' in data.columns and not data.empty:
            avg_price = data['price'].mean()
            insights.append(f"**Average Price:** £{avg_price:.2f}/MWh")
        return insights
    
    
    def _get_finance_insights(self, data: pd.DataFrame) -> List[str]:
        """Generate finance-specific insights"""
        insights = []
        if 'price' in data.columns and not data.empty:
            latest_price = data['price'].iloc[-1]
            insights.append(f"**Latest Price:** £{latest_price:.2f}")
        return insights
    
    def _generate_basic_recommendations(self, sector: str) -> List[str]:
        """Generate basic recommendations without AI"""
        base_recommendations = {
            'weather': [
                "Monitor daily weather forecasts",
                "Consider weather impact on activities",
                "Check for weather warnings"
            ],
            'energy': [
                "Monitor energy consumption patterns",
                "Consider time-of-use pricing",
                "Evaluate energy-efficient options"
            ]
        }
        
        return base_recommendations.get(sector, [
            f"Monitor {sector} trends regularly",
            "Review data for patterns",
            "Consider external factors"
        ])
    
    from modules.data_loader import DataLoaderModule
    async def _get_sector_data(self, sector: str) -> pd.DataFrame:
        """Get sample data for the specified sector"""
        now = pd.Timestamp.now()

        sample_data = {}

        try:
            # Import DataLoaderModule directly
            from modules.data_loader import DataLoaderModule
            # Create a new instance of DataLoaderModule
            data_loader = DataLoaderModule()

            
            if sector == 'transportation':
                real_data = await data_loader.load_transport_data()
                print(f"🚇 AI Analyzer loaded REAL transport data: {len(real_data)} rows")
                
                # Debug: Show all lines in the data
                if not real_data.empty and 'line_name' in real_data.columns:
                    unique_lines = real_data['line_name'].unique()
                    print(f"📋 Lines available in data: {list(unique_lines)}")
                    
                    # Check status distribution
                    if 'status' in real_data.columns:
                        status_counts = real_data['status'].value_counts()
                        print(f"📊 Status distribution: {dict(status_counts)}")
                        
                        # Check for delays
                        delayed_lines = real_data[real_data['status'] != 'Good Service']
                        if not delayed_lines.empty:
                            print(f"⚠️ Delayed lines: {list(delayed_lines['line_name'].unique())}")
                
                return real_data
            
            elif sector == 'weather':
                real_data = await data_loader.load_weather_data()
                print(f"🌤️ AI Analyzer loaded REAL weather data: {len(real_data)} rows")
                # Debug: Show weather data structure
                if not real_data.empty:
                    print(f"📊 Weather data columns: {list(real_data.columns)}")
                    print(f"🌡️ Current temperature: {real_data['temperature'].iloc[-1] if 'temperature' in real_data.columns else 'N/A'}°C")
                    print(f"💧 Current humidity: {real_data['humidity'].iloc[-1] if 'humidity' in real_data.columns else 'N/A'}%")
                    print(f"🌧️ Current precipitation: {real_data['precipitation'].iloc[-1] if 'precipitation' in real_data.columns else 'N/A'}mm")
                    print(f"🌈 Weather code: {real_data['weather_code'].iloc[-1] if 'weather_code' in real_data.columns else 'N/A'}")
                    
                    # Show data range
                    if 'timestamp' in real_data.columns:
                        print(f"⏰ Data range: {real_data['timestamp'].min()} to {real_data['timestamp'].max()}")

                return real_data


            elif sector == "finance":

                try:
                    real_data = await data_loader.load_financial_data_from_snowflake()
                    print(f"📈 AI Analyzer loaded financial data: {len(real_data)} rows")
                    
                    if not real_data.empty:
                        print(f"📊 Financial data columns: {list(real_data.columns)}")
                        # print(f"📅 Data date range: {real_data['timestamp'].min()} to {real_data['timestamp'].max()}")
                        # print(f"🏢 Companies: {real_data['company_name'].unique()}")
                        
                        # Return the DataFrame directly, not a dictionary
                        return real_data
                    else:
                        print("❌ No financial data available")
                        return pd.DataFrame()
                        
                except Exception as e:
                    print(f"❌ Error loading finance data: {e}")
                    return pd.DataFrame()

                
        except Exception as e:
            print(f"❌ Error loading finance data: {e}")

    def _analyze_company_performance(self, financial_data: pd.DataFrame) -> Dict:
        """Analyze company performance and identify top performers"""
        performance_analysis = []
        
        companies = financial_data['company_name'].unique()
        print(f"🏢 Analyzing {len(companies)} companies")
        
        for company in companies:
            company_data = financial_data[financial_data['company_name'] == company].sort_values('timestamp')
            
            if len(company_data) > 1:
                # Latest data
                latest = company_data.iloc[-1]
                previous = company_data.iloc[-2]
                
                # Calculate performance metrics
                price_change = latest['close'] - previous['close']
                price_change_pct = (price_change / previous['close']) * 100
                
                # Calculate 5-day trend if available
                if len(company_data) >= 5:
                    five_day_change = ((latest['close'] - company_data.iloc[-5]['close']) / company_data.iloc[-5]['close']) * 100
                else:
                    five_day_change = price_change_pct
                
                # Volume analysis
                avg_volume = company_data['volume'].mean()
                volume_ratio = latest['volume'] / avg_volume if avg_volume > 0 else 1
                
                performance_analysis.append({
                    'company': company,
                    'symbol': latest['symbol'],
                    'current_price': latest['close'],
                    'daily_change': price_change,
                    'daily_change_pct': price_change_pct,
                    'five_day_change_pct': five_day_change,
                    'volume_ratio': volume_ratio,
                    'trend': 'up' if price_change_pct > 0 else 'down',
                    'sector': self._get_company_sector(latest['symbol'])
                })
        
        # Sort by performance
        performance_analysis.sort(key=lambda x: x['daily_change_pct'], reverse=True)
        
        # Print performance summary
        print("\n" + "="*50)
        print("🏆 COMPANY PERFORMANCE ANALYSIS")
        print("="*50)
        
        print("\n📈 TOP PERFORMERS (Today):")
        for i, perf in enumerate(performance_analysis[:3]):
            icon = "🚀" if perf['daily_change_pct'] > 2 else "📈"
            print(f"{i+1}. {perf['company']}: {perf['daily_change_pct']:+.2f}% {icon}")
            print(f"   Price: £{perf['current_price']:.2f} | 5-day: {perf['five_day_change_pct']:+.2f}%")
        
        print("\n📉 WORST PERFORMERS (Today):")
        for i, perf in enumerate(performance_analysis[-3:]):
            icon = "🔻" if perf['daily_change_pct'] < -2 else "📉"
            print(f"{i+1}. {perf['company']}: {perf['daily_change_pct']:+.2f}% {icon}")
            print(f"   Price: £{perf['current_price']:.2f} | 5-day: {perf['five_day_change_pct']:+.2f}%")
        
        # High volume alerts
        high_volume = [p for p in performance_analysis if p['volume_ratio'] > 1.5]
        if high_volume:
            print("\n📊 UNUSUAL VOLUME (Today):")
            for perf in high_volume:
                print(f"• {perf['company']}: {perf['volume_ratio']:.1f}x average volume")
        
        return {
            'top_performers': performance_analysis[:3],
            'worst_performers': performance_analysis[-3:],
            'high_volume': high_volume,
            'market_summary': self._get_market_summary(performance_analysis)
        }

    def _get_company_sector(self, symbol: str) -> str:
        """Get company sector for categorization"""
        sectors = {
            'HSBA.L': 'Banking',
            'BARC.L': 'Banking', 
            'LLOY.L': 'Banking',
            'BP.L': 'Energy',
            'RIO.L': 'Mining',
            'GSK.L': 'Pharmaceuticals',
            'AZN.L': 'Pharmaceuticals',
            'ULVR.L': 'Consumer Goods',
            'TSCO.L': 'Retail'
        }
        return sectors.get(symbol, 'Other')

    def _get_market_summary(self, performance_data: List[Dict]) -> Dict:
        """Generate market summary"""
        if not performance_data:
            return {}
        
        gainers = len([p for p in performance_data if p['daily_change_pct'] > 0])
        losers = len([p for p in performance_data if p['daily_change_pct'] < 0])
        avg_change = sum(p['daily_change_pct'] for p in performance_data) / len(performance_data)
        
        return {
            'gainers': gainers,
            'losers': losers,
            'avg_daily_change': avg_change,
            'market_sentiment': 'bullish' if avg_change > 0 else 'bearish'
        }

    def _prepare_simplified_financial_data(self, financial_data: pd.DataFrame) -> List[Dict]:
        """Prepare simplified data for AI analysis to avoid token limits"""
        simplified = []
        
        # Get latest data for each company
        latest_data = financial_data.sort_values('timestamp').groupby('company_name').last().reset_index()
        
        for _, row in latest_data.iterrows():
            simplified.append({
                'company': row['company_name'],
                'price': row['close'],
                'daily_change': f"{((row['close'] - row['open']) / row['open'] * 100):+.2f}%",
                'volume': row['volume']
            })
        
        return simplified

        
    
    async def _get_fallback_response(self, prompt: str, sector: str, error: str) -> Dict[str, Any]:
        """Get fallback response when analysis fails"""
        return {
            'data': [],
            'insights': f"## Analysis Error\n\nUnable to analyze {sector} data. Error: {error}",
            'recommendations': [
                "Try again later",
                "Check service status",
                "Contact support if issue persists"
            ],
            'ai_used': False,
            'sector': sector
        }
    

    def _get_transport_insights(self, data: pd.DataFrame, prompt: str) -> List[str]:

        """Generate comprehensive transport insights"""
        insights = []
        
        if data.empty:
            return insights
        
        insights.append("**Transport Network Analysis:**")
        
        # Network overview
        total_lines = len(data['line_name'].unique())
        modes = data['mode'].unique()
        insights.append(f"- **Network Scale:** {total_lines} lines across {len(modes)} modes")
        insights.append(f"- **Modes Available:** {', '.join(modes)}")
        
        # Service status summary
        current_data = data[data['timestamp'] == data['timestamp'].max()]
        
        # Service types analysis
        if 'regular_service' in current_data.columns:
            regular_services = current_data['regular_service'].sum()
            night_services = current_data['night_service'].sum()
            insights.append(f"- **Service Types:** {regular_services} regular, {night_services} night services")
        
        # Delay analysis
        if 'delay_minutes' in current_data.columns:
            delayed_lines = len(current_data[current_data['delay_minutes'] > 0])
            total_current = len(current_data)
            delay_percentage = (delayed_lines / total_current) * 100 if total_current > 0 else 0
            insights.append(f"- **Current Delays:** {delayed_lines}/{total_current} lines ({delay_percentage:.1f}%)")
        
        # Route analysis
        if 'total_routes' in current_data.columns:
            total_routes = current_data['total_routes'].sum()
            insights.append(f"- **Route Coverage:** {total_routes} total routes")
        
        # Crowding information
        if 'crowding_available' in current_data.columns:
            crowding_data = current_data[current_data['crowding_available'] == True]
            if len(crowding_data) > 0:
                insights.append(f"- **Crowding Data:** Available for {len(crowding_data)} lines")
        
        # Historical performance
        if 'timestamp' in data.columns:
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_data = data[data['timestamp'] >= week_ago]
            
            if not recent_data.empty:
                # Reliability metrics
                on_time_percentage = self._calculate_reliability(recent_data)
                insights.append(f"- **Weekly Reliability:** {on_time_percentage:.1f}% on-time performance")
        
        # Specific prompt-based analysis
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['route', 'station', 'journey']):
            insights.extend(self._get_route_insights(data))
        
        if any(word in prompt_lower for word in ['crowding', 'capacity', 'passenger']):
            insights.extend(self._get_crowding_insights(data))
        
        if any(word in prompt_lower for word in ['service', 'schedule', 'frequency']):
            insights.extend(self._get_service_insights(data))
        
        if any(word in prompt_lower for word in ['predict', 'tomorrow', 'forecast']):
            insights.extend(self._generate_transport_predictions(data))
        
        return insights

    def _get_route_insights(self, data: pd.DataFrame) -> List[str]:

        """Generate route-specific insights"""
        insights = ["**Route Analysis:**"]
        
        try:
            if 'origin_stations' in data.columns and 'destination_stations' in data.columns:
                # Get most common routes
                all_origins = [origin for sublist in data['origin_stations'] for origin in sublist]
                all_destinations = [dest for sublist in data['destination_stations'] for dest in sublist]
                
                if all_origins and all_destinations:
                    from collections import Counter
                    common_origins = Counter(all_origins).most_common(3)
                    common_destinations = Counter(all_destinations).most_common(3)
                    
                    insights.append("- **Busiest Origins:** " + ", ".join([f"{station} ({count})" for station, count in common_origins]))
                    insights.append("- **Busiest Destinations:** " + ", ".join([f"{station} ({count})" for station, count in common_destinations]))
        except Exception as e:
            logger.warning(f"Error in route insights: {e}")
        
        return insights

    def _get_crowding_insights(self, data: pd.DataFrame) -> List[str]:
        """Generate crowding insights"""
        insights = ["**Passenger Capacity Analysis:**"]
        
        try:
            if 'crowding_level' in data.columns:
                crowding_levels = data['crowding_level'].value_counts()
                if not crowding_levels.empty:
                    insights.append("- **Crowding Distribution:**")
                    for level, count in crowding_levels.items():
                        if level != 'Unknown':
                            insights.append(f"  - {level}: {count} lines")
        except Exception as e:
            logger.warning(f"Error in crowding insights: {e}")
        
        return insights

    def _get_service_insights(self, data: pd.DataFrame) -> List[str]:
        """Generate service frequency and type insights"""
        insights = ["**Service Analysis:**"]
        
        try:
            if 'service_categories' in data.columns:
                all_categories = [cat for sublist in data['service_categories'] for cat in sublist]
                if all_categories:
                    from collections import Counter
                    common_services = Counter(all_categories).most_common(5)
                    insights.append("- **Service Types:** " + ", ".join([f"{service}" for service, count in common_services]))
        except Exception as e:
            logger.warning(f"Error in service insights: {e}")
        
        return insights

    def _calculate_reliability(self, data: pd.DataFrame) -> float:
        """Calculate service reliability percentage"""
        try:
            if 'delay_minutes' in data.columns:
                on_time_services = len(data[data['delay_minutes'] <= 5])  # ≤5 min delay considered on-time
                total_services = len(data)
                return (on_time_services / total_services) * 100 if total_services > 0 else 100
        except Exception as e:
            logger.warning(f"Error calculating reliability: {e}")
        
        return 0.0
    



    def _generate_delay_predictions(self, data: pd.DataFrame) -> List[str]:
        
        """Generate simple delay predictions based on historical patterns"""
        insights = []
        
        if data.empty:
            return insights
        
        insights.append("**Delay Predictions for Tomorrow:**")
        
        # Simple prediction based on recent patterns
        recent_data = data[data['timestamp'] >= (datetime.utcnow() - timedelta(days=3))]
        
        if not recent_data.empty:
            # Predict based on time of day patterns
            morning_data = recent_data[recent_data['timestamp'].dt.hour.between(7, 9)]
            evening_data = recent_data[recent_data['timestamp'].dt.hour.between(17, 19)]
            
            morning_delay = morning_data['delay_minutes'].mean() if not morning_data.empty else 0
            evening_delay = evening_data['delay_minutes'].mean() if not evening_data.empty else 0
            
            insights.append(f"- **Morning Rush (7-9 AM):** Expected {morning_delay:.1f} min delays")
            insights.append(f"- **Evening Rush (5-7 PM):** Expected {evening_delay:.1f} min delays")
            
            # Identify problematic lines
            line_delays = recent_data.groupby('line_name')['delay_minutes'].mean()
            problematic_lines = line_delays[line_delays > 5]
            
            if len(problematic_lines) > 0:
                insights.append("- **Lines to Watch:**")
                for line, delay in problematic_lines.nlargest(3).items():
                    insights.append(f"  - {line}: likely {delay:.1f} min delays")
        
        return insights
        





