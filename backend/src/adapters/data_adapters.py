# import pandas as pd
# import aiohttp
# import json
# import csv
# import io
# import asyncio
# import logging
# from abc import ABC, abstractmethod
# from typing import Dict, Any, List
# from datetime import datetime

# logger = logging.getLogger(__name__)

# class BaseDataAdapter(ABC):
#     """Base class for all data adapters"""
    
#     @abstractmethod
#     async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
#         pass
    
#     def _log_error(self, operation: str, error: Exception):
#         """Log errors consistently"""
#         logger.error(f"Error in {self.__class__.__name__}.{operation}: {error}")

# class CSVAdapter(BaseDataAdapter):
#     """Adapter for loading CSV data from files or URLs"""
    
#     async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
#         try:
#             file_path = config.get('file_path')
#             url = config.get('url')
            
#             if file_path:
#                 # Load from local file
#                 return pd.read_csv(file_path, **config.get('read_csv_args', {}))
#             elif url:
#                 # Load from URL
#                 async with aiohttp.ClientSession() as session:
#                     async with session.get(url) as response:
#                         content = await response.text()
#                         return pd.read_csv(io.StringIO(content), **config.get('read_csv_args', {}))
#             else:
#                 raise ValueError("Either 'file_path' or 'url' must be provided in config")
                
#         except Exception as e:
#             self._log_error("load_data", e)
#             return pd.DataFrame()

# class JSONAdapter(BaseDataAdapter):
#     """Adapter for loading JSON data from files or URLs"""
    
#     async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
#         try:
#             file_path = config.get('file_path')
#             url = config.get('url')
#             data_key = config.get('data_key')  # Key to extract data from JSON
            
#             if file_path:
#                 with open(file_path, 'r') as f:
#                     data = json.load(f)
#             elif url:
#                 async with aiohttp.ClientSession() as session:
#                     async with session.get(url) as response:
#                         data = await response.json()
#             else:
#                 raise ValueError("Either 'file_path' or 'url' must be provided in config")
            
#             # Extract data from specific key if provided
#             if data_key and isinstance(data, dict):
#                 data = data.get(data_key, data)
            
#             return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
            
#         except Exception as e:
#             self._log_error("load_data", e)
#             return pd.DataFrame()

# class APIAdapter(BaseDataAdapter):
#     """Adapter for loading data from REST APIs"""
    
#     async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
#         try:
#             url = config['url']
#             method = config.get('method', 'GET').upper()
#             headers = config.get('headers', {})
#             params = config.get('params', {})
#             data = config.get('data')
#             timeout = config.get('timeout', 30)
            
#             async with aiohttp.ClientSession() as session:
#                 if method == 'GET':
#                     async with session.get(url, params=params, headers=headers, timeout=timeout) as response:
#                         return await self._handle_response(response, config)
#                 elif method == 'POST':
#                     async with session.post(url, json=data, params=params, headers=headers, timeout=timeout) as response:
#                         return await self._handle_response(response, config)
#                 else:
#                     raise ValueError(f"Unsupported HTTP method: {method}")
                    
#         except Exception as e:
#             self._log_error("load_data", e)
#             return pd.DataFrame()
    
#     async def _handle_response(self, response, config: Dict[str, Any]) -> pd.DataFrame:
#         """Handle API response and convert to DataFrame"""
#         if response.status == 200:
#             content_type = response.headers.get('Content-Type', '')
            
#             if 'application/json' in content_type:
#                 data = await response.json()
#                 data_key = config.get('data_key')
                
#                 # Extract data from specific key if provided
#                 if data_key and isinstance(data, dict):
#                     data = data.get(data_key, data)
                
#                 # Handle different data structures
#                 if isinstance(data, list):
#                     return pd.DataFrame(data)
#                 elif isinstance(data, dict):
#                     # If it's a dictionary with nested data
#                     if any(isinstance(v, list) for v in data.values()):
#                         # Find the first list value
#                         for key, value in data.items():
#                             if isinstance(value, list):
#                                 return pd.DataFrame(value)
#                     return pd.DataFrame([data])
#                 else:
#                     return pd.DataFrame([{'data': data}])
                    
#             elif 'text/csv' in content_type:
#                 content = await response.text()
#                 return pd.read_csv(io.StringIO(content))
#             else:
#                 # Try to parse as JSON anyway
#                 try:
#                     data = await response.json()
#                     return pd.DataFrame([data])
#                 except:
#                     content = await response.text()
#                     return pd.DataFrame([{'raw_content': content}])
#         else:
#             raise Exception(f"API request failed with status {response.status}")

# class DatabaseAdapter(BaseDataAdapter):
#     """Adapter for loading data from databases (placeholder implementation)"""
    
