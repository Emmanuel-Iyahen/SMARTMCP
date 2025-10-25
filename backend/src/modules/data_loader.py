
import pandas as pd
import asyncio
import aiohttp
import httpx
import os
import json
from sqlalchemy import text  
import random  
import numpy as np
import logging
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
from adapters.data_adapters import (
    CSVAdapter, JSONAdapter, APIAdapter, 
    DatabaseAdapter, WebScraperAdapter, RealTimeAdapter
)

load_dotenv()
logger = logging.getLogger(__name__)

class DataLoaderModule:
    def __init__(self):
        self.adapters = {
            'csv': CSVAdapter(),
            'json': JSONAdapter(),
            'api': APIAdapter(),
            'database': DatabaseAdapter(),
            'web': WebScraperAdapter(),
            'realtime': RealTimeAdapter()
        }
        self.snowflake_conn = self._init_snowflake()
    
    def _init_snowflake(self):
        """Initialize Snowflake connection with environment variables"""
        try:
            user = os.getenv("user")
            password = os.getenv("password")
            account = os.getenv("account")
            warehouse = os.getenv("warehouse")
            database = os.getenv("database")
            schema = os.getenv("schema")

            if not all([user, password, account]):
                logger.warning("⚠️ Missing Snowflake credentials in environment variables.")
                return None
            
            #logger.info(f"🔧 Connecting to Snowflake as {user}@{account} [{database}.{schema}]...")

            conn = snowflake.connector.connect(
                user=user,
                password=password,
                account=account,
                warehouse=warehouse,
                database=database,
                schema=schema
            )
            logger.info("✅ Successfully connected to Snowflake.")
            return conn

        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            return None
        

    def test_snowflake_connection(self):

        """Simple test to verify Snowflake connection initialization"""
        if self.snowflake_conn is None:
            print("❌ Test Failed: self.snowflake_conn is None — connection was not initialized.")
            return False
        try:
            cur = self.snowflake_conn.cursor()
            cur.execute("SELECT CURRENT_VERSION()")
            version = cur.fetchone()
            print(f"✅ Test Passed: Connected to Snowflake. Version: {version[0]}")
            return True
        except Exception as e:
            print(f"❌ Test Failed: Exception during query — {e}")
            return False

    
    async def load_data(self, source_type: str, config: Dict) -> pd.DataFrame:
        """Load data from various sources with error handling"""
        adapter = self.adapters.get(source_type)
        if not adapter:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        try:
            return await adapter.load_data(config)
        except Exception as e:
            logger.error(f"Error loading data from {source_type}: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error
        

    
    # async def load_uk_energy_data(self) -> pd.DataFrame:
    #     """Load real UK energy data from Carbon Intensity API"""
    #     try:
    #         config = {
    #             'url': 'https://api.carbonintensity.org.uk/generation',
    #             'headers': {'Accept': 'application/json'},
    #             'timeout': 30,
    #             'data_key': 'data'  # Extract data from the 'data' key
    #         }
            
    #         data = await self.load_data('api', config)
    #         if not data.empty:
    #             return self._process_energy_data(data)
            
    #         # Fallback to sample data if API fails
    #         return self._get_sample_energy_data()
            
    #     except Exception as e:
    #         logger.error(f"Error loading energy data: {e}")
    #         return self._get_sample_energy_data()
        



 
    

    async def load_transport_data(self) -> pd.DataFrame:

        """Load real TFL transportation data with proper processing"""
        try:
            app_id = os.getenv('TFL_APP_ID', '')
            app_key = os.getenv('TFL_APP_KEY', '')
            
            # Use string values for boolean parameters
            params = {'detail': 'true'}
            if app_id and app_key:
                params.update({'app_id': app_id, 'app_key': app_key})
            
            config = {
                'url': 'https://api.tfl.gov.uk/Line/Mode/tube,overground,dlr/Status',
                'params': params,
                'headers': {'Accept': 'application/json'},
                'timeout': 30
            }
            
            raw_data = await self.load_data('api', config)

            
            if not raw_data.empty:
                processed_data = self._process_tfl_data(raw_data)

                
                if not processed_data.empty:
                    print(f"Processed {len(processed_data)} transport records")
                    return processed_data
            
            # Fallback to sample data
            print("Using sample transport data")
            return self._get_sample_transport_data()
            
        except Exception as e:
            logger.error(f"Error loading transport data: {e}")
            print(f"Transport data error: {e}")
            return self._get_sample_transport_data()
        

        

    def _process_tfl_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Process raw TFL API response to extract delay information"""
        try:
            processed_records = []
            
            # Iterate through each line in the response
            for _, line in raw_data.iterrows():
                line_info = self._extract_line_info(line)
                if line_info:
                    processed_records.append(line_info)

            return pd.DataFrame(processed_records)
            
        except Exception as e:
            logger.error(f"Error processing TFL data: {e}")
            print(f"TFL processing error: {e}")
            return pd.DataFrame()
        

        #here

    def _extract_line_info(self, line_data) -> dict:

        """Extract comprehensive information from a single line's data"""
        try:
            # Basic line information
            line_id = line_data.get('id', 'unknown')
            line_name = line_data.get('name', 'Unknown Line')
            mode_name = line_data.get('modeName', 'Unknown Mode')
            created = line_data.get('created', '')
            modified = line_data.get('modified', '')
            
            # Line details
            line_details = {
                'line_id': line_id,
                'line_name': line_name,
                'mode': mode_name,
                'timestamp': datetime.utcnow(),
                'created_date': created,
                'modified_date': modified,
            }
            
            # Extract service types
            service_types = line_data.get('serviceTypes', [])
            line_details.update(self._extract_service_types(service_types))
            
            # Extract line statuses (delays, disruptions)
            line_statuses = line_data.get('lineStatuses', [])
            status_info = self._extract_status_info(line_statuses)
            line_details.update(status_info)
            
            # Extract route information
            route_sections = line_data.get('routeSections', [])
            line_details.update(self._extract_route_info(route_sections))
            
            # Extract crowding information
            crowding = line_data.get('crowding', {})
            line_details.update(self._extract_crowding_info(crowding))
            
            # Extract additional properties
            line_details.update({
                'disruption_reasons': self._extract_disruption_reasons(line_statuses),
                'validity_periods': self._extract_validity_periods(line_data),
                'is_night_service': self._is_night_service(service_types),
            })
            
            return line_details
            
        except Exception as e:
            logger.warning(f"Error extracting line info: {e}")
            return None

    def _extract_service_types(self, service_types: list) -> dict:
        """Extract service type information"""
        info = {
            'regular_service': False,
            'night_service': False,
            'service_categories': []
        }
        
        try:
            for service in service_types:
                if isinstance(service, dict):
                    service_name = service.get('name', '')
                    if 'Regular' in service_name:
                        info['regular_service'] = True
                    if 'Night' in service_name:
                        info['night_service'] = True
                    info['service_categories'].append(service_name)
            
            info['service_categories'] = list(set(info['service_categories']))
        except Exception as e:
            logger.warning(f"Error extracting service types: {e}")
        
        return info

    def _extract_route_info(self, route_sections: list) -> dict:
        """Extract route section information"""
        info = {
            'total_routes': len(route_sections),
            'origin_stations': [],
            'destination_stations': [],
            'route_names': []
        }
        
        try:
            for route in route_sections:
                if isinstance(route, dict):
                    info['origin_stations'].append(route.get('originator', 'Unknown'))
                    info['destination_stations'].append(route.get('destination', 'Unknown'))
                    info['route_names'].append(route.get('name', 'Unknown Route'))
            
            info['origin_stations'] = list(set(info['origin_stations']))
            info['destination_stations'] = list(set(info['destination_stations']))
            info['route_names'] = list(set(info['route_names']))
        except Exception as e:
            logger.warning(f"Error extracting route info: {e}")
        
        return info

    def _extract_crowding_info(self, crowding: dict) -> dict:
        """Extract crowding information"""
        info = {
            'crowding_available': False,
            'crowding_level': 'Unknown',
            'passenger_capacity': 0,
            'current_load': 0
        }
        
        try:
            if crowding and isinstance(crowding, dict):
                info['crowding_available'] = True
                info['crowding_level'] = crowding.get('level', 'Unknown')
                # Additional crowding metrics can be extracted here
        except Exception as e:
            logger.warning(f"Error extracting crowding info: {e}")
        
        return info

    def _extract_disruption_reasons(self, line_statuses: list) -> list:
        """Extract all disruption reasons"""
        reasons = []
        
        try:
            for status in line_statuses:
                if isinstance(status, dict):
                    reason = status.get('reason', '')
                    if reason and reason not in reasons:
                        reasons.append(reason)
                    
                    # Extract from disruption object
                    disruption = status.get('disruption', {})
                    if disruption:
                        disruption_reason = disruption.get('description', '')
                        if disruption_reason and disruption_reason not in reasons:
                            reasons.append(disruption_reason)
        except Exception as e:
            logger.warning(f"Error extracting disruption reasons: {e}")
        
        return reasons

    def _extract_validity_periods(self, line_data: dict) -> list:
        """Extract validity periods for the line"""
        periods = []
        
        try:
            validity_periods = line_data.get('validityPeriods', [])
            for period in validity_periods:
                if isinstance(period, dict):
                    from_date = period.get('fromDate', '')
                    to_date = period.get('toDate', '')
                    is_now = period.get('isNow', False)
                    
                    periods.append({
                        'from_date': from_date,
                        'to_date': to_date,
                        'is_current': is_now
                    })
        except Exception as e:
            logger.warning(f"Error extracting validity periods: {e}")
        
        return periods

    def _is_night_service(self, service_types: list) -> bool:
        """Check if this is a night service"""
        try:
            for service in service_types:
                if isinstance(service, dict) and 'Night' in service.get('name', ''):
                    return True
        except Exception as e:
            logger.warning(f"Error checking night service: {e}")
        
        return False

    def _extract_status_info(self, line_statuses: list) -> dict:
        """Extract status information from line statuses array"""
        default_status = {
            'status': 'Good Service',
            'severity': 10,
            'reason': '',
            'category': 'None',
            'delay_minutes': 0,
            'is_active': True
        }
        
        if not line_statuses:
            return default_status
        
        try:
            # Get the first status (usually the most relevant)
            status = line_statuses[0] if isinstance(line_statuses, list) else line_statuses
            
            status_text = status.get('statusSeverityDescription', 'Good Service')
            severity = status.get('statusSeverity', 10)
            reason = status.get('reason', '')
            
            # Extract disruption category if available
            disruption = status.get('disruption', {})
            category = disruption.get('category', 'None') if disruption else 'None'
            
            # Estimate delay minutes based on status severity
            delay_minutes = self._estimate_delay_from_severity(severity, status_text)
            
            # Check if service is active
            is_active = severity < 20  # Assuming severity >= 20 means not active
            
            return {
                'status': status_text,
                'severity': severity,
                'reason': reason,
                'category': category,
                'delay_minutes': delay_minutes,
                'is_active': is_active
            }
            
        except Exception as e:
            logger.warning(f"Error extracting status info: {e}")
            return default_status

    def _estimate_delay_from_severity(self, severity: int, status_text: str) -> int:
        """Estimate delay minutes based on status severity and text"""
        status_lower = status_text.lower()
        
        # Map severity to delay minutes
        if severity <= 3:
            return 0  # Good service
        elif severity <= 6:
            return 5  # Minor delays
        elif severity <= 9:
            return 15  # Severe delays
        else:
            return 30  # Service closed/part closed
        
        # Additional checks based on status text
        if 'good service' in status_lower:
            return 0
        elif 'minor' in status_lower:
            return 5
        elif 'severe' in status_lower or 'part closure' in status_lower:
            return 20
        elif 'closed' in status_lower or 'suspended' in status_lower:
            return 60  # Major disruption
        else:
            return 10  # Default delay

    def _get_sample_transport_data(self) -> pd.DataFrame:
        
        """Sample transport data for development with realistic delays"""
        lines = [
            'Victoria', 'Central', 'Jubilee', 'Northern', 'Piccadilly',
            'District', 'Circle', 'Bakerloo', 'Metropolitan', 'DLR'
        ]
        
        # Realistic status scenarios
        status_scenarios = [
            {'status': 'Good Service', 'severity': 10, 'delay': 0},
            {'status': 'Minor Delays', 'severity': 7, 'delay': 5},
            {'status': 'Severe Delays', 'severity': 4, 'delay': 15},
            {'status': 'Part Suspended', 'severity': 2, 'delay': 30},
            {'status': 'Special Service', 'severity': 8, 'delay': 3}
        ]
        
        records = []
        base_time = datetime.utcnow()
        
        # Generate data for the past 7 days
        for day in range(7):
            for hour in range(24):
                timestamp = base_time - timedelta(days=day, hours=hour)
                
                for i, line in enumerate(lines):
                    scenario = status_scenarios[i % len(status_scenarios)]
                    
                    records.append({
                        'timestamp': timestamp,
                        'line_id': f'line_{line.lower().replace(" ", "_")}',
                        'line_name': line,
                        'mode': 'tube' if line != 'DLR' else 'dlr',
                        'status': scenario['status'],
                        'status_severity': scenario['severity'],
                        'reason': 'Signal failure' if scenario['delay'] > 10 else 'No issues',
                        'disruption_category': 'SignalFailure' if scenario['delay'] > 10 else 'None',
                        'delay_minutes': scenario['delay'],
                        'is_active': scenario['severity'] > 5
                    })
        
        return pd.DataFrame(records)
    



    
    # async def load_financial_data(self) -> pd.DataFrame:
    #     """Load UK financial market data with proper error handling"""
    #     try:
    #         api_key = os.getenv('alphavantage1')
    #         if not api_key:
    #             logger.warning("Alpha Vantage API key not configured")
    #             return self._get_sample_financial_data()
            
    #         symbols = [
    #             'HSBA.L',  # HSBC Holdings
    #             'BP.L',    # BP
    #             'GSK.L',   # GSK
    #             'ULVR.L',  # Unilever
    #             'AZN.L',   # AstraZeneca
    #             'RIO.L',   # Rio Tinto
    #             'LLOY.L',  # Lloyds Banking Group
    #             'BARC.L',  # Barclays
    #             'TSCO.L',  # Tesco
    #         ]
            
    #         all_data = []
            
    #         for symbol in symbols:
    #             try:
    #                 config = {
    #                     'url': 'https://www.alphavantage.co/query',
    #                     'params': {
    #                         'function': 'TIME_SERIES_DAILY',
    #                         'symbol': symbol,
    #                         'apikey': api_key,
    #                         'outputsize': 'compact'
    #                     },
    #                     'timeout': 30
    #                 }
                    
    #                 # Use your existing load_data method
    #                 data = await self.load_data('api', config)
    #                 print(f"🔍 Raw data for {symbol}:")
    #                 print(f"   Shape: {data.shape}")
    #                 print(f"   Columns: {list(data.columns)}")
                    
    #                 if not data.empty:
    #                     # Debug what's actually in the data
                        
                        
    #                     # Check if it's an error message
    #                     if 'Information' in data.columns:
    #                         info_msg = data['Information'].iloc[0]
    #                         print(f"❌ API Info for {symbol}: {info_msg}")
    #                         continue
    #                     elif 'Error Message' in data.columns:
    #                         error_msg = data['Error Message'].iloc[0]
    #                         print(f"❌ API Error for {symbol}: {error_msg}")
    #                         continue
    #                     elif 'Note' in data.columns:
    #                         note_msg = data['Note'].iloc[0]
    #                         print(f"💡 API Note for {symbol}: {note_msg}") 
    #                         continue
                        
    #                     # Try to process the data
    #                     processed_data = self._process_alpha_vantage_data_fixed(data, symbol)
    #                     print('processed financial stock data to view snowflake structure: ', processed_data)
    #                     if not processed_data.empty:
    #                         store_in_snowflake = await self.store_processed_financial_data_simple(processed_data)
    #                         if store_in_snowflake:
    #                             print('stored in snowflake')
    #                         else:
    #                             print('snowflake storage failed')
    #                         all_data.append(processed_data)
    #                         print(f"✅ Processed data for {symbol}: {len(processed_data)} records")
    #                     else:
    #                         print(f"❌ No processed data for {symbol}")
    #                 else:
    #                     print(f"❌ Empty data for {symbol}")
                            
    #             except Exception as e:
    #                 print(f"❌ Error loading {symbol}: {e}")
    #                 continue
            
    #         if all_data:
    #             combined_data = pd.concat(all_data, ignore_index=True)
    #             print(f"📊 Combined financial data: {len(combined_data)} total records")
                
    #             if not combined_data.empty:
    #                 print(f"📈 Sample processed data:")
    #                 print(combined_data[['timestamp', 'symbol', 'company_name', 'close', 'volume']].head())
                
    #             return combined_data
    #         else:
    #             print("📝 Using sample financial data - API may be rate limited")
    #             return self._get_sample_financial_data()
                    
    #     except Exception as e:
    #         logger.error(f"Error loading financial data: {e}")
    #         return self._get_sample_financial_data()

    def _process_alpha_vantage_data_fixed(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Process Alpha Vantage data with better error handling"""
        try:
            company_names = {
                'HSBA.L': 'HSBC Holdings',
                'BP.L': 'BP',
                'GSK.L': 'GSK', 
                'ULVR.L': 'Unilever',
                'AZN.L': 'AstraZeneca',
                'RIO.L': 'Rio Tinto',
                'LLOY.L': 'Lloyds Banking Group',
                'BARC.L': 'Barclays',
                'TSCO.L': 'Tesco'
            }
            
            records = []
            
            # Check if we have the expected time series data structure
            if 'Time Series (Daily)' in data.columns:
                time_series_data = data['Time Series (Daily)'].iloc[0]
                if isinstance(time_series_data, dict):
                    for date_str, values in list(time_series_data.items())[:5]:  # Last 5 days
                        if isinstance(values, dict):
                            records.append({
                                'timestamp': pd.to_datetime(date_str),
                                'symbol': symbol,
                                'company_name': company_names.get(symbol, symbol),
                                'open': float(values.get('1. open', 0)),
                                'high': float(values.get('2. high', 0)),
                                'low': float(values.get('3. low', 0)),
                                'close': float(values.get('4. close', 0)),
                                'volume': int(values.get('5. volume', 0))
                            })
            
            # Alternative: Check if data is already in the column-based format we saw earlier
            elif any(col not in ['symbol', 'company_name', 'Information', 'Error Message', 'Note'] for col in data.columns):
                # This handles the format where each column is a date containing OHLC dict
                for _, row in data.iterrows():
                    for col in data.columns:
                        if col not in ['symbol', 'company_name', 'Information', 'Error Message', 'Note']:
                            cell_data = row[col]
                            if isinstance(cell_data, dict):
                                records.append({
                                    'timestamp': pd.to_datetime(col),
                                    'symbol': symbol,
                                    'company_name': company_names.get(symbol, symbol),
                                    'open': float(cell_data.get('1. open', 0)),
                                    'high': float(cell_data.get('2. high', 0)),
                                    'low': float(cell_data.get('3. low', 0)),
                                    'close': float(cell_data.get('4. close', 0)),
                                    'volume': int(cell_data.get('5. volume', 0))
                                })
            
            return pd.DataFrame(records)
            
        except Exception as e:
            print(f"Error processing Alpha Vantage data for {symbol}: {e}")
            return pd.DataFrame()

    def _get_sample_financial_data(self) -> pd.DataFrame:
        """Generate realistic sample financial data"""
        print("📝 Generating realistic sample financial data...")
        
        companies = [
            {'symbol': 'HSBA.L', 'name': 'HSBC Holdings', 'sector': 'Banking', 'base_price': 650},
            {'symbol': 'BP.L', 'name': 'BP', 'sector': 'Energy', 'base_price': 480},
            {'symbol': 'GSK.L', 'name': 'GSK', 'sector': 'Pharmaceuticals', 'base_price': 1450},
            {'symbol': 'ULVR.L', 'name': 'Unilever', 'sector': 'Consumer Goods', 'base_price': 4200},
            {'symbol': 'AZN.L', 'name': 'AstraZeneca', 'sector': 'Pharmaceuticals', 'base_price': 10500},
            {'symbol': 'RIO.L', 'name': 'Rio Tinto', 'sector': 'Mining', 'base_price': 5200},
            {'symbol': 'LLOY.L', 'name': 'Lloyds Banking Group', 'sector': 'Banking', 'base_price': 52},
            {'symbol': 'BARC.L', 'name': 'Barclays', 'sector': 'Banking', 'base_price': 180},
            {'symbol': 'TSCO.L', 'name': 'Tesco', 'sector': 'Retail', 'base_price': 290}
        ]
        
        records = []
        base_date = datetime.now()
        
        for company in companies:
            base_price = company['base_price']
            base_volume = 1000000
            
            # Generate data for last 5 days with realistic price movements
            for days_ago in range(5):
                date = base_date - timedelta(days=days_ago)
                
                # Simulate realistic daily price movements (±2-5%)
                daily_change_pct = (np.random.random() - 0.5) * 0.1  # ±5%
                close_price = base_price * (1 + daily_change_pct)
                
                # Generate OHLC with realistic spreads
                open_price = close_price * (1 + (np.random.random() - 0.5) * 0.02)
                high_price = max(open_price, close_price) * (1 + np.random.random() * 0.03)
                low_price = min(open_price, close_price) * (1 - np.random.random() * 0.03)
                
                # Volume with some randomness
                volume = base_volume * (0.8 + np.random.random() * 0.4)
                
                records.append({
                    'timestamp': date,
                    'symbol': company['symbol'],
                    'company_name': company['name'],
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': int(volume)
                })
        
        df = pd.DataFrame(records)
        print(f"📊 Generated realistic sample data: {len(df)} records for {len(companies)} companies")
        return df


    async def _make_api_request(self, config):
        """Make API request and return JSON data"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    config['url'],
                    params=config['params'],
                    timeout=config['timeout']
                )
                return response.json()
        except Exception as e:
            print(f"API request error: {e}")
            return None

    
    async def load_weather_data(self) -> pd.DataFrame:
        """Load UK weather data from Open-Meteo (free, no API key required)"""
        try:
            # Get London weather data
            config = {
                'url': 'https://api.open-meteo.com/v1/forecast',
                'params': {
                    'latitude': 51.5074,
                    'longitude': -0.1278,
                    'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code',
                    'timezone': 'Europe/London'
                },
                'timeout': 30,
                'data_key': 'current'
            }
            
            data = await self.load_data('api', config)

        
            if not data.empty:
                return self._process_weather_data(data)
            
            return self._get_sample_weather_data()
            
        except Exception as e:
            logger.error(f"Error loading weather data: {e}")
            return self._get_sample_weather_data()
    

    
    
    
    def _process_weather_data(self, data: pd.DataFrame) -> pd.DataFrame:

        """Process weather API response"""
        try:
            if not data.empty:
                
                return pd.DataFrame([{
                    'timestamp': datetime.utcnow(),
                    'temperature': data.iloc[0].get('temperature_2m', 0),
                    'humidity': data.iloc[0].get('relative_humidity_2m', 0),
                    'precipitation': data.iloc[0].get('precipitation', 0),
                    'weather_code': data.iloc[0].get('weather_code', 0),
                    'location': 'London'
                }])
            
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return pd.DataFrame()
    
    def _extract_disruption_details(self, line_data) -> str:
        """Extract disruption details from TFL data"""
        try:
            statuses = line_data.get('lineStatuses', [])
            if statuses:
                reasons = [s.get('reason', '') for s in statuses if s.get('reason')]
                return '; '.join(reasons) if reasons else 'No disruption'
            return 'No disruption'
        except:
            return 'Unknown'
    
    def _estimate_delay_minutes(self, status: str) -> int:
        """Estimate delay minutes based on status description"""
        status_lower = status.lower()
        if 'severe' in status_lower:
            return 30
        elif 'minor' in status_lower:
            return 5
        elif 'good service' in status_lower:
            return 0
        else:
            return 10  # Default for other statuses
    

    
    def _get_sample_transport_data(self) -> pd.DataFrame:
        """Sample transport data for development"""
        lines = ['Victoria', 'Central', 'Jubilee', 'Northern', 'Piccadilly']
        statuses = ['Good Service', 'Minor Delays', 'Severe Delays', 'Part Suspended']
        
        return pd.DataFrame([
            {
                'timestamp': datetime.utcnow(),
                'line_id': f'line_{i}',
                'line_name': line,
                'mode': 'tube',
                'status': statuses[i % len(statuses)],
                'status_severity': 10 - (i % 4) * 3,
                'reason': 'Signal failure' if i % 3 == 0 else 'No issues',
                'delay_minutes': (i % 4) * 5
            }
            for i, line in enumerate(lines)
        ])
    
    def _get_sample_financial_data(self) -> pd.DataFrame:
        """Sample financial data for development"""
        return pd.DataFrame([
            {
                'timestamp': datetime.utcnow() - timedelta(days=i),
                'symbol': 'FTSE',
                'open': 7500 + i * 10,
                'high': 7550 + i * 10,
                'low': 7450 + i * 10,
                'close': 7520 + i * 10,
                'volume': 1000000 + i * 10000
            }
            for i in range(30, 0, -1)
        ])
    
    def _get_sample_weather_data(self) -> pd.DataFrame:
        """Sample weather data for development"""
        return pd.DataFrame([{
            'timestamp': datetime.utcnow(),
            'temperature': 15.5,
            'humidity': 65,
            'precipitation': 0.0,
            'weather_code': 3,  # Partly cloudy
            'location': 'London'
        }])

        


    async def store_processed_financial_data_simple(self, processed_data: pd.DataFrame) -> bool:
        """Simplified approach using write_pandas"""
        try:
            if self.snowflake_conn is None:
                print("⚠️ Snowflake not connected, skipping processed data storage")
                return False
            
            # Use Snowflake's built-in method
            from snowflake.connector.pandas_tools import write_pandas
            
            # Create a copy to avoid modifying the original DataFrame
            df_to_store = processed_data.copy()
            
            # FIX 1: Convert all column names to uppercase
            df_to_store.columns = [col.upper() for col in df_to_store.columns]

            if 'TIMESTAMP' in df_to_store.columns:
                df_to_store['TIMESTAMP'] = pd.to_datetime(df_to_store['TIMESTAMP'], errors='coerce')
                df_to_store['TIMESTAMP'] = df_to_store['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M:%S')

            print('data types going to snowflake are:', df_to_store.dtypes)
            
            
            success, nchunks, nrows, _ = write_pandas(
                conn=self.snowflake_conn,
                df=df_to_store,
                table_name='FINANCIAL_MARKET_DATA_PROCESSED',
                schema='FINANCE',
                database='MCP_PLATFORM',
                auto_create_table=False,
                overwrite=False
            )
            
            print(f"📊 write_pandas result: success={success}, chunks={nchunks}, rows={nrows}")
            return success
            
        except Exception as e:
            print(f"❌ Error with write_pandas: {e}")
            return False
        



    # Add this method to your DataLoaderModule class

    async def load_financial_data_from_snowflake(self) -> pd.DataFrame:
        """Load financial market data from Snowflake using snowflake-connector"""
        try:
            if hasattr(self, 'snowflake_conn') and self.snowflake_conn:
                query = """
                SELECT 
                    SYMBOL,
                    COMPANY_NAME,
                    OPEN,
                    HIGH,
                    LOW,
                    CLOSE,
                    VOLUME,
                    TIMESTAMP
                FROM MCP_PLATFORM.FINANCE.FINANCIAL_MARKET_DATA_PROCESSED 
                WHERE TIMESTAMP >= DATEADD(day, -7, CURRENT_DATE())
                ORDER BY TIMESTAMP DESC, SYMBOL
                """
                
                # Use snowflake-connector's cursor
                cursor = self.snowflake_conn.cursor()
                cursor.execute(query)
                
                # Fetch all results
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                # Create DataFrame
                df = pd.DataFrame(rows, columns=columns)
                cursor.close()
                    
                print(f"📊 Loaded {len(df)} financial records from Snowflake")
                return df
                
            else:
                logger.warning("Snowflake connection not available, returning sample financial data")
                return self._get_sample_financial_data()
                
        except Exception as e:
            logger.error(f"Error loading financial data: {e}")
            return self._get_sample_financial_data()
        

    def _get_sample_financial_data(self) -> pd.DataFrame:
        """Generate sample financial data for testing"""
        symbols = ['HSBA.L', 'BP.L', 'GSK.L', 'ULVR.L', 'AZN.L', 'RIO.L', 'LLOY.L', 'BARC.L']
        companies = ['HSBC Holdings', 'BP', 'GSK', 'Unilever', 'AstraZeneca', 'Rio Tinto', 'Lloyds Banking', 'Barclays']
        
        data = []
        base_date = datetime.now() - timedelta(days=5)
        
        for i, (symbol, company) in enumerate(zip(symbols, companies)):
            for day in range(5):
                timestamp = base_date + timedelta(days=day)
                base_price = 1000 + (i * 100)  # Vary base price by symbol
                close_price = base_price + random.uniform(-50, 50)
                
                data.append({
                    'SYMBOL': symbol,
                    'COMPANY_NAME': company,
                    'SECTOR': 'Finance',
                    'OPEN_PRICE': base_price,
                    'HIGH_PRICE': close_price + random.uniform(5, 20),
                    'LOW_PRICE': close_price - random.uniform(5, 20),
                    'CLOSE_PRICE': close_price,
                    'VOLUME': random.randint(1000000, 50000000),
                    'TIMESTAMP': timestamp
                })
        
        return pd.DataFrame(data)
    


    

    async def load_financial_trend_data(self) -> pd.DataFrame:
        """Load extended historical financial data from Snowflake for trend analysis"""
        try:
            conn = self._init_snowflake()

            if hasattr(self, 'snowflake_conn') and conn:
                print('new snowflake session successful')
                query = """
                SELECT 
                    SYMBOL,
                    COMPANY_NAME,
                    OPEN,
                    HIGH,
                    LOW,
                    CLOSE,
                    VOLUME,
                    TIMESTAMP
                FROM MCP_PLATFORM.FINANCE.FINANCIAL_MARKET_DATA_PROCESSED 
                WHERE TIMESTAMP >= DATEADD(month, -3, CURRENT_DATE())  -- 3 months of data for trends
                ORDER BY TIMESTAMP DESC, SYMBOL
                """
                
                cursor = self.snowflake_conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                df = pd.DataFrame(rows, columns=columns)
                cursor.close()
                    
                print(f"📈 Loaded {len(df)} historical records for trend analysis")
                return df
            else:
                logger.warning("Snowflake connection not available, returning sample trend data")
                return self._get_sample_trend_data()
                
        except Exception as e:
            logger.error(f"Error loading trend data: {e}")
            return self._get_sample_trend_data()



    def _process_financial_trends(self, trend_data: pd.DataFrame) -> Dict[str, Any]:
            
        """Process historical data for trend analysis - FIXED for available data"""
        try:
            if trend_data.empty:
                return self._get_sample_trend_analysis()
                
            trend_data = trend_data.copy()
            trend_data['TIMESTAMP'] = pd.to_datetime(trend_data['TIMESTAMP'])
            trend_data['DATE'] = trend_data['TIMESTAMP'].dt.date
            
            print(f"🔍 Trend Analysis - Data Summary:")
            print(f"   - Total records: {len(trend_data)}")
            print(f"   - Date range: {trend_data['DATE'].min()} to {trend_data['DATE'].max()}")
            print(f"   - Unique trading days: {trend_data['DATE'].nunique()}")
            print(f"   - Unique symbols: {trend_data['SYMBOL'].nunique()}")
            
            # Use available days instead of fixed 30-day window
            available_days = trend_data['DATE'].nunique()
            analysis_period = min(available_days, 30)  # Use available data, max 30 days
            
            if available_days < 5:
                print(f"⚠️ Insufficient data ({available_days} days) for meaningful trend analysis")
                return self._get_sample_trend_analysis()

            # Group by date for market-level trends
            daily_market = trend_data.groupby('DATE').agg({
                'CLOSE': 'mean',
                'VOLUME': 'sum',
                'SYMBOL': 'count'
            }).reset_index()
            
            daily_market = daily_market.sort_values('DATE')
            
            # Calculate market trends
            daily_market['price_change'] = daily_market['CLOSE'].pct_change() * 100
            daily_market['volume_change'] = daily_market['VOLUME'].pct_change() * 100
            
            # Use available period for analysis
            recent_period = daily_market.tail(analysis_period)
            
            # Prepare market trend data for charts
            market_trends = []
            for _, row in recent_period.iterrows():
                market_trends.append({
                    'date': row['DATE'].isoformat(),
                    'price': round(float(row['CLOSE']), 2),
                    'volume': int(row['VOLUME']),
                    'price_change': round(float(row['price_change']), 2) if not pd.isna(row['price_change']) else 0,
                    'stocks_traded': int(row['SYMBOL'])
                })
            
            # Calculate performance metrics for available period
            if len(recent_period) >= 2:
                start_price = recent_period['CLOSE'].iloc[0]
                end_price = recent_period['CLOSE'].iloc[-1]
                total_return = ((end_price - start_price) / start_price) * 100 if start_price > 0 else 0
                avg_daily_return = recent_period['price_change'].mean()
                volatility = recent_period['price_change'].std()
            else:
                total_return = avg_daily_return = volatility = 0
            
            # Individual stock performance for the available period
            stock_trends = []
            for symbol, symbol_data in trend_data.groupby('SYMBOL'):
                symbol_data = symbol_data.sort_values('DATE')
                symbol_recent = symbol_data[symbol_data['DATE'].isin(recent_period['DATE'])]
                
                if len(symbol_recent) >= 2:
                    symbol_recent = symbol_recent.sort_values('DATE')
                    start_price = symbol_recent['CLOSE'].iloc[0]
                    end_price = symbol_recent['CLOSE'].iloc[-1]
                    
                    if start_price > 0:
                        period_change = ((end_price - start_price) / start_price) * 100
                    else:
                        period_change = 0
                    
                    stock_trends.append({
                        'symbol': symbol,
                        'company': symbol_data['COMPANY_NAME'].iloc[0],
                        'period_change': round(period_change, 2),
                        'start_price': round(float(start_price), 2),
                        'end_price': round(float(end_price), 2),
                        'volatility': round(symbol_recent['CLOSE'].std() / symbol_recent['CLOSE'].mean() * 100, 2) if symbol_recent['CLOSE'].mean() > 0 else 0
                    })
            
            if not stock_trends:
                return self._get_sample_trend_analysis()
            
            stock_trends.sort(key=lambda x: x['period_change'], reverse=True)
            
            # Update metric names to reflect actual period
            period_name = f"{analysis_period}-Day" if analysis_period >= 10 else f"{analysis_period}-Day"
            
            # Enhanced trend indicators
            trend_status = "Bullish" if total_return > 2 else "Neutral" if total_return > -2 else "Bearish"
            volatility_status = "High" if volatility > 3 else "Moderate" if volatility > 1.5 else "Low"
            momentum_status = "Positive" if avg_daily_return > 0.1 else "Neutral" if avg_daily_return > -0.1 else "Negative"
            
            print(f"📊 Calculated Metrics ({period_name} Period):")
            print(f"   - Return: {total_return:+.2f}%")
            print(f"   - Avg Daily Return: {avg_daily_return:+.2f}%")
            print(f"   - Volatility: {volatility:.2f}%")
            
            return {
                'market_trends': market_trends,
                'performance_metrics': [
                    {'name': f'{period_name} Return', 'value': f'{total_return:+.2f}%'},
                    {'name': 'Avg Daily Return', 'value': f'{avg_daily_return:+.2f}%'},
                    {'name': 'Volatility', 'value': f'{volatility:.2f}%'},
                    {'name': 'Best Performer', 'value': f'{stock_trends[0]["symbol"]} ({stock_trends[0]["period_change"]:+.2f}%)'},
                    {'name': 'Worst Performer', 'value': f'{stock_trends[-1]["symbol"]} ({stock_trends[-1]["period_change"]:+.2f}%)'}
                ],
                'trend_indicators': [
                    {'name': 'Market Trend', 'status': trend_status},
                    {'name': 'Volatility Level', 'status': volatility_status},
                    {'name': 'Momentum', 'status': momentum_status}
                ],
                'stock_performance': [
                    {
                        'symbol': stock['symbol'],
                        'company': stock['company'],
                        'change': stock['period_change'],
                        'volatility': stock['volatility']
                    } for stock in stock_trends
                ],
                'analysis_period': period_name,
                'data_coverage': f"{available_days} days",
                'volatility_data': [
                    {
                        'date': day['date'],
                        'volatility': abs(day['price_change'])
                    } for day in market_trends
                ],
                'moving_averages': self._calculate_moving_averages(market_trends),
                'sector_performance': self._analyze_sectors(trend_data),
                'sector_rankings': self._rank_sectors(trend_data)
            }
            
        except Exception as e:
            logger.error(f"Error processing trend data: {e}")
            return self._get_sample_trend_analysis()




    def _calculate_moving_averages(self, market_trends: List[Dict]) -> List[Dict]:
        """Calculate 7-day and 30-day moving averages"""
        try:
            ma_data = []
            for i, day in enumerate(market_trends):
                if i >= 6:  # 7-day MA requires 7 data points
                    seven_day_avg = sum(d['price'] for d in market_trends[i-6:i+1]) / 7
                else:
                    seven_day_avg = day['price']
                    
                if i >= 29:  # 30-day MA requires 30 data points
                    thirty_day_avg = sum(d['price'] for d in market_trends[i-29:i+1]) / 30
                else:
                    thirty_day_avg = day['price']
                
                ma_data.append({
                    'date': day['date'],
                    'price': day['price'],
                    'price_7d': round(seven_day_avg, 2),
                    'price_30d': round(thirty_day_avg, 2)
                })
            return ma_data
        except Exception as e:
            logger.error(f"Error calculating moving averages: {e}")
            return []

    def _analyze_sectors(self, trend_data: pd.DataFrame) -> List[Dict]:
        """Analyze performance by sector (simplified - you might have actual sector data)"""
        # This is a simplified version - you would map symbols to actual sectors
        try:
            # Group by first letter of symbol as a pseudo-sector for demo
            trend_data['sector'] = trend_data['SYMBOL'].str[0]
            
            sector_performance = []
            for sector, sector_data in trend_data.groupby('sector'):
                if len(sector_data) < 2:
                    continue
                    
                sector_data = sector_data.sort_values('TIMESTAMP')
                start_avg = sector_data.groupby('DATE')['CLOSE'].mean().iloc[0]
                end_avg = sector_data.groupby('DATE')['CLOSE'].mean().iloc[-1]
                performance = ((end_avg - start_avg) / start_avg) * 100
                
                sector_performance.append({
                    'sector': f"Sector {sector}",
                    'performance': round(performance, 2),
                    'stock_count': len(sector_data['SYMBOL'].unique())
                })
            
            return sector_performance
        except Exception as e:
            logger.error(f"Error analyzing sectors: {e}")
            return []

    def _rank_sectors(self, trend_data: pd.DataFrame) -> List[Dict]:
        """Rank sectors by performance"""
        sector_data = self._analyze_sectors(trend_data)
        sector_data.sort(key=lambda x: x['performance'], reverse=True)
        
        return [
            {
                'name': sector['sector'],
                'change': sector['performance'],
                'trend': 'Outperforming' if sector['performance'] > 0 else 'Underperforming'
            } for sector in sector_data
        ]

    # Add these sample data methods for fallback
    def _get_sample_trend_data(self) -> pd.DataFrame:
        """Generate sample trend data for development"""
        # Implementation similar to your existing sample data method
        pass
        
    def _get_sample_trend_analysis(self) -> Dict[str, Any]:
        """Generate sample trend analysis for development"""
        # Implementation similar to your existing sample method
        pass