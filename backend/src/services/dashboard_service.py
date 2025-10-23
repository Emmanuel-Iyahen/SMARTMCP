import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from modules.data_loader import DataLoaderModule
from modules.ai_analyzer import AIAnalyzerModule
from modules.visualization import VisualizationModule
import logging
import asyncio

logger = logging.getLogger(__name__)

class DashboardService:
    def __init__(self, data_loader: DataLoaderModule, ai_analyzer: AIAnalyzerModule, visualization: VisualizationModule):
        self.data_loader = data_loader
        self.ai_analyzer = ai_analyzer
        self.visualization = visualization
        self.cache = {}  # Simple in-memory cache, replace with Redis in production
    
    async def get_overview(self) -> Dict[str, Any]:
        """Get comprehensive dashboard overview for all sectors"""
        try:
            # Load data from all sectors concurrently
            transport_data, weather_data, financial_data = await asyncio.gather(
                #self._get_energy_overview(),
                self._get_transport_overview(),
                self._get_weather_overview(),
                self._get_financial_overview(),  
            )
            
            return {
                #'energy': energy_data,
                'transportation': transport_data,
                'finance': financial_data,
                'weather': weather_data,
                'last_updated': datetime.utcnow().isoformat(),
                'summary': await self._generate_overall_summary({
                    #'energy': energy_data,
                    'transportation': transport_data,
                    'finance': financial_data  # Add this line
                })
            }
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {e}")
            raise



    async def _get_transport_overview(self) -> Dict[str, Any]:
            
        """Get transportation sector overview - FIXED VERSION"""
        try:
            transport_data = await self.data_loader.load_transport_data()
            
            # Ensure transport_data is a list of dictionaries
            if isinstance(transport_data, pd.DataFrame):
                if not transport_data.empty:
                    transport_data = transport_data.to_dict('records')
                else:
                    transport_data = []
            elif not isinstance(transport_data, list):
                transport_data = []
            
            # Calculate metrics properly - only count actual delays
            total_lines = len(transport_data)
            
            # Count only services that are NOT "Good Service"
            actual_delays = [
                item for item in transport_data 
                if isinstance(item, dict) and 
                item.get('status', 'Unknown') != 'Good Service' and
                'good service' not in item.get('status', '').lower()
            ]
            total_delays = len(actual_delays)
            
            delay_percentage = (total_delays / total_lines) * 100 if total_lines > 0 else 0

            # Prepare TWO different data structures:
            # 1. Chart data for the time-series delay chart
            chart_data = self._prepare_transport_chart_data(transport_data)
            
            # 2. All services data for displaying individual service statuses
            all_services_data = self._prepare_all_services_data(transport_data)
            
            # Identify major issues
            major_issues = await self._identify_major_transport_issues(transport_data)
            
            # Calculate trend based on actual delays
            if delay_percentage > 30:
                trend = 'poor'
            elif delay_percentage > 10:
                trend = 'stable'
            else:
                trend = 'excellent'
            
            return {
                'total_lines': total_lines,
                'delayed_lines': total_delays,
                'delay_percentage': round(delay_percentage, 1),
                'trend': trend,
                'chart_data': chart_data,  # For the delay trend chart
                'all_services_data': all_services_data,  # For service listings
                'major_issues': major_issues,
                'service_breakdown': self._get_service_breakdown(transport_data)
            }
        except Exception as e:
            logger.error(f"Error in transport overview: {e}")
            return {
                'total_lines': 0,
                'delayed_lines': 0,
                'delay_percentage': 0,
                'trend': 'stable',
                'chart_data': [],
                'all_services_data': [],
                'major_issues': [],
                'service_breakdown': {}
            }

    def _get_service_breakdown(self, transport_data: List[Dict]) -> Dict[str, int]:
        """Get breakdown of service statuses"""
        breakdown = {}
        for service in transport_data:
            if isinstance(service, dict):
                status = service.get('status', 'Unknown')
                breakdown[status] = breakdown.get(status, 0) + 1
        return breakdown
        


    # def _prepare_transport_chart_data(self, transport_data: List[Dict]) -> List[Dict]:

    #     """Prepare transport data for charting"""
    #     if not transport_data or not isinstance(transport_data, list):
    #         return []
    #     try:
    #         chart_data = []
    #         for service in transport_data:
    #             if isinstance(service, dict):
    #                 # Extract timestamp safely
    #                 timestamp = service.get('timestamp')
    #                 if isinstance(timestamp, datetime):
    #                     timestamp_str = timestamp.isoformat()
    #                 else:
    #                     timestamp_str = str(timestamp) if timestamp else datetime.utcnow().isoformat()
                    
    #                 # Extract delay minutes safely
    #                 delay_minutes = service.get('delay_minutes', 0)
    #                 if not isinstance(delay_minutes, (int, float)):
    #                     delay_minutes = 0
                    
    #                 chart_data.append({
    #                     'timestamp': timestamp_str,
    #                     'line_name': service.get('line_name', 'Unknown'),
    #                     'delay_minutes': delay_minutes,
    #                     'status': service.get('status', 'Unknown'),
    #                     'mode': service.get('mode', 'Unknown')
    #                 })
            
    #         return chart_data
    #     except Exception as e:
    #         logger.error(f"Error preparing transport chart data: {e}")
    #         return []




    def _prepare_transport_chart_data(self, transport_data: List[Dict]) -> List[Dict]:
            
        """Prepare transport data for charting - FIXED VERSION"""
        if not transport_data or not isinstance(transport_data, list):
            return []
        
        try:
            # Calculate overall delay metrics over time (simulated since we have real-time data)
            # For real-time data, we'll create a summary of current delays
            current_time = datetime.utcnow()
            
            # Calculate current delay statistics
            total_delay = 0
            delayed_count = 0
            max_delay = 0
            
            for service in transport_data:
                if isinstance(service, dict):
                    delay_minutes = service.get('delay_minutes', 0)
                    if not isinstance(delay_minutes, (int, float)):
                        try:
                            delay_minutes = float(delay_minutes)
                        except (ValueError, TypeError):
                            delay_minutes = 0
                    
                    # Only count actual delays (not "Good Service" with default 30 min)
                    status = service.get('status', 'Unknown')
                    is_actually_delayed = (
                        status != 'Good Service' and 
                        'good service' not in status.lower()
                    )
                    
                    if is_actually_delayed and delay_minutes > 0:
                        total_delay += delay_minutes
                        delayed_count += 1
                        max_delay = max(max_delay, delay_minutes)
            
            avg_delay = total_delay / delayed_count if delayed_count > 0 else 0
            
            # Create time-series data for the chart (last 6 hours simulated)
            chart_data = []
            for i in range(6):
                # Simulate some variation in delays over time
                time_point = current_time - timedelta(hours=(5 - i))
                
                # Add some realistic variation to the average delay
                variation = np.random.uniform(-5, 5)  # Small random variation
                delay_value = max(0, avg_delay + variation)
                
                chart_data.append({
                    'timestamp': time_point.isoformat(),
                    'value': round(delay_value, 1),  # Average delay in minutes
                    'delayed_services': delayed_count,  # Number of delayed services
                    'max_delay': round(max_delay, 1)  # Maximum delay
                })
            
            # Add current data point
            chart_data.append({
                'timestamp': current_time.isoformat(),
                'value': round(avg_delay, 1),
                'delayed_services': delayed_count,
                'max_delay': round(max_delay, 1)
            })
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error preparing transport chart data: {e}")
            # Fallback: return simple chart data
            return [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'value': 0,
                    'delayed_services': 0,
                    'max_delay': 0
                }
            ]


    def _prepare_all_services_data(self, transport_data: List[Dict]) -> List[Dict]:
            
        """Prepare individual service data for frontend display"""
        if not transport_data or not isinstance(transport_data, list):
            return []
        
        try:
            all_services = []
            for service in transport_data:
                if isinstance(service, dict):
                    # Extract timestamp safely
                    timestamp = service.get('timestamp')
                    if isinstance(timestamp, datetime):
                        timestamp_str = timestamp.isoformat()
                    else:
                        timestamp_str = str(timestamp) if timestamp else datetime.utcnow().isoformat()
                    
                    # Extract delay minutes safely
                    delay_minutes = service.get('delay_minutes', 0)
                    if not isinstance(delay_minutes, (int, float)):
                        delay_minutes = 0
                    
                    all_services.append({
                        'timestamp': timestamp_str,
                        'line_name': service.get('line_name', 'Unknown'),
                        'delay_minutes': delay_minutes,
                        'status': service.get('status', 'Unknown'),
                        'mode': service.get('mode', 'Unknown'),
                        'reason': service.get('reason', '')
                    })
            
            return all_services
        except Exception as e:
            logger.error(f"Error preparing all services data: {e}")
            return []





    async def _get_weather_overview(self) -> Dict[str, Any]:

        """Get weather overview with enhanced data"""
        try:
            weather_data = await self.data_loader.load_weather_data()
            #print('weather data from overview: ', weather_data)
            
            # Enhanced weather data processing
            if isinstance(weather_data, pd.DataFrame) and not weather_data.empty:
                # Extract current weather information
                current_temp = weather_data['temperature'].iloc[-1] if 'temperature' in weather_data.columns else 15.5
                humidity = weather_data['humidity'].iloc[-1] if 'humidity' in weather_data.columns else 50
                precipitation = weather_data['precipitation'].iloc[-1] if 'precipitation' in weather_data.columns else 0.0
                weather_code = weather_data['weather_code'].iloc[-1] if 'weather_code' in weather_data.columns else 3
                
                # Convert weather code to human-readable condition
                condition = self._get_weather_condition(weather_code)
                
                # Determine trend based on temperature changes
                trend = self._get_weather_trend(weather_data)
                
                # Generate chart data for temperature trends
                chart_data = self._prepare_weather_chart_data(weather_data)
                
                # Generate alerts based on weather conditions
                alerts = self._generate_weather_alerts(current_temp, precipitation, weather_code)
                
                return {
                    'current_temp': round(float(current_temp), 1),
                    'humidity': int(humidity),
                    'precipitation': round(float(precipitation), 1),
                    'condition': condition,
                    'trend': trend,
                    'forecast': self._get_weather_forecast(weather_code, current_temp),
                    'alerts': alerts,
                    'chart_data': chart_data
                }
            else:
                # Fallback to sample data
                return self._get_sample_weather_overview()
                
        except Exception as e:
            logger.error(f"Error in weather overview: {e}")
            return self._get_sample_weather_overview()

    def _get_weather_condition(self, weather_code: int) -> str:
        """Convert WMO weather code to human-readable condition"""
        weather_conditions = {
            0: 'Clear sky',
            1: 'Mainly clear', 
            2: 'Partly cloudy',
            3: 'Overcast',
            45: 'Fog',
            48: 'Depositing rime fog',
            51: 'Light drizzle',
            53: 'Moderate drizzle',
            55: 'Dense drizzle',
            61: 'Slight rain',
            63: 'Moderate rain',
            65: 'Heavy rain',
            80: 'Slight rain showers',
            81: 'Moderate rain showers',
            82: 'Violent rain showers'
        }
        return weather_conditions.get(weather_code, 'Unknown')

    def _get_weather_trend(self, weather_data: pd.DataFrame) -> str:
        """Determine weather trend based on temperature changes"""
        if len(weather_data) < 2:
            return 'stable'
        
        try:
            recent_temps = weather_data['temperature'].tail(3)
            if len(recent_temps) >= 2:
                temp_change = recent_temps.iloc[-1] - recent_temps.iloc[0]
                if temp_change > 2:
                    return 'warming'
                elif temp_change < -2:
                    return 'cooling'
            return 'stable'
        except:
            return 'stable'

    def _prepare_weather_chart_data(self, weather_data: pd.DataFrame) -> List[Dict]:
        """Prepare weather data for charting"""
        try:
            chart_data = []
            # Use last 6 data points for the chart
            recent_data = weather_data.tail(6)
            
            for _, row in recent_data.iterrows():
                chart_data.append({
                    'timestamp': row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                    'temperature': float(row['temperature']) if 'temperature' in row else 0,
                    'humidity': float(row['humidity']) if 'humidity' in row else 0,
                    'precipitation': float(row['precipitation']) if 'precipitation' in row else 0
                })
            
            return chart_data
        except Exception as e:
            logger.error(f"Error preparing weather chart data: {e}")
            return []

    def _generate_weather_alerts(self, temperature: float, precipitation: float, weather_code: int) -> List[Dict]:
        """Generate weather alerts based on current conditions"""
        alerts = []
        
        if temperature > 30:
            alerts.append({
                'type': 'heat_warning',
                'message': 'High temperature warning',
                'severity': 'warning'
            })
        elif temperature < 5:
            alerts.append({
                'type': 'cold_warning', 
                'message': 'Low temperature warning',
                'severity': 'warning'
            })
        
        if precipitation > 5.0:
            alerts.append({
                'type': 'heavy_rain',
                'message': 'Heavy precipitation expected',
                'severity': 'warning'
            })
        
        if weather_code in [45, 48]:  # Fog conditions
            alerts.append({
                'type': 'fog_alert',
                'message': 'Reduced visibility due to fog',
                'severity': 'info'
            })
        
        return alerts

    def _get_weather_forecast(self, weather_code: int, current_temp: float) -> str:
        """Generate simple weather forecast"""
        if weather_code in [0, 1]:  # Clear conditions
            return 'Clear conditions expected to continue'
        elif weather_code in [2, 3]:  # Cloudy conditions
            return 'Cloudy with stable conditions'
        elif weather_code >= 51:  # Precipitation
            return 'Precipitation likely to continue'
        else:
            return 'Stable weather conditions'

    def _get_sample_weather_overview(self) -> Dict[str, Any]:
        """Fallback sample weather data"""
        return {
            'current_temp': 15.5,
            'humidity': 65,
            'precipitation': 0.0,
            'condition': 'Partly Cloudy',
            'trend': 'stable',
            'forecast': 'Stable conditions expected',
            'alerts': [],
            'chart_data': [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'temperature': 15.5,
                    'humidity': 65,
                    'precipitation': 0.0
                }
            ]
    }
    
    
    async def _get_transport_detailed(self, timeframe: str) -> Dict[str, Any]:
        """Get detailed transport analysis"""
        transport_data = await self.data_loader.load_transport_data()
        
        return {
            'timeseries': transport_data,
            'metrics': {
                'total_services': len(transport_data),
                'on_time_services': len([x for x in transport_data if x.get('status') == 'Good Service']),
                'average_delay': np.mean([x.get('delay_minutes', 0) for x in transport_data]),
                'reliability_score': self._calculate_reliability_score(transport_data)
            },
            'trends': await self._analyze_transport_trends(transport_data)
        }
    


    async def _generate_overall_summary(self, sector_data: Dict[str, Any]) -> Dict[str, Any]:

        """Generate overall business summary"""
        try:
            # Ensure we have the required data
            transport_data = sector_data.get('transportation', {})
            #weather_data = sector_data.get('weather', {})
            
            logger.info(f"Transport data keys: {list(transport_data.keys())}")
            #logger.info(f"Weather data keys: {list(weather_data.keys())}")
            
            # Generate comprehensive summary
            return {
                #'market_outlook': await self._assess_market_outlook(sector_data),
                'key_opportunities': await self._identify_opportunities(sector_data),
                'risk_factors': await self._assess_risks(sector_data),
                'recommended_actions': await self._generate_actionable_insights(sector_data),
                'summary_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating overall summary: {e}")
            # Provide fallback summary
            return {
                'market_outlook': 'Analysis in progress - transport data loaded successfully',
                'key_opportunities': [
                    'Real-time transport monitoring services',
                    'Flexible work arrangement solutions'
                ],
                'risk_factors': [
                    'Monitor transport disruptions for business impact',
                    'Plan for alternative commuting options'
                ],
                'recommended_actions': [
                    'Check specific line statuses for detailed planning',
                    'Use real-time transport updates for route optimization'
                ],
                'summary_timestamp': datetime.utcnow().isoformat(),
                'note': 'Fallback summary provided due to analysis error'
            }
    
    def _prepare_chart_data(self, df: pd.DataFrame) -> List[Dict]:
        """Prepare data for charting"""
        if df.empty:
            return []
        
        return [
            {
                'timestamp': row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                'value': row['price'] if 'price' in row else row['value']
            }
            for _, row in df.iterrows()
        ]
    
    def _filter_by_timeframe(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Filter DataFrame by timeframe"""
        now = datetime.now()
        if timeframe == "24h":
            cutoff = now - timedelta(hours=24)
        elif timeframe == "7d":
            cutoff = now - timedelta(days=7)
        elif timeframe == "30d":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = now - timedelta(days=7)  # Default
        
        return df[df['timestamp'] >= cutoff]
    



    async def _identify_major_transport_issues(self, transport_data: List[Dict]) -> List[Dict]:
            
        """Identify actual major transport issues"""
        major_issues = []
        
        if not transport_data or not isinstance(transport_data, list):
            return major_issues
        
        try:
            logger.info(f"Processing {len(transport_data)} transport services for major issues")
            
            for service in transport_data:
                if isinstance(service, dict):
                    delay_minutes = service.get('delay_minutes', 0)
                    status = service.get('status', 'Unknown')
                    line_name = service.get('line_name', 'Unknown')
                    
                    # Convert delay_minutes to proper number
                    if not isinstance(delay_minutes, (int, float)):
                        try:
                            delay_minutes = float(delay_minutes)
                        except (ValueError, TypeError):
                            delay_minutes = 0
                    
                    #Only consider it a major issue if it's NOT "Good Service"
                    # and has significant delay or problematic status
                    is_problematic = (
                        status != 'Good Service' and 
                        status not in ['Good Service', 'Normal'] and
                        'good service' not in status.lower() and
                        'normal' not in status.lower()
                    )
                    
                    # Consider it major if either:
                    # 1. It's problematic AND has any delay, OR
                    # 2. Has significant delay (>15 min) regardless of status (data inconsistency)
                    if (is_problematic and delay_minutes > 0) or delay_minutes > 15:
                        # Only add if it's actually a problem
                        if is_problematic or delay_minutes > 15:
                            issue_type = self._categorize_issue_type(status, delay_minutes)
                            major_issues.append({
                                'line': line_name,
                                'delay': delay_minutes,
                                'status': status,
                                'reason': service.get('reason', 'No reason provided')[:100],
                                'type': issue_type,
                                'severity': self._assess_issue_severity(status, delay_minutes)
                            })
                            #logger.info(f"MAJOR ISSUE: {line_name} - {status} - {delay_minutes}min - {issue_type}")
            
            # Sort by severity (delay minutes and status type)
            major_issues.sort(key=lambda x: (x['delay'], 1 if x['status'] != 'Good Service' else 0), reverse=True)
            logger.info(f"Found {len(major_issues)} actual major issues after filtering")
            return major_issues # Return top 5 most severe issues
            
        except Exception as e:
            logger.error(f"Error identifying transport issues: {e}")
            return []

    def _categorize_issue_type(self, status: str, delay_minutes: float) -> str:
        """Categorize the type of transport issue"""
        status_lower = status.lower()
        
        if 'minor delay' in status_lower:
            return 'minor_delay'
        elif 'severe delay' in status_lower or 'major delay' in status_lower:
            return 'severe_delay'
        elif 'part closure' in status_lower or 'part suspended' in status_lower:
            return 'part_closure'
        elif 'suspended' in status_lower or 'closure' in status_lower:
            return 'suspended'
        elif 'reduced service' in status_lower:
            return 'reduced_service'
        elif 'planned closure' in status_lower:
            return 'planned_closure'
        elif 'good service' in status_lower or status == 'Good Service':
            return 'good_service' if delay_minutes <= 15 else 'data_inconsistency'
        else:
            return 'other_issue'

    def _assess_issue_severity(self, status: str, delay_minutes: float) -> str:
        """Assess the severity of an issue"""
        if delay_minutes > 30 or 'severe' in status.lower() or 'suspended' in status.lower():
            return 'high'
        elif delay_minutes > 15 or 'closure' in status.lower():
            return 'medium'
        elif delay_minutes > 5 or 'delay' in status.lower():
            return 'low'
        else:
            return 'info'


    
    async def _get_top_movers(self, financial_data: pd.DataFrame) -> List[Dict]:
        """Get top moving stocks"""
        if financial_data.empty:
            return []
        
        # Group by symbol and calculate changes
        movers = []
        for symbol in financial_data['symbol'].unique():
            symbol_data = financial_data[financial_data['symbol'] == symbol]
            if len(symbol_data) > 1:
                current = symbol_data['price'].iloc[-1]
                previous = symbol_data['price'].iloc[-2]
                change = ((current - previous) / previous * 100)
                movers.append({
                    'symbol': symbol,
                    'change': round(change, 2),
                    'current_price': round(current, 2)
                })
        
        return sorted(movers, key=lambda x: abs(x['change']), reverse=True)[:5]



    async def _assess_market_outlook(self, sector_data: Dict[str, Any]) -> str:
        """Assess market outlook based on sector data"""
        try:
            transport_data = sector_data.get('transportation', {})
            
            # Analyze transport data for market outlook
            total_lines = transport_data.get('total_lines', 0)
            delayed_lines = transport_data.get('delayed_lines', 0)
            delay_percentage = transport_data.get('delay_percentage', 0)
            
            if total_lines == 0:
                return "Insufficient transport data for market assessment"
            
            if delay_percentage > 30:
                return "🚧 Significant transport disruptions affecting business operations. Consider remote work options."
            elif delay_percentage > 15:
                return "⚠️ Moderate transport delays observed. Plan for longer commute times."
            elif delay_percentage > 5:
                return "📊 Minor transport issues. Normal operations with slight adjustments recommended."
            else:
                return "✅ Transport network operating normally. Optimal conditions for business operations."
                
        except Exception as e:
            logger.error(f"Error assessing market outlook: {e}")
            return "Market analysis temporarily unavailable"

    async def _identify_opportunities(self, sector_data: Dict[str, Any]) -> List[str]:
        """Identify business opportunities based on sector data"""
        try:
            opportunities = []
            transport_data = sector_data.get('transportation', {})
            
            delayed_lines = transport_data.get('delayed_lines', 0)
            major_issues = transport_data.get('major_issues', [])
            
            if delayed_lines > 5:
                opportunities.append("🚇 High transport delays present opportunities for remote work solutions")
                opportunities.append("🕒 Flexible scheduling could improve employee productivity during disruptions")
            
            if len(major_issues) > 2:
                opportunities.append("📱 Develop real-time transport alert services for affected areas")
                opportunities.append("🚌 Promote alternative transport options and partnerships")
            
            if not opportunities:
                opportunities.append("📈 Monitor transport patterns for emerging business opportunities")
                opportunities.append("🔍 Explore data analytics for transport optimization services")
            
            return opportunities[:4]  # Return top 4 opportunities
            
        except Exception as e:
            logger.error(f"Error identifying opportunities: {e}")
            return ["Opportunity analysis temporarily unavailable"]

    async def _assess_risks(self, sector_data: Dict[str, Any]) -> List[str]:
        """Assess risk factors based on sector data"""
        try:
            risks = []
            transport_data = sector_data.get('transportation', {})
            
            delayed_lines = transport_data.get('delayed_lines', 0)
            delay_percentage = transport_data.get('delay_percentage', 0)
            major_issues = transport_data.get('major_issues', [])
            
            if delay_percentage > 20:
                risks.append("⏰ High risk of employee lateness and productivity loss")
                risks.append("🚚 Supply chain disruptions possible due to transport issues")
            
            if len(major_issues) > 3:
                risks.append("🏢 Potential impact on customer access to business locations")
                risks.append("💼 Increased operational costs from transport alternatives")
            
            if delayed_lines > 0:
                risks.append("📉 Reduced efficiency in logistics and distribution")
            
            if not risks:
                risks.append("📊 Monitor transport network for emerging risks")
                risks.append("🔔 Stay alert for unexpected service disruptions")
            
            return risks[:4]  # Return top 4 risks
            
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            return ["Risk assessment temporarily unavailable"]

    async def _generate_actionable_insights(self, sector_data: Dict[str, Any]) -> List[str]:
        """Generate actionable insights based on sector data"""
        try:
            insights = []
            transport_data = sector_data.get('transportation', {})
            
            delayed_lines = transport_data.get('delayed_lines', 0)
            delay_percentage = transport_data.get('delay_percentage', 0)
            major_issues = transport_data.get('major_issues', [])
            
            if delay_percentage > 15:
                insights.append("🔄 Implement flexible work hours for employees affected by transport delays")
                insights.append("📱 Use real-time transport apps for route planning and alternative options")
            
            if len(major_issues) > 0:
                issue_lines = [issue.get('line', 'Unknown') for issue in major_issues]
                insights.append(f"🚫 Avoid affected lines: {', '.join(set(issue_lines))}")
                insights.append("🚍 Consider bus alternatives or ride-sharing for critical commutes")
            
            if delayed_lines > 0:
                insights.append("⏰ Allow additional travel time for meetings and appointments")
                insights.append("💻 Enable remote participation options for important meetings")
            
            if not insights:
                insights.append("✅ Transport conditions favorable - maintain current operations")
                insights.append("📊 Continue monitoring transport data for proactive planning")
            
            return insights[:4]  # Return top 4 insights
            
        except Exception as e:
            logger.error(f"Error generating actionable insights: {e}")
            return ["Insight generation temporarily unavailable"]
        



    async def _analyze_transport_trends(self, transport_data: List[Dict]) -> Dict[str, Any]:
            
        """Analyze transport trends with detailed insights"""
        try:
            if not transport_data or not isinstance(transport_data, list):
                return {'trend': 'unknown', 'analysis': 'No transport data available'}
            
            # Calculate comprehensive metrics
            total_services = len(transport_data)
            good_services = len([x for x in transport_data if isinstance(x, dict) and x.get('status') == 'Good Service'])
            delayed_services = total_services - good_services
            delay_percentage = (delayed_services / total_services) * 100 if total_services > 0 else 0
            
            # Analyze service types
            service_statuses = {}
            for service in transport_data:
                if isinstance(service, dict):
                    status = service.get('status', 'Unknown')
                    service_statuses[status] = service_statuses.get(status, 0) + 1
            
            # Identify major issues
            major_issues = []
            for service in transport_data:
                if isinstance(service, dict) and service.get('status') != 'Good Service':
                    major_issues.append({
                        'line': service.get('line_name', 'Unknown'),
                        'status': service.get('status', 'Unknown'),
                        'delay_minutes': service.get('delay_minutes', 0),
                        'reason': service.get('reason', 'No reason provided')[:100]
                    })
            
            # Determine overall trend
            if delay_percentage > 25:
                trend = 'deteriorating'
                trend_emoji = '📉'
            elif delay_percentage > 10:
                trend = 'moderate'
                trend_emoji = '➡️'
            else:
                trend = 'improving'
                trend_emoji = '📈'
            
            return {
                'trend': trend,
                'trend_emoji': trend_emoji,
                'analysis': f'{trend_emoji} {delayed_services}/{total_services} services experiencing issues ({delay_percentage:.1f}%)',
                'delay_percentage': round(delay_percentage, 1),
                'service_breakdown': service_statuses,
                'major_issues_count': len(major_issues),
                'recommendation': 'Monitor affected lines closely' if delayed_services > 0 else 'Normal service conditions'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing transport trends: {e}")
            return {'trend': 'unknown', 'analysis': 'Error analyzing transport trends'}
        



    async def _get_financial_overview(self) -> Dict[str, Any]:
        """Get financial market overview from Snowflake"""
        try:
            financial_data = await self.data_loader.load_financial_data_from_snowflake()
            
            if isinstance(financial_data, pd.DataFrame) and not financial_data.empty:
                return self._process_financial_data(financial_data)
            else:
                return self._get_sample_financial_overview()
                
        except Exception as e:
            logger.error(f"Error in financial overview: {e}")
            return self._get_sample_financial_overview()
        



    def _process_financial_data(self, financial_data: pd.DataFrame) -> Dict[str, Any]:
        """Process financial data for dashboard display"""
        try:
            financial_data = financial_data.copy()

            # --- 1️⃣ Normalize datatypes ---
            import numpy as np
            financial_data['TIMESTAMP'] = pd.to_datetime(financial_data['TIMESTAMP'], errors='coerce')
            
            # Convert to date (to handle multiple entries on same day)
            financial_data['DATE'] = financial_data['TIMESTAMP'].dt.date
            
            for col in financial_data.columns:
                if financial_data[col].dtype in [np.int64, np.int32]:
                    financial_data[col] = financial_data[col].astype(int)
                elif financial_data[col].dtype in [np.float64, np.float32]:
                    financial_data[col] = financial_data[col].astype(float)

            # --- 2️⃣ Get unique dates per symbol (remove duplicates) ---
            # Keep only the last entry for each symbol on each day
            financial_data = financial_data.sort_values(['SYMBOL', 'TIMESTAMP'], ascending=True)
            financial_data = financial_data.drop_duplicates(['SYMBOL', 'DATE'], keep='last')
            
            # --- 3️⃣ Ensure we have at least 2 days of data per symbol ---
            symbol_day_counts = financial_data.groupby('SYMBOL')['DATE'].nunique()
            valid_symbols = symbol_day_counts[symbol_day_counts >= 2].index
            financial_data = financial_data[financial_data['SYMBOL'].isin(valid_symbols)]
            
            if financial_data.empty:
                logger.warning("No symbols with sufficient data for change calculation")
                return self._get_sample_financial_overview()

            # --- 4️⃣ Compute daily changes ---
            all_stocks = []
            daily_changes = []

            for symbol, symbol_data in financial_data.groupby('SYMBOL'):
                symbol_data = symbol_data.sort_values('TIMESTAMP', ascending=True)
                
                # Get the last two unique days
                if len(symbol_data) >= 2:
                    current_day = symbol_data.iloc[-1]
                    previous_day = symbol_data.iloc[-2]
                    
                    current_close = float(current_day['CLOSE'])
                    previous_close = float(previous_day['CLOSE'])
                    
                    if previous_close != 0:
                        change_percent = ((current_close - previous_close) / previous_close) * 100
                    else:
                        change_percent = 0.0

                    stock_data = {
                        'symbol': str(symbol),
                        'company': str(current_day['COMPANY_NAME']),
                        'current_price': round(current_close, 2),
                        'change_percent': round(change_percent, 2),
                        'volume': int(current_day['VOLUME']),
                    }

                    all_stocks.append(stock_data)
                    daily_changes.append(stock_data)

            # --- 5️⃣ If still no data, return sample ---
            if not daily_changes:
                logger.warning("No daily changes calculated, returning sample data")
                return self._get_sample_financial_overview()

            # --- 6️⃣ Sort stocks by performance ---
            all_stocks.sort(key=lambda x: x['change_percent'], reverse=True)
            daily_changes.sort(key=lambda x: abs(x['change_percent']), reverse=True)

            top_gainers = [s for s in daily_changes if s['change_percent'] > 0][:3]
            top_losers = [s for s in daily_changes if s['change_percent'] < 0][:3]

            # --- 7️⃣ Market metrics ---
            total_change = sum(s['change_percent'] for s in daily_changes)
            avg_change = total_change / len(daily_changes) if daily_changes else 0.0
            advancing = sum(1 for s in daily_changes if s['change_percent'] > 0)
            declining = sum(1 for s in daily_changes if s['change_percent'] < 0)
            unchanged = sum(1 for s in daily_changes if s['change_percent'] == 0)

            # --- 8️⃣ Chart data ---
            chart_data = self._prepare_financial_chart_data(financial_data)

            # --- 9️⃣ Market trend detection ---
            if avg_change > 1:
                trend = 'bullish'
            elif avg_change < -1:
                trend = 'bearish'
            else:
                trend = 'neutral'

            return {
                'market_trend': trend,
                'average_change': round(avg_change, 2),
                'advancing_stocks': advancing,
                'declining_stocks': declining,
                'unchanged_stocks': unchanged,
                'total_stocks': len(daily_changes),
                'all_stocks': all_stocks,
                'top_gainers': top_gainers,
                'top_losers': top_losers,
                'chart_data': chart_data,
                'market_summary': self._generate_market_summary(avg_change, trend, advancing, declining),
                'alerts': self._generate_financial_alerts(daily_changes, avg_change),
            }

        except Exception as e:
            logger.error(f"Error processing financial data: {e}")
            return self._get_sample_financial_overview()
        

    def _prepare_financial_chart_data(self, financial_data: pd.DataFrame) -> List[Dict]:
        """Prepare financial data for charting"""
        try:
            chart_data = []
            # Convert numpy types first
            financial_data = financial_data.copy()
            financial_data['CLOSE'] = financial_data['CLOSE'].astype(float)
            
            # Get data for last 7 days
            recent_data = financial_data[financial_data['TIMESTAMP'] >= (datetime.now() - timedelta(days=7))]
            
            if recent_data.empty:
                return []
                
            # Group by date and calculate average market performance
            daily_avg = recent_data.groupby('TIMESTAMP').agg({
                'CLOSE': 'mean',
                'SYMBOL': 'count'
            }).reset_index()
            
            for _, row in daily_avg.iterrows():
                chart_data.append({
                    'timestamp': row['TIMESTAMP'].isoformat() if hasattr(row['TIMESTAMP'], 'isoformat') else str(row['TIMESTAMP']),
                    'price': float(row['CLOSE']),
                    'stocks_traded': int(row['SYMBOL'])
                })
            
            return chart_data
        except Exception as e:
            logger.error(f"Error preparing financial chart data: {e}")
            return []
        

    def _generate_market_summary(self, avg_change: float, trend: str, advancing: int, declining: int) -> str:
        """Generate market summary based on metrics"""
        if trend == 'bullish':
            return f"📈 Bullish market with {advancing} advancing stocks. Average gain: {avg_change:+.2f}%"
        elif trend == 'bearish':
            return f"📉 Bearish pressure with {declining} declining stocks. Average loss: {avg_change:+.2f}%"
        else:
            return f"➡️ Market neutral with {advancing} advancing and {declining} declining stocks"

    def _generate_financial_alerts(self, stocks: List[Dict], avg_change: float) -> List[Dict]:
        """Generate financial alerts based on market conditions"""
        alerts = []
        
        # Volatility alert
        changes = [abs(stock['change_percent']) for stock in stocks]
        avg_volatility = sum(changes) / len(changes) if changes else 0
        
        if avg_volatility > 5:
            alerts.append({
                'type': 'high_volatility',
                'message': f'High market volatility detected ({avg_volatility:.1f}% average change)',
                'severity': 'warning'
            })
        
        # Significant moves alert
        big_movers = [stock for stock in stocks if abs(stock['change_percent']) > 10]
        if big_movers:
            alerts.append({
                'type': 'big_movers',
                'message': f'{len(big_movers)} stocks moved more than 10%',
                'severity': 'info'
            })
        
        # Market direction alert
        if avg_change > 3:
            alerts.append({
                'type': 'strong_bullish',
                'message': 'Strong bullish momentum in the market',
                'severity': 'success'
            })
        elif avg_change < -3:
            alerts.append({
                'type': 'strong_bearish',
                'message': 'Strong bearish pressure in the market',
                'severity': 'error'
            })
        
        return alerts
    


    def _get_sample_financial_overview(self) -> Dict[str, Any]:
        """Fallback sample financial data"""
        return {
            'market_trend': 'neutral',
            'average_change': 0.5,
            'advancing_stocks': 4,
            'declining_stocks': 3,
            'unchanged_stocks': 1,
            'total_stocks': 8,
            'top_gainers': [
                {'symbol': 'HSBA.L', 'change_percent': 2.1, 'current_price': 1038.8},
                {'symbol': 'BP.L', 'change_percent': 1.2, 'current_price': 445.5},
                {'symbol': 'GSK.L', 'change_percent': 1.1, 'current_price': 1486.0}
            ],
            'top_losers': [
                {'symbol': 'AZN.L', 'change_percent': -1.5, 'current_price': 11000.0},
                {'symbol': 'ULVR.L', 'change_percent': -0.8, 'current_price': 4412.0},
                {'symbol': 'RIO.L', 'change_percent': -0.7, 'current_price': 4831.5}
            ],
            'chart_data': [
                {
                    'timestamp': datetime.utcnow().isoformat(),
                    'price': 4500.0,
                    'stocks_traded': 8
                }
            ],
            'market_summary': 'Market showing mixed performance with slight bullish bias',
            'alerts': []
        }