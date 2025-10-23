
// import React, { useState, useEffect } from 'react';
// import {
//   Grid,
//   Card,
//   CardContent,
//   Typography,
//   Box,
//   Chip,
//   LinearProgress,
//   List,
//   ListItem,
//   ListItemText,
//   Alert,
//   Button,
//   Paper,
//   Tabs,
//   Tab,
// } from '@mui/material';
// import { 
//   LineChart, 
//   Line, 
//   XAxis, 
//   YAxis, 
//   CartesianGrid, 
//   Tooltip, 
//   ResponsiveContainer,
//   BarChart,
//   Bar,
//   AreaChart,
//   Area,
//   ComposedChart
// } from 'recharts';
// import { dashboardService } from '../services/api';

// const Dashboard = () => {
//   const [dashboardData, setDashboardData] = useState(null);
//   const [trendData, setTrendData] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [trendLoading, setTrendLoading] = useState(false);
//   const [error, setError] = useState(null);

//   const loadDashboardData = async () => {
//     try {
//       setLoading(true);
//       setError(null);
//       const response = await dashboardService.getOverview();
      
//       let actualData;
//       if (response.data && response.data.data) {
//         actualData = response.data.data;
//       } else if (response.data && (response.data.transportation || response.data.weather)) {
//         actualData = response.data;
//       } else {
//         actualData = response.data || {};
//       }
      
//       setDashboardData(actualData);
//     } catch (error) {
//       console.error('Error loading dashboard data:', error);
//       setError(error.response?.data?.detail || error.message || 'Failed to load dashboard data');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const loadTrendData = async () => {
//     try {
//       setTrendLoading(true);
//       const response = await dashboardService.getFinancialTrends();
//       setTrendData(response.data);
//     } catch (error) {
//       console.error('Error loading trend data:', error);
//     } finally {
//       setTrendLoading(false);
//     }
//   };

//   useEffect(() => {
//     loadDashboardData();
//     loadTrendData();
//   }, []);

//   if (loading) {
//     return (
//       <Box sx={{ p: 3 }}>
//         <LinearProgress />
//         <Typography variant="body2" sx={{ mt: 2 }}>Loading dashboard data...</Typography>
//       </Box>
//     );
//   }

//   if (error) {
//     return (
//       <Box sx={{ p: 3 }}>
//         <Alert 
//           severity="error" 
//           action={
//             <Button color="inherit" size="small" onClick={loadDashboardData}>
//               Retry
//             </Button>
//           }
//         >
//           {error}
//         </Alert>
//       </Box>
//     );
//   }

//   if (!dashboardData) {
//     return (
//       <Box sx={{ p: 3 }}>
//         <Alert severity="warning">
//           No dashboard data available. Please check your backend connection.
//         </Alert>
//       </Box>
//     );
//   }

//   // Extract sectors and prioritize key ones
//   const sectors = Object.keys(dashboardData).filter(key => 
//     !['last_updated', 'summary', 'status', 'timestamp'].includes(key)
//   );

//   // Define priority sectors for the top section
//   const prioritySectors = ['finance', 'transportation', 'weather'];
//   const prioritySectorData = prioritySectors
//     .filter(sector => sectors.includes(sector))
//     .map(sector => ({
//       name: sector,
//       data: dashboardData[sector]
//     }));

//   // Other sectors for the bottom section
//   const otherSectors = sectors.filter(sector => !prioritySectors.includes(sector));

//   return (
//     <Box sx={{ p: 3 }}>
//       <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
//         <Typography variant="h4">
//           Universal MCP Platform Dashboard
//         </Typography>
//         <Box>
//           <Button variant="outlined" onClick={loadDashboardData} sx={{ mr: 1 }}>
//             Refresh Dashboard
//           </Button>
//           <Button variant="outlined" onClick={loadTrendData}>
//             Refresh Trends
//           </Button>
//         </Box>
//       </Box>
      
//       {dashboardData.last_updated && (
//         <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
//           Last updated: {new Date(dashboardData.last_updated).toLocaleString()}
//         </Typography>
//       )}
      
//       {/* Summary Section */}
//       {dashboardData.summary && (
//         <Card sx={{ mb: 3 }}>
//           <CardContent>
//             <Typography variant="h6" gutterBottom>Business Summary</Typography>
//             <Typography variant="body2" color="text.secondary" paragraph>
//               {dashboardData.summary.market_outlook || 'Market outlook analysis'}
//             </Typography>
            
//             <Grid container spacing={2}>
//               <Grid item xs={12} md={6}>
//                 <Typography variant="subtitle2">Opportunities</Typography>
//                 <List dense>
//                   {dashboardData.summary.key_opportunities?.map((opp, index) => (
//                     <ListItem key={index}>
//                       <ListItemText primary={opp} />
//                     </ListItem>
//                   ))}
//                 </List>
//               </Grid>
//               <Grid item xs={12} md={6}>
//                 <Typography variant="subtitle2">Risks</Typography>
//                 <List dense>
//                   {dashboardData.summary.risk_factors?.map((risk, index) => (
//                     <ListItem key={index}>
//                       <ListItemText primary={risk} />
//                     </ListItem>
//                   ))}
//                 </List>
//               </Grid>
//             </Grid>
//           </CardContent>
//         </Card>
//       )}

//       {/* Centralized Priority Cards Section */}
//       <Box sx={{ mb: 4 }}>
//         <Typography variant="h5" gutterBottom sx={{ 
//           display: 'flex', 
//           alignItems: 'center', 
//           mb: 3,
//           color: 'primary.main',
//           fontWeight: 'bold'
//         }}>
//           🎯 Key Metrics Overview
//         </Typography>
        
//         <Grid container spacing={3}>
//           {prioritySectorData.map(({ name, data }) => (
//             <Grid item xs={12} md={4} key={name}>
//               <SectorCard sector={name} data={data} />
//             </Grid>
//           ))}
//         </Grid>
//       </Box>

//       {/* Financial Trend Analysis Section - Placed Below Priority Cards */}
//       <FinancialTrendSection 
//         trendData={trendData} 
//         loading={trendLoading}
//         onRefresh={loadTrendData}
//       />

//       {/* Other Sectors Section */}
//       {otherSectors.length > 0 && (
//         <Box sx={{ mt: 4 }}>
//           <Typography variant="h5" gutterBottom sx={{ 
//             display: 'flex', 
//             alignItems: 'center',
//             mb: 3,
//             color: 'text.secondary'
//           }}>
//             📊 Additional Metrics
//           </Typography>
          
//           <Grid container spacing={3}>
//             {otherSectors.map((sector) => {
//               const sectorData = dashboardData[sector];
//               return (
//                 <Grid item xs={12} md={6} lg={4} key={sector}>
//                   <SectorCard sector={sector} data={sectorData} />
//                 </Grid>
//               );
//             })}
//           </Grid>
//         </Box>
//       )}
//     </Box>
//   );
// };


// // Financial Trend Section Component - FIXED
// const FinancialTrendSection = ({ trendData, loading, onRefresh }) => {
//   const [selectedTab, setSelectedTab] = useState(0);

//   if (loading) {
//     return (
//       <Paper sx={{ p: 3, mb: 3, mt: 2 }}>
//         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
//           <Typography variant="h5" sx={{ color: 'secondary.main', fontWeight: 'bold' }}>
//             📈 Financial Trend Analysis
//           </Typography>
//           <Button variant="outlined" size="small" disabled>
//             Loading...
//           </Button>
//         </Box>
//         <LinearProgress />
//       </Paper>
//     );
//   }

//   if (!trendData) {
//     return (
//       <Paper sx={{ p: 3, mb: 3, mt: 2 }}>
//         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
//           <Typography variant="h5" sx={{ color: 'secondary.main', fontWeight: 'bold' }}>
//             📈 Financial Trend Analysis
//           </Typography>
//           <Button variant="outlined" size="small" onClick={onRefresh}>
//             Load Trends
//           </Button>
//         </Box>
//         <Alert severity="info">
//           Trend data not available. Click "Load Trends" to fetch historical analysis.
//         </Alert>
//       </Paper>
//     );
//   }

//   console.log('Full Trend Data:', trendData); // Debug log
//   console.log('Trend Data.data:', trendData.data); // Debug log

//   // Extract the actual data from the response
//   const trendDataContent = trendData.data || {};

//   return (
//     <Paper sx={{ p: 3, mb: 3, mt: 2, bgcolor: 'background.default' }}>
//       <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
//         <Typography variant="h5" sx={{ color: 'secondary.main', fontWeight: 'bold' }}>
//           📈 Financial Trend Analysis
//         </Typography>
//         <Button variant="outlined" size="small" onClick={onRefresh}>
//           Refresh Trends
//         </Button>
//       </Box>

//       <Tabs 
//         value={selectedTab} 
//         onChange={(e, newValue) => setSelectedTab(newValue)} 
//         sx={{ 
//           mb: 3,
//           borderBottom: 1,
//           borderColor: 'divider'
//         }}
//         indicatorColor="secondary"
//         textColor="secondary"
//       >
//         <Tab label="Market Overview" />
//         <Tab label="Stock Performance" />
//         <Tab label="Historical Trends" />
//         <Tab label="Sector Analysis" />
//       </Tabs>

