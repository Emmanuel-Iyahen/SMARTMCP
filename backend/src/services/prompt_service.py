
import pandas as pd
import numpy as np
import re
import json
from typing import Dict, List, Any, Optional
from modules.ai_analyzer import AIAnalyzerModule
from modules.data_loader import DataLoaderModule
import logging

logger = logging.getLogger(__name__)

class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle non-serializable values"""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj) if np.isfinite(obj) else None
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif pd.isna(obj) or obj is None:
            return None
        elif isinstance(obj, (np.generic, pd.Series)):
            return obj.item() if hasattr(obj, 'item') else str(obj)
        return super().default(obj)

class PromptService:
    def __init__(self, ai_analyzer: AIAnalyzerModule, data_loader: DataLoaderModule):
        self.ai_analyzer = ai_analyzer
        self.data_loader = data_loader
        self.sector_keywords = {
            'energy': ['energy', 'power', 'electricity', 'gas', 'oil', 'renewable', 'grid'],
            'transportation': ['transport', 'tube', 'train', 'bus', 'delay', 'tfl', 'commute'],
            'finance': ['stock', 'market', 'ftse', 'investment', 'price', 'financial', 'trading'],
            'weather': ['weather', 'temperature', 'forecast', 'rain', 'met office', 'temperature'],
            'ecommerce': ['ecommerce', 'online', 'retail', 'sales', 'shopping'],
            'social_media': ['social media', 'twitter', 'facebook', 'engagement', 'trending']
        }
        self.json_encoder = JSONEncoder()
    
    async def analyze_prompt(self, prompt: str, sector: str = None) -> Dict[str, Any]:
        """Analyze user prompt and generate insights"""
        print('the sector is:', sector)
        try:
            # If sector not specified, detect it from prompt
            if not sector:
                sector = self._detect_sector_from_prompt(prompt)
            
            if not sector:
                return await self._handle_multi_sector_prompt(prompt)
            
            # Get sector-specific analysis
            result = await self._analyze_sector_prompt(prompt, sector)

            print('analysing for sector')
            
            # Ensure the result is JSON serializable
            return self._make_json_serializable(result)
            
        except Exception as e:
            logger.error(f"Error analyzing prompt: {e}")
            return self._make_json_serializable({
                'error': 'Unable to process prompt at this time',
                'suggestions': ['Try rephrasing your question', 'Specify a sector clearly']
            })
    

    async def _analyze_sector_prompt(self, prompt: str, sector: str) -> Dict[str, Any]:
        """Analyze prompt for a specific sector"""
        try:
            # Load relevant data
            sector_data = await self._load_sector_data(sector)
            
            
            # Use AI analyzer to generate insights
            analysis_result = await self.ai_analyzer.analyze_data(prompt, sector)
            
            # Enhance with additional context
            enhanced_insights = await self._enhance_insights(
                analysis_result.get('insights', ''), 
                sector_data, 
                prompt
            )
            
            result = {
                'sector': sector,
                'prompt': prompt,
                'insights': enhanced_insights,
                'data_summary': self._summarize_data(sector_data),
                'visualizations': await self._generate_visualizations(sector_data, prompt),
                'recommendations': analysis_result.get('recommendations', []),
                'related_questions': await self._suggest_related_questions(prompt, sector),
                'confidence_score': float(self._calculate_confidence(sector_data, prompt))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in sector analysis for {sector}: {e}")
            return await self._get_fallback_response(prompt, sector, str(e))
    
    def _make_json_serializable(self, data: Any) -> Any:
        """Recursively make data JSON serializable"""
        if isinstance(data, dict):
            return {k: self._make_json_serializable(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._make_json_serializable(item) for item in data]
        elif isinstance(data, (np.integer, np.floating)):
            return float(data) if np.isfinite(data) else None
        elif isinstance(data, pd.Timestamp):
            return data.isoformat()
        elif pd.isna(data) or data is None:
            return None
        elif hasattr(data, 'item'):  # numpy types
            return data.item() if np.isfinite(data.item()) else None
        elif isinstance(data, float) and not np.isfinite(data):
            return None
        else:
            return data
    
    async def _load_sector_data(self, sector: str) -> pd.DataFrame:
        """Load data for the specified sector"""
        try:
            if sector == 'energy':
                data = await self.data_loader.load_uk_energy_data()
            elif sector == 'transportation':
                data = await self.data_loader.load_transport_data()
            elif sector == 'finance':
                data = await self.data_loader.load_financial_data_from_snowflake()
            elif sector == 'weather':
                data = await self.data_loader.load_weather_data()

                print('weather data detected', data)
            else:
                data = pd.DataFrame()
            
            # Clean the data to remove non-finite values
            return self._clean_dataframe(data)
            
        except Exception as e:
            logger.error(f"Error loading data for sector {sector}: {e}")
            return pd.DataFrame()
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame by replacing non-finite values"""
        if df.empty:
            return df
        
        # Make a copy to avoid modifying the original
        df_clean = df.copy()
        
        # Replace non-finite values in numeric columns
        numeric_columns = df_clean.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            df_clean[col] = df_clean[col].apply(lambda x: x if np.isfinite(x) else None)
        
        return df_clean
    
    def _summarize_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary of the underlying data"""
        if data.empty:
            return {'record_count': 0, 'time_range': 'No data available'}
        
        summary = {
            'record_count': int(len(data)),
            'columns': list(data.columns)
        }
        
        if 'timestamp' in data.columns and not data.empty:
            try:
                # Ensure timestamps are serializable
                min_time = data['timestamp'].min()
                max_time = data['timestamp'].max()
                summary['time_range'] = {
                    'start': min_time.isoformat() if hasattr(min_time, 'isoformat') else str(min_time),
                    'end': max_time.isoformat() if hasattr(max_time, 'isoformat') else str(max_time)
                }
            except Exception as e:
                logger.warning(f"Error processing timestamp: {e}")
                summary['time_range'] = 'Error processing dates'
        
        # Add basic statistics for numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            try:
                # Convert statistics to serializable format
                stats = data[numeric_cols].describe()
                serializable_stats = {}
                for col in stats.columns:
                    col_stats = {}
                    for stat_name, value in stats[col].items():
                        if np.isfinite(value):
                            col_stats[stat_name] = float(value)
                        else:
                            col_stats[stat_name] = None
                    serializable_stats[col] = col_stats
                summary['statistics'] = serializable_stats
            except Exception as e:
                logger.warning(f"Error calculating statistics: {e}")
                summary['statistics'] = 'Error calculating statistics'
        
        return summary
    
    async def _enhance_insights(self, base_insights: str, data: pd.DataFrame, prompt: str) -> str:
        """Enhance AI-generated insights with data context"""
        if data.empty:
            return base_insights + "\n\nNote: Limited data available for comprehensive analysis."
        
        # Add data quality context
        data_context = f"\n\nAnalysis based on {len(data)} data points"
        if 'timestamp' in data.columns and not data.empty:
            try:
                date_range = f" from {data['timestamp'].min()} to {data['timestamp'].max()}"
                data_context += date_range
            except Exception as e:
                logger.warning(f"Error processing timestamp range: {e}")
        
        return base_insights + data_context
    
    async def _generate_visualizations(self, data: pd.DataFrame, prompt: str) -> List[Dict[str, Any]]:
        """Generate relevant visualizations based on prompt and data"""
        visualizations = []
        
        if not data.empty and 'timestamp' in data.columns:
            visualizations.append({
                'type': 'timeseries',
                'title': 'Trend Analysis',
                'description': 'Historical trends based on your query'
            })
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                visualizations.append({
                    'type': 'correlation',
                    'title': 'Relationship Analysis',
                    'description': 'Correlations between different metrics'
                })
        
        return visualizations
    
    async def _suggest_related_questions(self, prompt: str, sector: str) -> List[str]:
        """Suggest related questions based on the prompt"""
        base_questions = {
            'energy': [
                "How have energy prices changed over the past month?",
                "What are the peak energy usage times?",
                "How do current prices compare to historical averages?"
            ],
            'transportation': [
                "Which lines have the most frequent delays?",
                "What are the peak commute times with least delays?",
                "How does weather affect transport delays?"
            ],
            'finance': [
                "What's the FTSE 100 trend this week?",
                "Which stocks are performing best?",
                "How does economic news affect market performance?"
            ],
            'weather': [
                "How does weather impact energy consumption?",
                "What's the correlation between weather and transport delays?",
                "How does temperature affect retail sales?",
                "What's the weather forecast for the next few days?",
                "How does current weather compare to seasonal averages?"
            ]
        }
        
        sector_questions = base_questions.get(sector, [])
        
        prompt_lower = prompt.lower()
        if 'today' in prompt_lower:
            sector_questions.append(f"What are the current {sector} conditions?")
        if 'summary' in prompt_lower:
            sector_questions.append(f"What are the key {sector} metrics to monitor?")
        
        return sector_questions[:5]
    
    def _calculate_confidence(self, data: pd.DataFrame, prompt: str) -> float:
        """Calculate confidence score for the analysis"""
        if data.empty:
            return 0.3
        
        confidence = 0.7
        
        if len(data) > 100:
            confidence += 0.2
        if 'timestamp' in data.columns:
            confidence += 0.1
        
        complex_indicators = ['predict', 'forecast', 'correlation', 'impact', 'analyze']
        if any(indicator in prompt.lower() for indicator in complex_indicators):
            confidence -= 0.1
        
        return float(np.clip(confidence, 0.1, 1.0))
    
    async def _handle_multi_sector_prompt(self, prompt: str) -> Dict[str, Any]:
        """Handle prompts that span multiple sectors"""
        detected_sectors = self._detect_multiple_sectors(prompt)
        
        if not detected_sectors:
            return {
                'error': 'Unable to identify relevant sector(s)',
                'suggestions': [
                    'Please specify a sector (e.g., "energy", "transportation")',
                    'Try: "Show me energy prices and transport delays"'
                ]
            }
        
        sector_analyses = {}
        for sector in detected_sectors:
            try:
                sector_analyses[sector] = await self._analyze_sector_prompt(prompt, sector)
            except Exception as e:
                logger.error(f"Error analyzing sector {sector}: {e}")
                sector_analyses[sector] = await self._get_fallback_response(prompt, sector, str(e))
        
        cross_sector_insights = await self._generate_cross_sector_insights(prompt, sector_analyses)
        
        result = {
            'sectors': detected_sectors,
            'cross_sector_insights': cross_sector_insights,
            'sector_analyses': sector_analyses,
            'integrated_recommendations': await self._integrate_recommendations(sector_analyses)
        }
        
        return self._make_json_serializable(result)
    
    def _detect_sector_from_prompt(self, prompt: str) -> Optional[str]:
        """Detect the most relevant sector from prompt text"""
        prompt_lower = prompt.lower()

        # Check for specific night tube keywords first (highest priority)
        night_tube_keywords = ['night tube', 'night service', 'night transport', 'overnight tube']
        if any(keyword in prompt_lower for keyword in night_tube_keywords):
            return 'transportation'

        # Check for general transport-related keywords
        transport_keywords = [

            'tube', 'train', 'bus', 'delay', 'tfl', 'transport', 'underground',
            'line', 'station', 'commute', 'journey', 'service', 'disruption',
            'central line', 'victoria line', 'northern line', 'piccadilly line'
        ]
        
        if any(keyword in prompt_lower for keyword in transport_keywords):
            print('key word for transport found')
            return 'transportation'

        # Check for weather-related keywords
        weather_keywords = ['weather', 'temperature', 'forecast', 'rain', 'snow', 'wind']
        if any(keyword in prompt_lower for keyword in weather_keywords):
            return 'weather'
        
        sector_scores = {}
        for sector, keywords in self.sector_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            if score > 0:
                sector_scores[sector] = score
        
        return max(sector_scores.items(), key=lambda x: x[1])[0] if sector_scores else None
    
    def _detect_multiple_sectors(self, prompt: str) -> List[str]:
        """Detect multiple sectors mentioned in prompt"""
        prompt_lower = prompt.lower()
        detected_sectors = []
        
        for sector, keywords in self.sector_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_sectors.append(sector)
        
        return detected_sectors
    
    async def _generate_cross_sector_insights(self, prompt: str, sector_analyses: Dict) -> str:
        """Generate insights that span multiple sectors"""
        sectors_list = list(sector_analyses.keys())
        return f"Cross-sector analysis covering {', '.join(sectors_list)}."
    
    async def _integrate_recommendations(self, sector_analyses: Dict) -> List[str]:
        """Integrate recommendations from multiple sector analyses"""
        all_recommendations = []
        
        for sector, analysis in sector_analyses.items():
            recommendations = analysis.get('recommendations', [])
            sector_recs = [f"{sector.title()}: {rec}" for rec in recommendations]
            all_recommendations.extend(sector_recs)
        
        return all_recommendations[:10]
    
    async def _get_fallback_response(self, prompt: str, sector: str, error: str) -> Dict[str, Any]:
        """Get fallback response when analysis fails"""
        return {
            'sector': sector,
            'prompt': prompt,
            'insights': f"Analysis for {sector} sector based on your query: '{prompt}'. Note: Limited analysis due to: {error}",
            'data_summary': {'record_count': 0, 'status': 'Data loading issue'},
            'visualizations': [],
            'recommendations': [
                "Check if data sources are available",
                "Try a simpler query",
                "Contact support if the issue persists"
            ],
            'related_questions': [
                f"What are the current trends in {sector}?",
                f"How can I get better insights for {sector}?",
                f"What data sources are available for {sector}?"
            ],
            'confidence_score': 0.3
        }