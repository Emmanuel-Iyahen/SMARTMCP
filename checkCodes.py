    async def get_overview(self) -> Dict[str, Any]:
        """Get comprehensive dashboard overview for all sectors"""
        try:
            # Load data from all sectors concurrently
            energy_data, transport_data, financial_data, weather_data = await asyncio.gather(
                #self._get_energy_overview(),
                self._get_transport_overview(),
                #self._get_financial_overview(),
                self._get_weather_overview()
            )
            
            return {
                #'energy': energy_data,
                'transportation': transport_data,
                #'finance': financial_data,
                'weather': weather_data,
                'last_updated': datetime.utcnow().isoformat(),
                'summary': await self._generate_overall_summary({
                    #'energy': energy_data,
                    'transportation': transport_data,
                    #'finance': financial_data
                })
            }
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {e}")
            raise



    async def _generate_overall_summary(self, sector_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall business summary"""
        # Use AI to generate insights across sectors
        summary_prompt = f"""
        Analyze the following multi-sector data and provide a concise business summary:
        
        Energy: {sector_data['energy']}
        Transportation: {sector_data['transportation']} 
        Finance: {sector_data['finance']}
        
        Focus on cross-sector implications and business opportunities.
        """
        
        try:
            # This would use the AI analyzer for cross-sector insights
            # For now, return a structured summary
            return {
                'market_outlook': await self._assess_market_outlook(sector_data),
                'key_opportunities': await self._identify_opportunities(sector_data),
                'risk_factors': await self._assess_risks(sector_data),
                'recommended_actions': await self._generate_actionable_insights(sector_data)
            }
        except Exception as e:
            logger.error(f"Error generating overall summary: {e}")
            return {
                'market_outlook': 'Data analysis in progress',
                'key_opportunities': [],
                'risk_factors': [],
                'recommended_actions': ['Monitor sector data for updates']
            }