//       {selectedTab === 0 && <MarketOverviewTab data={trendDataContent} />}
//       {selectedTab === 1 && <StockPerformanceTab data={trendDataContent} />}
//       {selectedTab === 2 && <HistoricalTrendsTab data={trendDataContent} />}
//       {selectedTab === 3 && <SectorAnalysisTab data={trendDataContent} />}
//     </Paper>
//   );
// };

// // UPDATED Tab Components to match actual data structure
// const MarketOverviewTab = ({ data }) => {
//   // Transform data for the chart
//   const chartData = data.market_trends?.map(trend => ({
//     date: trend.date,
//     price: trend.price,
//     volume: trend.volume,
//     price_change: trend.price_change,
//     stocks_traded: trend.stocks_traded
//   })) || [];

//   return (
//     <Grid container spacing={3}>
//       <Grid item xs={12} md={8}>
//         <Card elevation={2}>
//           <CardContent>
//             <Typography variant="h6" gutterBottom color="primary">
//               Market Trend ({chartData.length} Days)
//             </Typography>
//             {chartData.length > 0 ? (
//               <ResponsiveContainer width="100%" height={300}>
//                 <ComposedChart data={chartData}>
//                   <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
//                   <XAxis 
//                     dataKey="date"
//                     tick={{ fontSize: 12 }}
//                     tickFormatter={(value) => new Date(value).toLocaleDateString()}
//                   />
//                   <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
//                   <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
//                   <Tooltip 
//                     formatter={(value, name) => {
//                       if (name === 'price') return [`£${value}`, 'Market Average'];
//                       if (name === 'volume') return [`${(value / 1000000).toFixed(1)}M`, 'Volume'];
//                       if (name === 'price_change') return [`${value}%`, 'Daily Change'];
//                       return [value, name];
//                     }}
//                     labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
//                     contentStyle={{ 
//                       backgroundColor: '#fff',
//                       border: '1px solid #ccc',
//                       borderRadius: '4px'
//                     }}
//                   />
//                   <Area 
//                     yAxisId="left"
//                     type="monotone" 
//                     dataKey="price" 
//                     fill="#8884d8" 
//                     stroke="#8884d8" 
//                     fillOpacity={0.3}
//                     strokeWidth={2}
//                   />
//                   <Bar 
//                     yAxisId="right"
//                     dataKey="volume" 
//                     fill="#82ca9d" 
//                     opacity={0.6}
//                   />
//                 </ComposedChart>
//               </ResponsiveContainer>
//             ) : (
//               <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
//                 <Typography color="text.secondary">No market trend data available</Typography>
//               </Box>
//             )}
//           </CardContent>
//         </Card>
//       </Grid>
      
//       <Grid item xs={12} md={4}>
//         <Card elevation={2} sx={{ mb: 2 }}>
//           <CardContent>
//             <Typography variant="h6" gutterBottom color="primary">
//               Performance Metrics
//             </Typography>
//             {data.performance_metrics?.map((metric, index) => (
//               <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1.5 }}>
//                 <Typography variant="body2" color="text.secondary">
//                   {metric.name}:
//                 </Typography>
//                 <Chip 
//                   label={metric.value} 
//                   size="small"
//                   color={
//                     metric.value.includes('+') ? 'success' : 
//                     metric.value.includes('-') ? 'error' : 'default'
//                   }
//                   variant="outlined"
//                 />
//               </Box>
//             )) || (
//               <Typography color="text.secondary">No performance metrics available</Typography>
//             )}
//           </CardContent>
//         </Card>
        
//         <Card elevation={2}>
//           <CardContent>
//             <Typography variant="h6" gutterBottom color="primary">
//               Trend Indicators
//             </Typography>
//             {data.trend_indicators?.map((indicator, index) => (
//               <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
//                 <Typography variant="body2" color="text.secondary">
//                   {indicator.name}
//                 </Typography>
//                 <Chip 
//                   label={indicator.status} 
//                   size="small"
//                   color={
//                     indicator.status === 'Bullish' ? 'success' :
//                     indicator.status === 'Bearish' ? 'error' : 'default'
//                   }
//                 />
//               </Box>
//             )) || (
//               <Typography color="text.secondary">No trend indicators available</Typography>
//             )}
//           </CardContent>
//         </Card>
//       </Grid>
//     </Grid>
//   );
// };

// const StockPerformanceTab = ({ data }) => {
//   const stockData = data.stock_performance || [];
  
//   return (
//     <Grid container spacing={2}>
//       <Grid item xs={12}>
//         <Card elevation={2}>
//           <CardContent>
//             <Typography variant="h6" gutterBottom color="primary">
//               Stock Performance ({stockData.length} Stocks)
//             </Typography>
//             {stockData.length > 0 ? (
//               <ResponsiveContainer width="100%" height={400}>
//                 <BarChart
//                   data={stockData}
//                   layout="vertical"
//                   margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
//                 >
//                   <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
//                   <XAxis 
//                     type="number" 
//                     tick={{ fontSize: 12 }}
//                     tickFormatter={(value) => `${value}%`}
//                   />
//                   <YAxis 
//                     type="category" 
//                     dataKey="symbol"
//                     tick={{ fontSize: 12 }}
//                     width={80}
//                   />
//                   <Tooltip 
//                     formatter={(value, name) => {
//                       if (name === 'change') return [`${value}%`, 'Change'];
//                       return [value, name];
//                     }}
//                     labelFormatter={(label) => `Symbol: ${label}`}
//                     contentStyle={{ 
//                       backgroundColor: '#fff',
//                       border: '1px solid #ccc',
//                       borderRadius: '4px'
//                     }}
//                   />
//                   <Bar 
//                     dataKey="change" 
//                     fill={(entry) => entry.change >= 0 ? '#4caf50' : '#f44336'}
//                     radius={[0, 4, 4, 0]}
//                   />
//                 </BarChart>
//               </ResponsiveContainer>
//             ) : (
//               <Box sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
//                 <Typography color="text.secondary">No stock performance data available</Typography>
//               </Box>
//             )}
//           </CardContent>
//         </Card>
//       </Grid>
//     </Grid>
//   );
// };


// const HistoricalTrendsTab = ({ data }) => {
//   const volatilityData = data.volatility_data || [];
//   const movingAverages = data.moving_averages || [];
  
//   return (
//     <Grid container spacing={3}>
//       <Grid item xs={12} md={6}>
//         <Card elevation={2}>
//           <CardContent>
//             <Typography variant="h6" gutterBottom color="primary">
//               Volatility Analysis
//             </Typography>
//             {volatilityData.length > 0 ? (
//               <ResponsiveContainer width="100%" height={250}>
//                 <LineChart data={volatilityData}>
//                   <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
//                   <XAxis 
//                     dataKey="date"
//                     tick={{ fontSize: 12 }}
//                     tickFormatter={(value) => new Date(value).toLocaleDateString()}
//                   />
//                   <YAxis 
//                     tick={{ fontSize: 12 }}
//                     tickFormatter={(value) => `${value}%`}
//                   />
//                   <Tooltip 
//                     formatter={(value) => [`${value}%`, 'Volatility']}
//                     labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
//                     contentStyle={{ 
//                       backgroundColor: '#fff',
//                       border: '1px solid #ccc',
//                       borderRadius: '4px'
//                     }}
//                   />
//                   <Line 
//                     type="monotone" 
//                     dataKey="volatility" 
//                     stroke="#ff6b6b" 
//                     strokeWidth={2}
//                     dot={{ r: 2 }}
//                     activeDot={{ r: 4 }}
//                   />
//                 </LineChart>
//               </ResponsiveContainer>
//             ) : (
//               <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
//                 <Typography color="text.secondary">No volatility data available</Typography>
//               </Box>
//             )}
//           </CardContent>
//         </Card>
//       </Grid>
      