#     async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
#         try:
#             # This would be implemented for specific databases
#             # For now, return empty DataFrame
#             logger.warning("DatabaseAdapter not fully implemented")
#             return pd.DataFrame()
            
#         except Exception as e:
#             self._log_error("load_data", e)
#             return pd.DataFrame()

# class WebScraperAdapter(BaseDataAdapter):
#     """Adapter for web scraping (placeholder implementation)"""
    
#     async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
#         try:
#             # This would use libraries like BeautifulSoup or Scrapy
#             # For now, return empty DataFrame
#             logger.warning("WebScraperAdapter not fully implemented")
#             return pd.DataFrame()
            
#         except Exception as e:
#             self._log_error("load_data", e)
#             return pd.DataFrame()

# class RealTimeAdapter(BaseDataAdapter):
#     """Adapter for real-time data streams (placeholder implementation)"""
    
#     async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
#         try:
#             # This would handle WebSocket connections or streaming APIs
#             # For now, return empty DataFrame
#             logger.warning("RealTimeAdapter not fully implemented")
#             return pd.DataFrame()
            
#         except Exception as e:
#             self._log_error("load_data", e)
#             return pd.DataFrame()





import pandas as pd
import aiohttp
import json
import csv
import io
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseDataAdapter(ABC):
    """Base class for all data adapters"""
    
    @abstractmethod
    async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        pass
    
    def _log_error(self, operation: str, error: Exception):
        """Log errors consistently"""
        logger.error(f"Error in {self.__class__.__name__}.{operation}: {error}")

class CSVAdapter(BaseDataAdapter):
    """Adapter for loading CSV data from files or URLs"""
    
    async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            file_path = config.get('file_path')
            url = config.get('url')
            
            if file_path:
                # Load from local file
                return pd.read_csv(file_path, **config.get('read_csv_args', {}))
            elif url:
                # Load from URL
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        content = await response.text()
                        return pd.read_csv(io.StringIO(content), **config.get('read_csv_args', {}))
            else:
                raise ValueError("Either 'file_path' or 'url' must be provided in config")
                
        except Exception as e:
            self._log_error("load_data", e)
            return pd.DataFrame()

class JSONAdapter(BaseDataAdapter):
    """Adapter for loading JSON data from files or URLs"""
    
    async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            file_path = config.get('file_path')
            url = config.get('url')
            data_key = config.get('data_key')  # Key to extract data from JSON
            
            if file_path:
                with open(file_path, 'r') as f:
                    data = json.load(f)
            elif url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        data = await response.json()
            else:
                raise ValueError("Either 'file_path' or 'url' must be provided in config")
            
            # Extract data from specific key if provided
            if data_key and isinstance(data, dict):
                data = data.get(data_key, data)
            
            return pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
            
        except Exception as e:
            self._log_error("load_data", e)
            return pd.DataFrame()

class APIAdapter(BaseDataAdapter):
    """Adapter for loading data from REST APIs"""
    
    async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            url = config['url']
            method = config.get('method', 'GET').upper()
            headers = config.get('headers', {})
            params = config.get('params', {})
            data = config.get('data')
            timeout = config.get('timeout', 30)
            
            # Convert boolean parameters to strings for API compatibility
            params = self._sanitize_params(params)
            
            async with aiohttp.ClientSession() as session:
                if method == 'GET':
                    async with session.get(url, params=params, headers=headers, timeout=timeout) as response:
                        return await self._handle_response(response, config)
                elif method == 'POST':
                    async with session.post(url, json=data, params=params, headers=headers, timeout=timeout) as response:
                        return await self._handle_response(response, config)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
        except Exception as e:
            self._log_error("load_data", e)
            return pd.DataFrame()
    
    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, str]:
        """Convert parameter values to strings to avoid type issues"""
        sanitized = {}
        for key, value in params.items():
            if isinstance(value, bool):
                sanitized[key] = str(value).lower()
            elif isinstance(value, (int, float)):
                sanitized[key] = str(value)
            elif value is None:
                continue  # Skip None values
            else:
                sanitized[key] = value
        return sanitized
    
    async def _handle_response(self, response, config: Dict[str, Any]) -> pd.DataFrame:
        """Handle API response and convert to DataFrame"""
        if response.status == 200:
            content_type = response.headers.get('Content-Type', '')
            
            if 'application/json' in content_type:
                data = await response.json()
                data_key = config.get('data_key')
                
                # Extract data from specific key if provided
                if data_key and isinstance(data, dict):
                    data = data.get(data_key, data)
                
                # Handle different data structures
                if isinstance(data, list):
                    return pd.DataFrame(data)
                elif isinstance(data, dict):
                    # If it's a dictionary with nested data
                    if any(isinstance(v, list) for v in data.values()):
                        # Find the first list value
                        for key, value in data.items():
                            if isinstance(value, list):
                                return pd.DataFrame(value)
                    return pd.DataFrame([data])
                else:
                    return pd.DataFrame([{'data': data}])
                    
            elif 'text/csv' in content_type:
                content = await response.text()
                return pd.read_csv(io.StringIO(content))
            else:
                # Try to parse as JSON anyway
                try:
                    data = await response.json()
                    return pd.DataFrame([data])
                except:
                    content = await response.text()
                    return pd.DataFrame([{'raw_content': content}])
        else:
            raise Exception(f"API request failed with status {response.status}")

