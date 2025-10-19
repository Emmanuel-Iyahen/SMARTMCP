# airflow/etl/financial_loader.py

import os
import pandas as pd
import asyncio
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
from typing import Dict, List, Any, Optional
import logging
from dotenv import load_dotenv
from .data_adapters import (
    CSVAdapter, JSONAdapter, APIAdapter, 
    DatabaseAdapter, WebScraperAdapter, RealTimeAdapter
)

load_dotenv()
logger = logging.getLogger(__name__)

class FinancialDataLoader:
        
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
            return snowflake.connector.connect(
                user = os.getenv("user"),
                password = os.getenv("password"),
                account = os.getenv("account"),
                warehouse = os.getenv("warehouse"),
                database = os.getenv("database"),
                schema = os.getenv("schema")
            )
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {e}")
            return None


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
    
    async def load_financial_data(self) -> pd.DataFrame:
            """Load UK financial market data with proper error handling"""
            try:
                api_key = os.getenv('alphavantage1')
                if not api_key:
                    logger.warning("Alpha Vantage API key not configured")
                    return self._get_sample_financial_data()
                
                symbols = [
                    'HSBA.L',  # HSBC Holdings
                    'BP.L',    # BP
                    'GSK.L',   # GSK
                    'ULVR.L',  # Unilever
                    'AZN.L',   # AstraZeneca
                    'RIO.L',   # Rio Tinto
                    'LLOY.L',  # Lloyds Banking Group
                    'BARC.L',  # Barclays
                    'TSCO.L',  # Tesco
                ]
                
                all_data = []
                
                for symbol in symbols:
                    try:
                        config = {
                            'url': 'https://www.alphavantage.co/query',
                            'params': {
                                'function': 'TIME_SERIES_DAILY',
                                'symbol': symbol,
                                'apikey': api_key,
                                'outputsize': 'compact'
                            },
                            'timeout': 30
                        }
                        
                        # Use your existing load_data method
                        data = await self.load_data('api', config)
                        print(f"🔍 Raw data for {symbol}:")
                        print(f"   Shape: {data.shape}")
                        print(f"   Columns: {list(data.columns)}")
                        
                        if not data.empty:
                            # Debug what's actually in the data
                            print(f"   First row: {data.iloc[0].to_dict()}")
                            
                            # Check if it's an error message
                            if 'Information' in data.columns:
                                info_msg = data['Information'].iloc[0]
                                print(f"❌ API Info for {symbol}: {info_msg}")
                                continue
                            elif 'Error Message' in data.columns:
                                error_msg = data['Error Message'].iloc[0]
                                print(f"❌ API Error for {symbol}: {error_msg}")
                                continue
                            elif 'Note' in data.columns:
                                note_msg = data['Note'].iloc[0]
                                print(f"💡 API Note for {symbol}: {note_msg}")
                                continue
                            
                            # Try to process the data
                            processed_data = self._process_alpha_vantage_data_fixed(data, symbol)
                            if not processed_data.empty:
                                store_in_snowflake = await self.store_processed_financial_data_simple(processed_data)
                                if store_in_snowflake:
                                    print('stored in snowflake')
                                else:
                                    print('snowflake storage failed')
                                all_data.append(processed_data)
                                print(f"✅ Processed data for {symbol}: {len(processed_data)} records")
                            else:
                                print(f"❌ No processed data for {symbol}")
                        else:
                            print(f"❌ Empty data for {symbol}")
                                
                    except Exception as e:
                        print(f"❌ Error loading {symbol}: {e}")
                        continue
                
                if all_data:
                    combined_data = pd.concat(all_data, ignore_index=True)
                    print(f"📊 Combined financial data: {len(combined_data)} total records")
                    
                    if not combined_data.empty:
                        print(f"📈 Sample processed data:")
                        print(combined_data[['timestamp', 'symbol', 'company_name', 'close', 'volume']].head())
                    
                    return combined_data
                else:
                    print("📝 Using sample financial data - API may be rate limited")
                    return self._get_sample_financial_data()
                        
            except Exception as e:
                logger.error(f"Error loading financial data: {e}")
                return self._get_sample_financial_data()

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