//       <Grid item xs={12} md={6}>
//         <Card elevation={2}>
//           <CardContent>
//             <Typography variant="h6" gutterBottom color="primary">
//               Moving Averages
//             </Typography>
//             {movingAverages.length > 0 ? (
//               <ResponsiveContainer width="100%" height={250}>
//                 <LineChart data={movingAverages}>
//                   <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
//                   <XAxis 
//                     dataKey="date"
//                     tick={{ fontSize: 12 }}
//                     tickFormatter={(value) => new Date(value).toLocaleDateString()}
//                   />
//                   <YAxis tick={{ fontSize: 12 }} />
//                   <Tooltip 
//                     formatter={(value, name) => {
//                       if (name === 'price') return [`£${value}`, 'Price'];
//                       if (name === 'price_7d') return [`£${value}`, '7-Day MA'];
//                       if (name === 'price_30d') return [`£${value}`, '30-Day MA'];
//                       return [value, name];
//                     }}
//                     labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
//                     contentStyle={{ 
//                       backgroundColor: '#fff',
//                       border: '1px solid #ccc',
//                       borderRadius: '4px'
//                     }}
//                   />
//                   <Line 
//                     type="monotone" 
//                     dataKey="price" 
//                     stroke="#8884d8" 
//                     strokeWidth={2}
//                     name="Price"
//                     dot={{ r: 2 }}
//                   />
//                   <Line 
//                     type="monotone" 
//                     dataKey="price_7d" 
//                     stroke="#4ecdc4" 
//                     strokeWidth={2}
//                     name="7-Day MA"
//                     dot={false}
//                     strokeDasharray="3 3"
//                   />
//                   <Line 
//                     type="monotone" 
//                     dataKey="price_30d" 
//                     stroke="#45b7d1" 
//                     strokeWidth={2}
//                     name="30-Day MA"
//                     dot={false}
//                     strokeDasharray="5 5"
//                   />
//                 </LineChart>
//               </ResponsiveContainer>
//             ) : (
//               <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
//                 <Typography color="text.secondary">No moving average data available</Typography>
//               </Box>
//             )}
//           </CardContent>
//         </Card>
//       </Grid>
//     </Grid>
//   );
// };


// const SectorAnalysisTab = ({ data }) => {
//   const sectorPerformance = data.sector_performance || [];
//   const sectorRankings = data.sector_rankings || [];
  
//   return (
//     <Grid container spacing={2}>
//       <Grid item xs={12} md={8}>
//         <Card elevation={2}>
//           <CardContent>
//             <Typography variant="h6" gutterBottom color="primary">
//               Sector Performance ({sectorPerformance.length} Sectors)
//             </Typography>
//             {sectorPerformance.length > 0 ? (
//               <ResponsiveContainer width="100%" height={300}>
//                 <BarChart data={sectorPerformance}>
//                   <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
//                   <XAxis 
//                     dataKey="sector" 
//                     tick={{ fontSize: 12 }}
//                     angle={-45}
//                     textAnchor="end"
//                     height={80}
//                   />
//                   <YAxis 
//                     tick={{ fontSize: 12 }}
//                     tickFormatter={(value) => `${value}%`}
//                   />
//                   <Tooltip 
//                     formatter={(value, name) => {
//                       if (name === 'performance') return [`${value}%`, 'Performance'];
//                       return [value, name];
//                     }}
//                     contentStyle={{ 
//                       backgroundColor: '#fff',
//                       border: '1px solid #ccc',
//                       borderRadius: '4px'
//                     }}
//                   />
//                   <Bar 
//                     dataKey="performance" 
//                     fill={(entry) => entry.performance >= 0 ? '#4caf50' : '#f44336'}
//                     radius={[4, 4, 0, 0]}
//                   />
//                 </BarChart>
//               </ResponsiveContainer>
//             ) : (
//               <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
//                 <Typography color="text.secondary">No sector performance data available</Typography>
//               </Box>
//             )}
//           </CardContent>
//         </Card>
//       </Grid>
      
//       <Grid item xs={12} md={4}>
//         <Card elevation={2}>
//           <CardContent>
//             <Typography variant="h6" gutterBottom color="primary">
//               Sector Rankings
//             </Typography>
//             {sectorRankings.length > 0 ? (
//               <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
//                 {sectorRankings.map((sector, index) => (
//                   <ListItem 
//                     key={index} 
//                     sx={{ 
//                       borderBottom: index < sectorRankings.length - 1 ? 1 : 0, 
//                       borderColor: 'divider', 
//                       py: 1.5 
//                     }}
//                   >
//                     <ListItemText 
//                       primary={
//                         <Typography variant="body2" fontWeight="medium">
//                           {sector.name}
//                         </Typography>
//                       }
//                       secondary={`${sector.change}% • ${sector.trend}`}
//                     />
//                     <Chip 
//                       label={`#${index + 1}`}
//                       size="small"
//                       color={
//                         index === 0 ? 'success' : 
//                         index === 1 ? 'primary' : 
//                         index === 2 ? 'secondary' : 'default'
//                       }
//                       variant={index < 3 ? "filled" : "outlined"}
//                     />
//                   </ListItem>
//                 ))}
//               </List>
//             ) : (
//               <Typography color="text.secondary" sx={{ py: 2 }}>
//                 No sector rankings available
//               </Typography>
//             )}
//           </CardContent>
//         </Card>
//       </Grid>
//     </Grid>
//   );
// };

// // Keep your existing SectorCard component exactly as is
// const SectorCard = ({ sector, data }) => {
//   console.log(`Rendering ${sector} card with data:`, data);

//   if (!data) {
//     return (
//       <Card sx={{ height: '100%' }}>
//         <CardContent>
//           <Typography variant="h6" component="div">
//             {sector.charAt(0).toUpperCase() + sector.slice(1)}
//           </Typography>
//           <Typography variant="body2" color="text.secondary">
//             No data available
//           </Typography>
//         </CardContent>
//       </Card>
//     );
//   }

//   // Handle different data structures for different sectors
//   const getSectorDisplayData = (sector, data) => {
//     console.log(`Processing ${sector} data:`, data);
    
//     const sectorLower = sector.toLowerCase();
    
//     switch (sectorLower) {
//       case 'transportation':
//         // Categorize services by condition
//         const allServices = data.major_issues || data.majorIssues || [];
//         const serviceBreakdown = data.service_breakdown || {};
        
//         // Categorize services
//         const goodServices = allServices.filter(service => 
//           service.status === 'Good Service' || service.type === 'good_service'
//         );
        
//         const moderateServices = allServices.filter(service => 
//           service.status === 'Minor Delays' || 
//           service.status === 'Reduced Service' ||
//           service.type === 'minor_delay' ||
//           service.type === 'reduced_service'
//         );
        
//         const poorServices = allServices.filter(service => 
//           service.status === 'Part Closure' || 
//           service.status === 'Planned Closure' ||
//           service.type === 'part_closure' ||
//           service.type === 'suspended'
//         );

//         return {
//           title: 'Transportation',
//           currentValue: `${data.delayed_lines || 0}/${data.total_lines || 0} lines delayed`,
//           change: data.delay_percentage ? `${data.delay_percentage}%` : '0%',
//           trend: data.trend || 'stable',
//           chartData: data.chart_data || data.chartData || [],
//           metrics: [
//             { label: 'Total Lines', value: data.total_lines || 0 },
//             { label: 'Delayed Lines', value: data.delayed_lines || 0 },
//             { label: 'Delay %', value: data.delay_percentage ? `${data.delay_percentage}%` : '0%' }
//           ],
//           allServices: allServices,
//           goodServices: goodServices,
//           moderateServices: moderateServices,
//           poorServices: poorServices,
//           serviceBreakdown: serviceBreakdown
//         };
      
//       case 'weather':
//         // Enhanced weather data handling
//         const hasWeatherData = data.current_temp !== undefined;
//         return {
//           title: 'Weather',
//           currentValue: hasWeatherData ? `${data.current_temp || 0}°C` : 'No data',
//           change: data.condition || 'Unknown',
//           trend: data.trend || 'stable',
//           chartData: data.chart_data || data.chartData || [],
//           metrics: [
//             { label: 'Temperature', value: hasWeatherData ? `${data.current_temp || 0}°C` : 'N/A' },
//             { label: 'Humidity', value: data.humidity ? `${data.humidity}%` : 'N/A' },
//             { label: 'Condition', value: data.condition || 'Unknown' },
//             { label: 'Forecast', value: data.forecast || 'Stable' }
//           ],
//           alerts: data.alerts || []
//         };


//       case 'finance':
        
//         return {
//           title: 'Financial Markets',
//           currentValue: data.market_trend ? `Market: ${data.market_trend}` : 'No data',
//           change: data.average_change ? `${data.average_change > 0 ? '+' : ''}${data.average_change}%` : '0%',
//           trend: data.market_trend === 'bullish' ? 'up' : data.market_trend === 'bearish' ? 'down' : 'stable',
//           chartData: data.chart_data || data.chartData || [],
//           metrics: [
//             { label: 'Total Stocks', value: data.total_stocks || 0 },
//             { label: 'Advancing', value: data.advancing_stocks || 0 },
//             { label: 'Declining', value: data.declining_stocks || 0 },
//             { label: 'Avg Change', value: data.average_change ? `${data.average_change > 0 ? '+' : ''}${data.average_change}%` : '0%' }
//           ],
//           topGainers: data.top_gainers || [],
//           topLosers: data.top_losers || [],
//           allStocks: data.all_stocks || [], // This was missing!
//           marketSummary: data.market_summary || 'Market data unavailable',
//           alerts: data.alerts || []
//         };
            
//       default:
//         return {
//           title: sector.charAt(0).toUpperCase() + sector.slice(1),
//           currentValue: 'Data available',
//           change: 'N/A',
//           trend: 'stable',
//           chartData: data.chart_data || data.chartData || [],
//           metrics: [
//             { label: 'Status', value: 'Data loaded' },
//             { label: 'Type', value: typeof data === 'object' ? 'Object data' : 'Other' }
//           ]
//         };
//     }
//   };