class DatabaseAdapter(BaseDataAdapter):
    """Adapter for loading data from databases (placeholder implementation)"""
    
    async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            # This would be implemented for specific databases
            # For now, return empty DataFrame
            logger.warning("DatabaseAdapter not fully implemented")
            return pd.DataFrame()
            
        except Exception as e:
            self._log_error("load_data", e)
            return pd.DataFrame()

class WebScraperAdapter(BaseDataAdapter):
    """Adapter for web scraping (placeholder implementation)"""
    
    async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            # This would use libraries like BeautifulSoup or Scrapy
            # For now, return empty DataFrame
            logger.warning("WebScraperAdapter not fully implemented")
            return pd.DataFrame()
            
        except Exception as e:
            self._log_error("load_data", e)
            return pd.DataFrame()

class RealTimeAdapter(BaseDataAdapter):
    """Adapter for real-time data streams (placeholder implementation)"""
    
    async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
        try:
            # This would handle WebSocket connections or streaming APIs
            # For now, return empty DataFrame
            logger.warning("RealTimeAdapter not fully implemented")
            return pd.DataFrame()
            
        except Exception as e:
            self._log_error("load_data", e)
            return pd.DataFrame()







# class APIAdapter(BaseDataAdapter):
#     """Adapter for loading data from REST APIs"""
    
#     async def load_data(self, config: Dict[str, Any]) -> pd.DataFrame:
#         try:
#             url = config['url']
#             method = config.get('method', 'GET').upper()
#             headers = config.get('headers', {})
#             params = config.get('params', {})
#             data = config.get('data')
#             timeout = config.get('timeout', 30)
            
#             # Convert boolean parameters to strings for API compatibility
#             params = self._sanitize_params(params)
            
#             async with aiohttp.ClientSession() as session:
#                 if method == 'GET':
#                     async with session.get(url, params=params, headers=headers, timeout=timeout) as response:
#                         return await self._handle_response(response, config)
#                 elif method == 'POST':
#                     async with session.post(url, json=data, params=params, headers=headers, timeout=timeout) as response:
#                         return await self._handle_response(response, config)
#                 else:
#                     raise ValueError(f"Unsupported HTTP method: {method}")
                    
#         except Exception as e:
#             self._log_error("load_data", e)
#             return pd.DataFrame()
    
#     def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, str]:
#         """Convert parameter values to strings to avoid type issues"""
#         sanitized = {}
#         for key, value in params.items():
#             if isinstance(value, bool):
#                 sanitized[key] = str(value).lower()
#             elif isinstance(value, (int, float)):
#                 sanitized[key] = str(value)
#             elif value is None:
#                 continue  # Skip None values
#             else:
#                 sanitized[key] = value
#         return sanitized
    
#     async def _handle_response(self, response, config: Dict[str, Any]) -> pd.DataFrame:
#         """Handle API response and convert to DataFrame"""
#         if response.status == 200:
#             content_type = response.headers.get('Content-Type', '')
            
#             if 'application/json' in content_type:
#                 data = await response.json()
#                 data_key = config.get('data_key')
                
#                 # Extract data from specific key if provided
#                 if data_key and isinstance(data, dict):
#                     data = data.get(data_key, data)
                
#                 # Handle different data structures
#                 if isinstance(data, list):
#                     return pd.DataFrame(data)
#                 elif isinstance(data, dict):
#                     # If it's a dictionary with nested data
#                     if any(isinstance(v, list) for v in data.values()):
#                         # Find the first list value
#                         for key, value in data.items():
#                             if isinstance(value, list):
#                                 return pd.DataFrame(value)
#                     return pd.DataFrame([data])
#                 else:
#                     return pd.DataFrame([{'data': data}])
                    
#             elif 'text/csv' in content_type:
#                 content = await response.text()
#                 return pd.read_csv(io.StringIO(content))
#             else:
#                 # Try to parse as JSON anyway
#                 try:
#                     data = await response.json()
#                     return pd.DataFrame([data])
#                 except:
#                     content = await response.text()
#                     return pd.DataFrame([{'raw_content': content}])
#         else:
#             raise Exception(f"API request failed with status {response.status}")