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



# In your financial_loader.py - keep all original method names but fix the logic

class FinancialDataLoader:
        
    def __init__(self):
        self.adapters = {
            'csv': CSVAdapter(),
            'json': JSONAdapter(),
            'api': APIAdapter(),  # This now works correctly
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
        """Load UK financial market data with proper error handling - FIXED"""
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
                    
                    # This now works because the APIAdapter is fixed
                    data = await self.load_data('api', config)
                    
                    print(f"🔍 Data for {symbol}:")
                    print(f"   Shape: {data.shape}")
                    if not data.empty:
                        print(f"   Columns: {list(data.columns)}")
                        print(f"   Latest date: {data['timestamp'].iloc[0] if 'timestamp' in data.columns else 'N/A'}")
                    
                    if not data.empty:
                        # Process the data (now it's a proper DataFrame from the fixed adapter)
                        processed_data = self._process_alpha_vantage_data_fixed(data, symbol)
                        if not processed_data.empty:
                            # Store in Snowflake
                            store_in_snowflake = await self.store_processed_financial_data_simple(processed_data)
                            if store_in_snowflake:
                                print(f'✅ Stored {symbol} in snowflake - {len(processed_data)} records')
                            else:
                                print(f'❌ Snowflake storage failed for {symbol}')
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
                    latest_date = combined_data['timestamp'].max().strftime('%Y-%m-%d')
                    print(f"📈 Latest data date: {latest_date}")
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
        """Process Alpha Vantage data - FIXED VERSION"""
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
            
            # Check if we have the expected data
            if data.empty:
                return pd.DataFrame()
            
            # The fixed APIAdapter should return data with these columns:
            expected_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            if not all(col in data.columns for col in expected_columns):
                print(f"⚠️ Unexpected columns for {symbol}: {list(data.columns)}")
                return pd.DataFrame()
            
            # Create a copy to avoid modifying the original
            processed_data = data.copy()
            
            # Add symbol and company name
            processed_data['symbol'] = symbol
            processed_data['company_name'] = company_names.get(symbol, symbol)
            
            # Ensure timestamp is datetime
            processed_data['timestamp'] = pd.to_datetime(processed_data['timestamp'])
            
            # Sort by timestamp descending and take only the 2 most recent days
            processed_data = processed_data.sort_values('timestamp', ascending=False)
            processed_data = processed_data.head(2).reset_index(drop=True)
            
            # Reorder columns for consistency
            column_order = ['timestamp', 'symbol', 'company_name', 'open', 'high', 'low', 'close', 'volume']
            processed_data = processed_data[column_order]
            
            return processed_data
            
        except Exception as e:
            print(f"Error processing Alpha Vantage data for {symbol}: {e}")
            return pd.DataFrame()

    async def store_processed_financial_data_simple(self, processed_data: pd.DataFrame) -> bool:
        """Simplified approach using write_pandas - KEEP ORIGINAL"""
        try:
            if self.snowflake_conn is None:
                print("⚠️ Snowflake not connected, skipping processed data storage")
                return False
            
            # Use Snowflake's built-in method
            from snowflake.connector.pandas_tools import write_pandas
            
            # Create a copy to avoid modifying the original DataFrame
            df_to_store = processed_data.copy()
            
            # Convert all column names to uppercase
            df_to_store.columns = [col.upper() for col in df_to_store.columns]

            if 'TIMESTAMP' in df_to_store.columns:
                df_to_store['TIMESTAMP'] = pd.to_datetime(df_to_store['TIMESTAMP'], errors='coerce')
                df_to_store['TIMESTAMP'] = df_to_store['TIMESTAMP'].dt.strftime('%Y-%m-%d %H:%M:%S')

            print(f'📊 Data types going to snowflake: {df_to_store.dtypes}')
            print(f'📊 Data to store shape: {df_to_store.shape}')
            
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

    def _get_sample_financial_data(self) -> pd.DataFrame:
        """Get sample financial data - KEEP YOUR ORIGINAL IMPLEMENTATION"""
        # Your existing sample data implementation
        sample_data = {
            'timestamp': [pd.Timestamp.now().normalize() - pd.Timedelta(days=i) for i in range(3)],
            'symbol': ['HSBA.L', 'BP.L', 'GSK.L'],
            'company_name': ['HSBC Holdings', 'BP', 'GSK'],
            'open': [650.0, 500.0, 1400.0],
            'high': [660.0, 510.0, 1420.0],
            'low': [640.0, 490.0, 1380.0],
            'close': [655.0, 505.0, 1410.0],
            'volume': [1000000, 2000000, 1500000]
        }
        return pd.DataFrame(sample_data)