//   const displayData = getSectorDisplayData(sector, data);
//   console.log(`Display data for ${sector}:`, displayData);

//   // Prepare chart data - handle different data structures
//   const chartData = displayData.chartData.map(item => ({
//     ...item,
//     // value: item.delay_minutes || item.temperature || item.value || 0
//     value: item.delay_minutes || item.temperature || item.price || item.value || 0
//   }));

//   // Function to get status color
//   const getStatusColor = (status) => {
//     if (status === 'Good Service') return 'success';
//     if (status === 'Minor Delays') return 'warning';
//     if (status === 'Reduced Service') return 'warning';
//     if (status === 'Part Closure') return 'error';
//     if (status === 'Planned Closure') return 'error';
//     return 'default';
//   };

//   // Function to get condition icon
//   const getConditionIcon = (status) => {
//     if (status === 'Good Service') return '✅';
//     if (status === 'Minor Delays') return '⚠️';
//     if (status === 'Reduced Service') return '📉';
//     if (status === 'Part Closure') return '🚧';
//     if (status === 'Planned Closure') return '🔒';
//     return '❓';
//   };

//   return (
//     <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
//       <CardContent sx={{ flexGrow: 1 }}>
//         <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
//           <Typography variant="h6" component="div">
//             {displayData.title}
//           </Typography>
//           <Chip 
//             label={displayData.trend} 
//             color={
//               displayData.trend === 'up' ? 'error' : 
//               displayData.trend === 'down' ? 'success' : 
//               'default'
//             } 
//             size="small" 
//           />
//         </Box>
        
//         {/* Chart */}
//         {chartData.length > 0 && chartData.some(item => item.value !== undefined && item.value !== null) ? (
//           <ResponsiveContainer width="100%" height={120}>
//             <LineChart data={chartData}>
//               <CartesianGrid strokeDasharray="3 3" />
//               <XAxis 
//                 dataKey="timestamp" 
//                 tick={{ fontSize: 10 }}
//                 tickFormatter={(value) => {
//                   try {
//                     const date = new Date(value);
//                     return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
//                   } catch {
//                     return 'Time';
//                   }
//                 }}
//               />
//               <YAxis />
//               <Tooltip 
//                 formatter={(value, name) => {
//                   if (sector.toLowerCase() === 'transportation') {
//                     return [`${value} min`, 'Delay'];
//                   } else if (sector.toLowerCase() === 'weather') {
//                     return [`${value}°C`, 'Temperature'];
//                   } else if (sector.toLowerCase() === 'finance') {
//                   return [`£${value}`, 'Price'];
//                 }
//                   return [value, name];
//                 }}
//                 labelFormatter={(label) => `Time: ${new Date(label).toLocaleTimeString()}`}
//               />
//               <Line 
//                 type="monotone" 
//                 dataKey="value" 
//                 stroke="#00b4d8" 
//                 strokeWidth={2} 
//                 dot={{ r: 2 }}
//               />
//             </LineChart>
//           </ResponsiveContainer>
//         ) : (
//           <Box sx={{ 
//             height: 120, 
//             display: 'flex', 
//             alignItems: 'center', 
//             justifyContent: 'center', 
//             bgcolor: 'grey.50',
//             borderRadius: 1
//           }}>
//             <Typography variant="body2" color="text.secondary">
//               No chart data available
//             </Typography>
//           </Box>
//         )}
        
//         {/* Metrics */}
//         <Grid container spacing={1} sx={{ mt: 2 }}>
//           {displayData.metrics.map((metric, index) => (
//             <Grid item xs={6} key={index}>
//               <Typography variant="caption" color="text.secondary" display="block">
//                 {metric.label}
//               </Typography>
//               <Typography variant="body2" fontWeight="bold">
//                 {metric.value}
//               </Typography>
//             </Grid>
//           ))}
//         </Grid>

//         {/* Service Breakdown for Transportation */}
//         {sector.toLowerCase() === 'transportation' && displayData.serviceBreakdown && (
//           <Box sx={{ mt: 2 }}>
//             <Typography variant="subtitle2" gutterBottom>
//               Service Breakdown:
//             </Typography>
//             <Grid container spacing={1} sx={{ mb: 1 }}>
//               {Object.entries(displayData.serviceBreakdown).map(([status, count]) => (
//                 <Grid item xs={6} key={status}>
//                   <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
//                     <Chip 
//                       label={count} 
//                       size="small" 
//                       color={getStatusColor(status)}
//                       variant="outlined"
//                     />
//                     <Typography variant="caption" color="text.secondary">
//                       {status}
//                     </Typography>
//                   </Box>
//                 </Grid>
//               ))}
//             </Grid>
//           </Box>
//         )}

//         {/* All Services Categorized */}
//         {sector.toLowerCase() === 'transportation' && displayData.allServices && displayData.allServices.length > 0 && (
//           <Box sx={{ mt: 2 }}>
//             <Typography variant="subtitle2" gutterBottom>
//               All Services ({displayData.allServices.length}):
//             </Typography>
            
//             {/* Good Services */}
//             {displayData.goodServices.length > 0 && (
//               <Box sx={{ mb: 1 }}>
//                 <Typography variant="caption" color="success.main" fontWeight="bold">
//                   ✅ Good Service ({displayData.goodServices.length})
//                 </Typography>
//                 <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
//                   {displayData.goodServices.map((service, index) => (
//                     <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
//                       <ListItemText 
//                         primary={
//                           <Typography variant="body2" fontSize="0.75rem">
//                             {service.line}
//                           </Typography>
//                         }
//                         secondary={
//                           service.delay > 0 && (
//                             <Typography variant="caption" color="text.secondary">
//                               {service.delay} min
//                             </Typography>
//                           )
//                         }
//                       />
//                     </ListItem>
//                   ))}
//                 </List>
//               </Box>
//             )}

//             {/* Moderate Services */}
//             {displayData.moderateServices.length > 0 && (
//               <Box sx={{ mb: 1 }}>
//                 <Typography variant="caption" color="warning.main" fontWeight="bold">
//                   ⚠️ Moderate Issues ({displayData.moderateServices.length})
//                 </Typography>
//                 <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
//                   {displayData.moderateServices.map((service, index) => (
//                     <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
//                       <ListItemText 
//                         primary={
//                           <Typography variant="body2" fontSize="0.75rem">
//                             {service.line}
//                           </Typography>
//                         }
//                         secondary={
//                           <Box>
//                             <Typography variant="caption" display="block">
//                               {service.status}
//                             </Typography>
//                             {service.delay > 0 && (
//                               <Typography variant="caption" color="text.secondary">
//                                 {service.delay} min delay
//                               </Typography>
//                             )}
//                           </Box>
//                         }
//                       />
//                     </ListItem>
//                   ))}
//                 </List>
//               </Box>
//             )}

//             {/* Poor Services */}
//             {displayData.poorServices.length > 0 && (
//               <Box sx={{ mb: 1 }}>
//                 <Typography variant="caption" color="error.main" fontWeight="bold">
//                   🚧 Poor Service ({displayData.poorServices.length})
//                 </Typography>
//                 <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
//                   {displayData.poorServices.map((service, index) => (
//                     <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
//                       <ListItemText 
//                         primary={
//                           <Typography variant="body2" fontSize="0.75rem">
//                             {service.line}
//                           </Typography>
//                         }
//                         secondary={
//                           <Box>
//                             <Typography variant="caption" display="block">
//                               {service.status}
//                             </Typography>
//                             {service.delay > 0 && (
//                               <Typography variant="caption" color="text.secondary">
//                                 {service.delay} min delay
//                               </Typography>
//                             )}
//                             {service.reason && service.reason !== 'No reason provided' && (
//                               <Typography variant="caption" color="text.secondary" display="block">
//                                 {service.reason.substring(0, 40)}...
//                               </Typography>
//                             )}
//                           </Box>
//                         }
//                       />
//                     </ListItem>
//                   ))}
//                 </List>
//               </Box>
//             )}
//           </Box>
//         )}

//         {/* Alerts for Weather */}
//         {sector.toLowerCase() === 'weather' && displayData.alerts && displayData.alerts.length > 0 && (
//           <Box sx={{ mt: 2 }}>
//             <Typography variant="subtitle2" gutterBottom>
//               Weather Alerts:
//             </Typography>
//             <List dense sx={{ maxHeight: 100, overflow: 'auto' }}>
//               {displayData.alerts.slice(0, 3).map((alert, index) => (
//                 <ListItem key={index} sx={{ py: 0.5 }}>
//                   <ListItemText 
//                     primary={alert.message || 'Alert'}
//                     secondary={`Severity: ${alert.severity || 'info'}`}
//                   />
//                 </ListItem>
//               ))}
//             </List>
//           </Box>
//         )}


               


// {/* Financial Market Data */}
// {sector.toLowerCase() === 'finance' && (
//   <Box sx={{ mt: 2 }}>
//     {/* Market Summary */}
//     <Typography variant="subtitle2" gutterBottom>
//       Market Summary:
//     </Typography>
//     <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
//       {displayData.marketSummary}
//     </Typography>

//     {/* All Companies Ranking */}
//     {displayData.allStocks && displayData.allStocks.length > 0 && (
//       <Box sx={{ mb: 2 }}>
//         <Typography variant="subtitle2" gutterBottom>
//           📊 All Companies ({displayData.allStocks.length}):
//         </Typography>
//         <List dense sx={{ maxHeight: 120, overflow: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
//           {displayData.allStocks.map((stock, index) => (
//             <ListItem 
//               key={index} 
//               sx={{ 
//                 py: 0.5, 
//                 pl: 1,
//                 borderBottom: index < displayData.allStocks.length - 1 ? '1px solid' : 'none',
//                 borderColor: 'divider'
//               }}
//             >
//               <ListItemText 
//                 primary={
//                   <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
//                     <Typography variant="body2" fontSize="0.75rem" fontWeight="medium">
//                       {stock.symbol}
//                     </Typography>
//                     <Chip 
//                       label={`${stock.change_percent > 0 ? '+' : ''}${stock.change_percent?.toFixed(2)}%`}
//                       size="small"
//                       color={stock.change_percent > 0 ? 'success' : stock.change_percent < 0 ? 'error' : 'default'}
//                       variant="outlined"
//                     />
//                   </Box>
//                 }
//                 secondary={
//                   <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
//                     <Typography variant="caption" color="text.secondary">
//                       {stock.company}
//                     </Typography>
//                     <Typography variant="caption" fontWeight="bold">
//                       £{stock.current_price?.toFixed(2)}
//                     </Typography>
//                   </Box>
//                 }
//               />
//             </ListItem>
//           ))}
//         </List>
//       </Box>
//     )}


//     {/* Performance Summary */}
//   <Grid container spacing={1} sx={{ mb: 2 }}>
//     <Grid item xs={6}>
//       <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'success.light', borderRadius: 1 }}>
//         <Typography variant="caption" display="block" fontWeight="bold" color="success.dark">
//           Advancing
//         </Typography>
//         <Typography variant="h6" color="success.dark">
//           {displayData.advancing_stocks } {/* Change to advancing_stocks */}
//         </Typography>
//       </Box>
//     </Grid>
//     <Grid item xs={6}>
//       <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
//         <Typography variant="caption" display="block" fontWeight="bold" color="error.dark">
//           Declining
//         </Typography>
//         <Typography variant="h6" color="error.dark">
//           {displayData.declining_stocks } {/* Change to declining_stocks */}
//         </Typography>
//       </Box>
//     </Grid>
//   </Grid>

//     {/* Top Gainers & Losers Side by Side */}
//     <Grid container spacing={1} sx={{ mb: 2 }}>
//       {/* Top Gainers */}
//       <Grid item xs={6}>
//         <Box sx={{ border: '1px solid', borderColor: 'success.light', borderRadius: 1, p: 1 }}>
//           <Typography variant="caption" color="success.main" fontWeight="bold" display="block" textAlign="center">
//             📈 Top Gainers
//           </Typography>
//           <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
//             {displayData.topGainers && displayData.topGainers.map((stock, index) => (
//               <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
//                 <ListItemText 
//                   primary={
//                     <Typography variant="body2" fontSize="0.7rem" fontWeight="medium">
//                       {stock.symbol}
//                     </Typography>
//                   }
//                   secondary={
//                     <Typography variant="caption" color="success.main">
//                       +{stock.change_percent?.toFixed(2)}%
//                     </Typography>
//                   }
//                 />
//               </ListItem>
//             ))}
//           </List>
//         </Box>
//       </Grid>

//       {/* Top Losers */}
//       <Grid item xs={6}>
//         <Box sx={{ border: '1px solid', borderColor: 'error.light', borderRadius: 1, p: 1 }}>
//           <Typography variant="caption" color="error.main" fontWeight="bold" display="block" textAlign="center">
//             📉 Top Losers
//           </Typography>
//           <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
//             {displayData.topLosers && displayData.topLosers.map((stock, index) => (
//               <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
//                 <ListItemText 
//                   primary={
//                     <Typography variant="body2" fontSize="0.7rem" fontWeight="medium">
//                       {stock.symbol}
//                     </Typography>
//                   }
//                   secondary={
//                     <Typography variant="caption" color="error.main">
//                       {stock.change_percent?.toFixed(2)}%
//                     </Typography>
//                   }
//                 />
//               </ListItem>
//             ))}
//           </List>
//         </Box>
//       </Grid>
//     </Grid>

//     {/* Financial Alerts */}
//     {displayData.alerts && displayData.alerts.length > 0 && (
//       <Box sx={{ mt: 1 }}>
//         <Typography variant="subtitle2" gutterBottom>
//           Market Alerts:
//         </Typography>
//         <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
//           {displayData.alerts.slice(0, 2).map((alert, index) => (
//             <ListItem key={index} sx={{ py: 0.5 }}>
//               <ListItemText 
//                 primary={alert.message || 'Alert'}
//                 secondary={`Type: ${alert.type || 'info'}`}
//               />
//             </ListItem>
//           ))}
//         </List>
//       </Box>
//     )}
//   </Box>
// )}

//       </CardContent>
//     </Card>
//   );
// };

// export default Dashboard;
















import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Alert,
  Button,
  Paper,
  Tabs,
  Tab,
} from '@mui/material';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
  ComposedChart
} from 'recharts';
import { dashboardService } from '../services/api';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [trendLoading, setTrendLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dashboardService.getOverview();
      
      let actualData;
      if (response.data && response.data.data) {
        actualData = response.data.data;
      } else if (response.data && (response.data.transportation || response.data.weather)) {
        actualData = response.data;
      } else {
        actualData = response.data || {};
      }
      
      setDashboardData(actualData);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const loadTrendData = async () => {
    try {
      setTrendLoading(true);
      const response = await dashboardService.getFinancialTrends();
      setTrendData(response.data);
    } catch (error) {
      console.error('Error loading trend data:', error);
    } finally {
      setTrendLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    loadTrendData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2 }}>Loading dashboard data...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={loadDashboardData}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          No dashboard data available. Please check your backend connection.
        </Alert>
      </Box>
    );
  }

  // Extract sectors and prioritize key ones
  const sectors = Object.keys(dashboardData).filter(key => 
    !['last_updated', 'summary', 'status', 'timestamp'].includes(key)
  );

  // Define priority sectors for the top section
  const prioritySectors = ['finance', 'transportation', 'weather'];
  const prioritySectorData = prioritySectors
    .filter(sector => sectors.includes(sector))
    .map(sector => ({
      name: sector,
      data: dashboardData[sector]
    }));

  // Other sectors for the bottom section
  const otherSectors = sectors.filter(sector => !prioritySectors.includes(sector));

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Universal MCP Platform Dashboard
        </Typography>
        <Box>
          <Button variant="outlined" onClick={loadDashboardData} sx={{ mr: 1 }}>
            Refresh Dashboard
          </Button>
          <Button variant="outlined" onClick={loadTrendData}>
            Refresh Trends
          </Button>
        </Box>
      </Box>
      
      {dashboardData.last_updated && (
        <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
          Last updated: {new Date(dashboardData.last_updated).toLocaleString()}
        </Typography>
      )}
      
      {/* Summary Section */}
      {dashboardData.summary && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Business Summary</Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              {dashboardData.summary.market_outlook || 'Market outlook analysis'}
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Opportunities</Typography>
                <List dense>
                  {dashboardData.summary.key_opportunities?.map((opp, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={opp} />
                    </ListItem>
                  ))}
                </List>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Risks</Typography>
                <List dense>
                  {dashboardData.summary.risk_factors?.map((risk, index) => (
                    <ListItem key={index}>
                      <ListItemText primary={risk} />
                    </ListItem>
                  ))}
                </List>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

  // Update the Centralized Priority Cards Section - CENTERED
  <Box sx={{ mb: 4 }}>
    <Typography variant="h5" gutterBottom sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      mb: 3,
      color: 'primary.main',
      fontWeight: 'bold',
      textAlign: 'center', // Center the title
      justifyContent: 'center' // Center the title
    }}>
      🎯 Key Metrics Overview
    </Typography>
    
    <Grid container spacing={3} justifyContent="center"> {/* Added justifyContent="center" */}
      {prioritySectorData.map(({ name, data }) => (
        <Grid item xs={12} md={4} key={name} sx={{ display: 'flex', justifyContent: 'center' }}>
          <Box sx={{ width: '100%', maxWidth: 400 }}> {/* Constrain max width for better centering */}
            <SectorCard sector={name} data={data} />
          </Box>
        </Grid>
      ))}
    </Grid>
  </Box>


      {/* Financial Trend Analysis Section - Placed Below Priority Cards */}
      <FinancialTrendSection 
        trendData={trendData} 
        loading={trendLoading}
        onRefresh={loadTrendData}
      />

      {/* Other Sectors Section */}
      {otherSectors.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom sx={{ 
            display: 'flex', 
            alignItems: 'center',
            mb: 3,
            color: 'text.secondary'
          }}>
            📊 Additional Metrics
          </Typography>
          
          <Grid container spacing={3}>
            {otherSectors.map((sector) => {
              const sectorData = dashboardData[sector];
              return (
                <Grid item xs={12} md={6} lg={4} key={sector}>
                  <SectorCard sector={sector} data={sectorData} />
                </Grid>
              );
            })}
          </Grid>
        </Box>
      )}
    </Box>
  );
};



// Update the Financial Trend Section to be wider
const FinancialTrendSection = ({ trendData, loading, onRefresh }) => {
  const [selectedTab, setSelectedTab] = useState(0);

  if (loading) {
    return (
      <Paper sx={{ p: 3, mb: 3, mt: 2, width: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" sx={{ color: 'secondary.main', fontWeight: 'bold' }}>
            📈 Financial Trend Analysis
          </Typography>
          <Button variant="outlined" size="small" disabled>
            Loading...
          </Button>
        </Box>
        <LinearProgress />
      </Paper>
    );
  }

  if (!trendData) {
    return (
      <Paper sx={{ p: 3, mb: 3, mt: 2, width: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h5" sx={{ color: 'secondary.main', fontWeight: 'bold' }}>
            📈 Financial Trend Analysis
          </Typography>
          <Button variant="outlined" size="small" onClick={onRefresh}>
            Load Trends
          </Button>
        </Box>
        <Alert severity="info">
          Trend data not available. Click "Load Trends" to fetch historical analysis.
        </Alert>
      </Paper>
    );
  }

  const trendDataContent = trendData.data || {};

  return (
    <Paper sx={{ 
      p: 3, 
      mb: 3, 
      mt: 2, 
      bgcolor: 'background.default',
      width: '100%',
      maxWidth: '100%'
    }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ color: 'secondary.main', fontWeight: 'bold' }}>
          📈 Financial Trend Analysis
        </Typography>
        <Button variant="outlined" size="small" onClick={onRefresh}>
          Refresh Trends
        </Button>
      </Box>

      <Tabs 
        value={selectedTab} 
        onChange={(e, newValue) => setSelectedTab(newValue)} 
        sx={{ 
          mb: 3,
          borderBottom: 1,
          borderColor: 'divider',
          width: '100%'
        }}
        indicatorColor="secondary"
        textColor="secondary"
      >
        <Tab label="Market Overview" />
        <Tab label="Stock Performance" />
        <Tab label="Historical Trends" />
        <Tab label="Sector Analysis" />
      </Tabs>

      {/* Make the tab content container wider */}
      <Box sx={{ width: '100%', maxWidth: '100%' }}>
        {selectedTab === 0 && <MarketOverviewTab data={trendDataContent} />}
        {selectedTab === 1 && <StockPerformanceTab data={trendDataContent} />}
        {selectedTab === 2 && <HistoricalTrendsTab data={trendDataContent} />}
        {selectedTab === 3 && <SectorAnalysisTab data={trendDataContent} />}
      </Box>
    </Paper>
  );
};



// MarketOverviewTab - FIXED FULL WIDTH
const MarketOverviewTab = ({ data }) => {
  const chartData = data.market_trends?.map(trend => ({
    date: trend.date,
    price: trend.price,
    volume: trend.volume,
    price_change: trend.price_change,
    stocks_traded: trend.stocks_traded
  })) || [];

  return (
    <Box sx={{ width: '100%' }}>
      {/* Main Chart - Full Width */}
      <Card elevation={2} sx={{ width: '100%', mb: 3 }}>
        <CardContent sx={{ width: '100%' }}>
          <Typography variant="h6" gutterBottom color="primary">
            Market Trend ({chartData.length} Days)
          </Typography>
          {chartData.length > 0 ? (
            <Box sx={{ width: '100%', height: 500 }}>
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart 
                  data={chartData}
                  margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => {
                      const date = new Date(value);
                      return date.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric' 
                      });
                    }}
                    interval={0}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis 
                    yAxisId="left"
                    tick={{ fontSize: 12 }}
                    width={60}
                  />
                  <YAxis 
                    yAxisId="right"
                    orientation="right"
                    tick={{ fontSize: 12 }}
                    width={80}
                  />
                  <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'price') return [`£${value}`, 'Market Average'];
                      if (name === 'volume') return [`${(value / 1000000).toFixed(1)}M`, 'Volume'];
                      if (name === 'price_change') return [`${value}%`, 'Daily Change'];
                      return [value, name];
                    }}
                    labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                  />
                  <Area 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="price" 
                    fill="#8884d8" 
                    stroke="#8884d8" 
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                  <Bar 
                    yAxisId="right"
                    dataKey="volume" 
                    fill="#82ca9d" 
                    opacity={0.7}
                    barSize={40}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </Box>
          ) : (
            <Box sx={{ height: 500, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography color="text.secondary">No market trend data available</Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Metrics - Full Width Grid */}
      <Grid container spacing={2} sx={{ width: '100%' }}>
        <Grid item xs={12} md={6}>
          <Card elevation={2} sx={{ width: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                Performance Metrics
              </Typography>
              {data.performance_metrics?.map((metric, index) => (
                <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="body1" color="text.secondary">
                    {metric.name}:
                  </Typography>
                  <Chip 
                    label={metric.value} 
                    size="medium"
                    color={metric.value.includes('+') ? 'success' : metric.value.includes('-') ? 'error' : 'default'}
                    variant="outlined"
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card elevation={2} sx={{ width: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom color="primary">
                Trend Indicators
              </Typography>
              {data.trend_indicators?.map((indicator, index) => (
                <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body1" color="text.secondary">
                    {indicator.name}
                  </Typography>
                  <Chip 
                    label={indicator.status} 
                    size="medium"
                    color={indicator.status === 'Bullish' ? 'success' : indicator.status === 'Bearish' ? 'error' : 'default'}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};


const StockPerformanceTab = ({ data }) => {
  const stockData = data.stock_performance || [];
  
  return (
    <Box sx={{ width: '100%' }}>
      <Card elevation={2} sx={{ width: '100%' }}>
        <CardContent sx={{ width: '100%' }}>
          <Typography variant="h6" gutterBottom color="primary">
            Stock Performance ({stockData.length} Stocks)
          </Typography>
          {stockData.length > 0 ? (
            <Box sx={{ width: '100%', height: 500 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={stockData}
                  layout="vertical"
                  margin={{ top: 20, right: 30, left: 120, bottom: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis 
                    type="number" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <YAxis 
                    type="category" 
                    dataKey="symbol"
                    tick={{ fontSize: 12 }}
                    width={100}
                  />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Change']}
                    labelFormatter={(label) => `Symbol: ${label}`}
                  />
                  <Bar 
                    dataKey="change" 
                    fill={(entry) => entry.change >= 0 ? '#4caf50' : '#f44336'}
                    radius={[0, 4, 4, 0]}
                    barSize={30}
                  />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          ) : (
            <Box sx={{ height: 500, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Typography color="text.secondary">No stock performance data available</Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};


// HistoricalTrendsTab - FIXED VERSION
const HistoricalTrendsTab = ({ data }) => {
  const volatilityData = data.volatility_data || [];
  const movingAverages = data.moving_averages || [];
  
  return (
    <Box sx={{ width: '100%' }}>
      <Grid container spacing={3} sx={{ width: '100%' }}>
        {/* Volatility Chart */}
        <Grid item xs={12} lg={6}>
          <Card elevation={2} sx={{ width: '100%', height: '100%' }}>
            <CardContent sx={{ width: '100%', height: '100%' }}>
              <Typography variant="h6" gutterBottom color="primary">
                Volatility Analysis
              </Typography>
              {volatilityData.length > 0 ? (
                <Box sx={{ width: '100%', height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={volatilityData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="date"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => {
                          const date = new Date(value);
                          return date.toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric' 
                          });
                        }}
                        interval={0}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis 
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => `${value}%`}
                        width={60}
                      />
                      <Tooltip 
                        formatter={(value) => [`${value}%`, 'Volatility']}
                        labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="volatility" 
                        stroke="#ff6b6b" 
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography color="text.secondary">No volatility data available</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Moving Averages Chart */}
        <Grid item xs={12} lg={6}>
          <Card elevation={2} sx={{ width: '100%', height: '100%' }}>
            <CardContent sx={{ width: '100%', height: '100%' }}>
              <Typography variant="h6" gutterBottom color="primary">
                Moving Averages
              </Typography>
              {movingAverages.length > 0 ? (
                <Box sx={{ width: '100%', height: 400 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={movingAverages}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="date"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => {
                          const date = new Date(value);
                          return date.toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric' 
                          });
                        }}
                        interval={0}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis 
                        tick={{ fontSize: 12 }}
                        width={60}
                      />
                      <Tooltip 
                        formatter={(value, name) => {
                          if (name === 'price') return [`£${value}`, 'Price'];
                          if (name === 'price_7d') return [`£${value}`, '7-Day MA'];
                          if (name === 'price_30d') return [`£${value}`, '30-Day MA'];
                          return [value, name];
                        }}
                        labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="price" 
                        stroke="#8884d8" 
                        strokeWidth={2}
                        dot={{ r: 3 }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="price_7d" 
                        stroke="#4ecdc4" 
                        strokeWidth={2}
                        dot={false}
                        strokeDasharray="3 3"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="price_30d" 
                        stroke="#45b7d1" 
                        strokeWidth={2}
                        dot={false}
                        strokeDasharray="5 5"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography color="text.secondary">No moving average data available</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};


// SectorAnalysisTab - FIXED VERSION
const SectorAnalysisTab = ({ data }) => {
  const sectorPerformance = data.sector_performance || [];
  const sectorRankings = data.sector_rankings || [];
  
  return (
    <Box sx={{ width: '100%' }}>
      <Grid container spacing={3} sx={{ width: '100%' }}>
        {/* Sector Performance Chart */}
        <Grid item xs={12} lg={8}>
          <Card elevation={2} sx={{ width: '100%' }}>
            <CardContent sx={{ width: '100%' }}>
              <Typography variant="h6" gutterBottom color="primary">
                Sector Performance ({sectorPerformance.length} Sectors)
              </Typography>
              {sectorPerformance.length > 0 ? (
                <Box sx={{ width: '100%', height: 500 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={sectorPerformance}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="sector" 
                        tick={{ fontSize: 12 }}
                        angle={-45}
                        textAnchor="end"
                        height={100}
                      />
                      <YAxis 
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => `${value}%`}
                      />
                      <Tooltip 
                        formatter={(value) => [`${value}%`, 'Performance']}
                        labelFormatter={(label) => `Sector: ${label}`}
                      />
                      <Bar 
                        dataKey="performance" 
                        fill={(entry) => entry.performance >= 0 ? '#4caf50' : '#f44336'}
                        radius={[4, 4, 0, 0]}
                        barSize={50}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ height: 500, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography color="text.secondary">No sector performance data available</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Sector Rankings */}
        <Grid item xs={12} lg={4}>
          <Card elevation={2} sx={{ width: '100%', height: '100%' }}>
            <CardContent sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="h6" gutterBottom color="primary">
                Sector Rankings
              </Typography>
              {sectorRankings.length > 0 ? (
                <Box sx={{ flexGrow: 1, maxHeight: 500, overflow: 'auto' }}>
                  <List dense>
                    {sectorRankings.map((sector, index) => (
                      <ListItem key={index} sx={{ py: 1.5 }}>
                        <ListItemText 
                          primary={<Typography variant="body2" fontWeight="medium">{sector.name}</Typography>}
                          secondary={`${sector.change}% • ${sector.trend}`}
                        />
                        <Chip 
                          label={`#${index + 1}`}
                          size="small"
                          color={index === 0 ? 'success' : index === 1 ? 'primary' : index === 2 ? 'secondary' : 'default'}
                          variant={index < 3 ? "filled" : "outlined"}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              ) : (
                <Typography color="text.secondary" sx={{ py: 2 }}>
                  No sector rankings available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

// Keep your existing SectorCard component exactly as is
const SectorCard = ({ sector, data }) => {
  console.log(`Rendering ${sector} card with data:`, data);

  if (!data) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Typography variant="h6" component="div">
            {sector.charAt(0).toUpperCase() + sector.slice(1)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            No data available
          </Typography>
        </CardContent>
      </Card>
    );
  }

  // Handle different data structures for different sectors
  const getSectorDisplayData = (sector, data) => {
    console.log(`Processing ${sector} data:`, data);
    
    const sectorLower = sector.toLowerCase();
    
    switch (sectorLower) {
      case 'transportation':
        // Categorize services by condition
        const allServices = data.major_issues || data.majorIssues || [];
        const serviceBreakdown = data.service_breakdown || {};
        
        // Categorize services
        const goodServices = allServices.filter(service => 
          service.status === 'Good Service' || service.type === 'good_service'
        );
        
        const moderateServices = allServices.filter(service => 
          service.status === 'Minor Delays' || 
          service.status === 'Reduced Service' ||
          service.type === 'minor_delay' ||
          service.type === 'reduced_service'
        );
        
        const poorServices = allServices.filter(service => 
          service.status === 'Part Closure' || 
          service.status === 'Planned Closure' ||
          service.type === 'part_closure' ||
          service.type === 'suspended'
        );

        return {
          title: 'Transportation',
          currentValue: `${data.delayed_lines || 0}/${data.total_lines || 0} lines delayed`,
          change: data.delay_percentage ? `${data.delay_percentage}%` : '0%',
          trend: data.trend || 'stable',
          chartData: data.chart_data || data.chartData || [],
          metrics: [
            { label: 'Total Lines', value: data.total_lines || 0 },
            { label: 'Delayed Lines', value: data.delayed_lines || 0 },
            { label: 'Delay %', value: data.delay_percentage ? `${data.delay_percentage}%` : '0%' }
          ],
          allServices: allServices,
          goodServices: goodServices,
          moderateServices: moderateServices,
          poorServices: poorServices,
          serviceBreakdown: serviceBreakdown
        };
      
      case 'weather':
        // Enhanced weather data handling
        const hasWeatherData = data.current_temp !== undefined;
        return {
          title: 'Weather',
          currentValue: hasWeatherData ? `${data.current_temp || 0}°C` : 'No data',
          change: data.condition || 'Unknown',
          trend: data.trend || 'stable',
          chartData: data.chart_data || data.chartData || [],
          metrics: [
            { label: 'Temperature', value: hasWeatherData ? `${data.current_temp || 0}°C` : 'N/A' },
            { label: 'Humidity', value: data.humidity ? `${data.humidity}%` : 'N/A' },
            { label: 'Condition', value: data.condition || 'Unknown' },
            { label: 'Forecast', value: data.forecast || 'Stable' }
          ],
          alerts: data.alerts || []
        };


      case 'finance':
        
        return {
          title: 'Financial Markets',
          currentValue: data.market_trend ? `Market: ${data.market_trend}` : 'No data',
          change: data.average_change ? `${data.average_change > 0 ? '+' : ''}${data.average_change}%` : '0%',
          trend: data.market_trend === 'bullish' ? 'up' : data.market_trend === 'bearish' ? 'down' : 'stable',
          chartData: data.chart_data || data.chartData || [],
          metrics: [
            { label: 'Total Stocks', value: data.total_stocks || 0 },
            { label: 'Advancing', value: data.advancing_stocks || 0 },
            { label: 'Declining', value: data.declining_stocks || 0 },
            { label: 'Avg Change', value: data.average_change ? `${data.average_change > 0 ? '+' : ''}${data.average_change}%` : '0%' }
          ],
          topGainers: data.top_gainers || [],
          topLosers: data.top_losers || [],
          allStocks: data.all_stocks || [], // This was missing!
          marketSummary: data.market_summary || 'Market data unavailable',
          alerts: data.alerts || []
        };
            
      default:
        return {
          title: sector.charAt(0).toUpperCase() + sector.slice(1),
          currentValue: 'Data available',
          change: 'N/A',
          trend: 'stable',
          chartData: data.chart_data || data.chartData || [],
          metrics: [
            { label: 'Status', value: 'Data loaded' },
            { label: 'Type', value: typeof data === 'object' ? 'Object data' : 'Other' }
          ]
        };
    }
  };

  const displayData = getSectorDisplayData(sector, data);
  console.log(`Display data for ${sector}:`, displayData);

  // Prepare chart data - handle different data structures
  const chartData = displayData.chartData.map(item => ({
    ...item,
    // value: item.delay_minutes || item.temperature || item.value || 0
    value: item.delay_minutes || item.temperature || item.price || item.value || 0
  }));

  // Function to get status color
  const getStatusColor = (status) => {
    if (status === 'Good Service') return 'success';
    if (status === 'Minor Delays') return 'warning';
    if (status === 'Reduced Service') return 'warning';
    if (status === 'Part Closure') return 'error';
    if (status === 'Planned Closure') return 'error';
    return 'default';
  };

  // Function to get condition icon
  const getConditionIcon = (status) => {
    if (status === 'Good Service') return '✅';
    if (status === 'Minor Delays') return '⚠️';
    if (status === 'Reduced Service') return '📉';
    if (status === 'Part Closure') return '🚧';
    if (status === 'Planned Closure') return '🔒';
    return '❓';
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" component="div">
            {displayData.title}
          </Typography>
          <Chip 
            label={displayData.trend} 
            color={
              displayData.trend === 'up' ? 'error' : 
              displayData.trend === 'down' ? 'success' : 
              'default'
            } 
            size="small" 
          />
        </Box>
        
        {/* Chart */}
        {chartData.length > 0 && chartData.some(item => item.value !== undefined && item.value !== null) ? (
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="timestamp" 
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => {
                  try {
                    const date = new Date(value);
                    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                  } catch {
                    return 'Time';
                  }
                }}
              />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => {
                  if (sector.toLowerCase() === 'transportation') {
                    return [`${value} min`, 'Delay'];
                  } else if (sector.toLowerCase() === 'weather') {
                    return [`${value}°C`, 'Temperature'];
                  } else if (sector.toLowerCase() === 'finance') {
                  return [`£${value}`, 'Price'];
                }
                  return [value, name];
                }}
                labelFormatter={(label) => `Time: ${new Date(label).toLocaleTimeString()}`}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#00b4d8" 
                strokeWidth={2} 
                dot={{ r: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <Box sx={{ 
            height: 120, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            bgcolor: 'grey.50',
            borderRadius: 1
          }}>
            <Typography variant="body2" color="text.secondary">
              No chart data available
            </Typography>
          </Box>
        )}
        
        {/* Metrics */}
        <Grid container spacing={1} sx={{ mt: 2 }}>
          {displayData.metrics.map((metric, index) => (
            <Grid item xs={6} key={index}>
              <Typography variant="caption" color="text.secondary" display="block">
                {metric.label}
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {metric.value}
              </Typography>
            </Grid>
          ))}
        </Grid>

        {/* Service Breakdown for Transportation */}
        {sector.toLowerCase() === 'transportation' && displayData.serviceBreakdown && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Service Breakdown:
            </Typography>
            <Grid container spacing={1} sx={{ mb: 1 }}>
              {Object.entries(displayData.serviceBreakdown).map(([status, count]) => (
                <Grid item xs={6} key={status}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Chip 
                      label={count} 
                      size="small" 
                      color={getStatusColor(status)}
                      variant="outlined"
                    />
                    <Typography variant="caption" color="text.secondary">
                      {status}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* All Services Categorized */}
        {sector.toLowerCase() === 'transportation' && displayData.allServices && displayData.allServices.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              All Services ({displayData.allServices.length}):
            </Typography>
            
            {/* Good Services */}
            {displayData.goodServices.length > 0 && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="caption" color="success.main" fontWeight="bold">
                  ✅ Good Service ({displayData.goodServices.length})
                </Typography>
                <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
                  {displayData.goodServices.map((service, index) => (
                    <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
                      <ListItemText 
                        primary={
                          <Typography variant="body2" fontSize="0.75rem">
                            {service.line}
                          </Typography>
                        }
                        secondary={
                          service.delay > 0 && (
                            <Typography variant="caption" color="text.secondary">
                              {service.delay} min
                            </Typography>
                          )
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Moderate Services */}
            {displayData.moderateServices.length > 0 && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="caption" color="warning.main" fontWeight="bold">
                  ⚠️ Moderate Issues ({displayData.moderateServices.length})
                </Typography>
                <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
                  {displayData.moderateServices.map((service, index) => (
                    <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
                      <ListItemText 
                        primary={
                          <Typography variant="body2" fontSize="0.75rem">
                            {service.line}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" display="block">
                              {service.status}
                            </Typography>
                            {service.delay > 0 && (
                              <Typography variant="caption" color="text.secondary">
                                {service.delay} min delay
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Poor Services */}
            {displayData.poorServices.length > 0 && (
              <Box sx={{ mb: 1 }}>
                <Typography variant="caption" color="error.main" fontWeight="bold">
                  🚧 Poor Service ({displayData.poorServices.length})
                </Typography>
                <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
                  {displayData.poorServices.map((service, index) => (
                    <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
                      <ListItemText 
                        primary={
                          <Typography variant="body2" fontSize="0.75rem">
                            {service.line}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" display="block">
                              {service.status}
                            </Typography>
                            {service.delay > 0 && (
                              <Typography variant="caption" color="text.secondary">
                                {service.delay} min delay
                              </Typography>
                            )}
                            {service.reason && service.reason !== 'No reason provided' && (
                              <Typography variant="caption" color="text.secondary" display="block">
                                {service.reason.substring(0, 40)}...
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Box>
        )}

        {/* Alerts for Weather */}
        {sector.toLowerCase() === 'weather' && displayData.alerts && displayData.alerts.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Weather Alerts:
            </Typography>
            <List dense sx={{ maxHeight: 100, overflow: 'auto' }}>
              {displayData.alerts.slice(0, 3).map((alert, index) => (
                <ListItem key={index} sx={{ py: 0.5 }}>
                  <ListItemText 
                    primary={alert.message || 'Alert'}
                    secondary={`Severity: ${alert.severity || 'info'}`}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}


               


{/* Financial Market Data */}
{sector.toLowerCase() === 'finance' && (
  <Box sx={{ mt: 2 }}>
    {/* Market Summary */}
    <Typography variant="subtitle2" gutterBottom>
      Market Summary:
    </Typography>
    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
      {displayData.marketSummary}
    </Typography>

    {/* All Companies Ranking */}
    {displayData.allStocks && displayData.allStocks.length > 0 && (
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          📊 All Companies ({displayData.allStocks.length}):
        </Typography>
        <List dense sx={{ maxHeight: 120, overflow: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
          {displayData.allStocks.map((stock, index) => (
            <ListItem 
              key={index} 
              sx={{ 
                py: 0.5, 
                pl: 1,
                borderBottom: index < displayData.allStocks.length - 1 ? '1px solid' : 'none',
                borderColor: 'divider'
              }}
            >
              <ListItemText 
                primary={
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" fontSize="0.75rem" fontWeight="medium">
                      {stock.symbol}
                    </Typography>
                    <Chip 
                      label={`${stock.change_percent > 0 ? '+' : ''}${stock.change_percent?.toFixed(2)}%`}
                      size="small"
                      color={stock.change_percent > 0 ? 'success' : stock.change_percent < 0 ? 'error' : 'default'}
                      variant="outlined"
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                    <Typography variant="caption" color="text.secondary">
                      {stock.company}
                    </Typography>
                    <Typography variant="caption" fontWeight="bold">
                      £{stock.current_price?.toFixed(2)}
                    </Typography>
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Box>
    )}


    {/* Performance Summary */}
  <Grid container spacing={1} sx={{ mb: 2 }}>
    <Grid item xs={6}>
      <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'success.light', borderRadius: 1 }}>
        <Typography variant="caption" display="block" fontWeight="bold" color="success.dark">
          Advancing
        </Typography>
        <Typography variant="h6" color="success.dark">
          {displayData.advancing_stocks } {/* Change to advancing_stocks */}
        </Typography>
      </Box>
    </Grid>
    <Grid item xs={6}>
      <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
        <Typography variant="caption" display="block" fontWeight="bold" color="error.dark">
          Declining
        </Typography>
        <Typography variant="h6" color="error.dark">
          {displayData.declining_stocks } {/* Change to declining_stocks */}
        </Typography>
      </Box>
    </Grid>
  </Grid>

    {/* Top Gainers & Losers Side by Side */}
    <Grid container spacing={1} sx={{ mb: 2 }}>
      {/* Top Gainers */}
      <Grid item xs={6}>
        <Box sx={{ border: '1px solid', borderColor: 'success.light', borderRadius: 1, p: 1 }}>
          <Typography variant="caption" color="success.main" fontWeight="bold" display="block" textAlign="center">
            📈 Top Gainers
          </Typography>
          <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
            {displayData.topGainers && displayData.topGainers.map((stock, index) => (
              <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
                <ListItemText 
                  primary={
                    <Typography variant="body2" fontSize="0.7rem" fontWeight="medium">
                      {stock.symbol}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" color="success.main">
                      +{stock.change_percent?.toFixed(2)}%
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Grid>

      {/* Top Losers */}
      <Grid item xs={6}>
        <Box sx={{ border: '1px solid', borderColor: 'error.light', borderRadius: 1, p: 1 }}>
          <Typography variant="caption" color="error.main" fontWeight="bold" display="block" textAlign="center">
            📉 Top Losers
          </Typography>
          <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
            {displayData.topLosers && displayData.topLosers.map((stock, index) => (
              <ListItem key={index} sx={{ py: 0.2, pl: 1 }}>
                <ListItemText 
                  primary={
                    <Typography variant="body2" fontSize="0.7rem" fontWeight="medium">
                      {stock.symbol}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" color="error.main">
                      {stock.change_percent?.toFixed(2)}%
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      </Grid>
    </Grid>

    {/* Financial Alerts */}
    {displayData.alerts && displayData.alerts.length > 0 && (
      <Box sx={{ mt: 1 }}>
        <Typography variant="subtitle2" gutterBottom>
          Market Alerts:
        </Typography>
        <List dense sx={{ maxHeight: 80, overflow: 'auto' }}>
          {displayData.alerts.slice(0, 2).map((alert, index) => (
            <ListItem key={index} sx={{ py: 0.5 }}>
              <ListItemText 
                primary={alert.message || 'Alert'}
                secondary={`Type: ${alert.type || 'info'}`}
              />
            </ListItem>
          ))}
        </List>
      </Box>
    )}
  </Box>
)}

      </CardContent>
    </Card>
  );
};

export default Dashboard;