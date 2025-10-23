


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
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [trendLoading, setTrendLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

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

  const handleMCPConfig = () => {
    navigate('/mcp-configuration');
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

      {/* Updated Header with MCP Configuration Button */}
<Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
  <Typography variant="h4">
    Universal MCP Platform Dashboard
  </Typography>
  <Box>
    <Button 
      variant="contained" 
      onClick={handleMCPConfig}
      sx={{ 
        mr: 1,
        backgroundColor: '#1976d2',
        '&:hover': {
          backgroundColor: '#1565c0',
        }
      }}
     
    >
      🔌 MCP Configuration
    </Button>
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
      
{/* Project Description Section */}
<Card sx={{ mb: 3, bgcolor: 'primary.50', border: 1, borderColor: 'primary.200' }}>
  <CardContent>
    <Typography variant="h5" gutterBottom color="primary.main" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      🚀 SmartMCP Platform Overview
    </Typography>
    
    <Typography variant="body1" paragraph sx={{ lineHeight: 1.6 }}>
      <strong>SmartMCP</strong> is a Universal Multi-Sector Data Analysis Platform that serves real-time data 
      from multiple UK sources, provide AI insights via prompts and MCP (Model Context Protocol) server capabilities for 
      external AI clients and applications.
    </Typography>

    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Typography variant="h6" gutterBottom color="secondary.main">
          📊 Data Sources
        </Typography>
        <List dense>
          <ListItem sx={{ px: 0 }}>
            <ListItemText 
              primary="🚇 TFL Transport API" 
              secondary="Real-time London transport status, delays, and service updates"
            />
          </ListItem>
          <ListItem sx={{ px: 0 }}>
            <ListItemText 
              primary="💹 Alphavantage Financial Data" 
              secondary="UK stock market data from FTSE 100 companies"
            />
          </ListItem>
          <ListItem sx={{ px: 0 }}>
            <ListItemText 
              primary="🌤️ Open-Meteo Weather API" 
              secondary="Current London weather conditions and forecasts"
            />
          </ListItem>
        </List>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Typography variant="h6" gutterBottom color="secondary.main">
          🔌 MCP Capabilities
        </Typography>
        <List dense>
          <ListItem sx={{ px: 0 }}>
            <ListItemText 
              primary="🤖 Standard MCP 1.0.0 Server" 
              secondary="Compatible with Claude Desktop and other MCP clients"
            />
          </ListItem>
          <ListItem sx={{ px: 0 }}>
            <ListItemText 
              primary="🛠️ 5+ Data Tools" 
              secondary="Transport, finance, weather, trends, and combined data"
            />
          </ListItem>
          <ListItem sx={{ px: 0 }}>
            <ListItemText 
              primary="🔐 Secure Authentication" 
              secondary="Bearer token authentication for API access"
            />
          </ListItem>
        </List>
      </Grid>
    </Grid>

    <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1, border: 1, borderColor: 'divider' }}>
      <Typography variant="subtitle2" gutterBottom color="primary.main">
        💡 How It Works
      </Typography>
      <Typography variant="body2" color="text.secondary">
        This dashboard displays real-time data analysis while the platform simultaneously serves the same data 
        to external MCP clients through standardized protocols. Click the <strong>"🔌 MCP Configuration"</strong> 
        button to set up external client connections.
      </Typography>
    </Box>
  </CardContent>
</Card>

      {/* Update the Centralized Priority Cards Section - CENTERED */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          mb: 3,
          color: 'primary.main',
          fontWeight: 'bold',
          textAlign: 'center',
          justifyContent: 'center'
        }}>
          🎯 Key Sectors Overview
        </Typography>
        
        <Grid container spacing={3} justifyContent="center">
          {prioritySectorData.map(({ name, data }) => (
            <Grid item xs={12} md={4} key={name} sx={{ display: 'flex', justifyContent: 'center' }}>
              <Box sx={{ width: '100%', maxWidth: 400 }}>
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
                  {/* <YAxis 
                    yAxisId="left"
                    tick={{ fontSize: 12 }}
                    width={60}
                  />
                  <YAxis 
                    yAxisId="right"
                    orientation="right"
                    tick={{ fontSize: 12 }}
                    width={80}
                  /> */}

                  <YAxis 
  yAxisId="left"
  tick={{ fontSize: 12 }}
  width={60}
  tickFormatter={(value) => `£${(value / 100).toFixed(2)}`} // FIXED
/>
<YAxis 
  yAxisId="right"
  orientation="right"
  tick={{ fontSize: 12 }}
  width={80}
  tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`} // Volume in millions
/>
                  {/* <Tooltip 
                    formatter={(value, name) => {
                      if (name === 'price') return [`£${value}`, 'Market Average'];
                      if (name === 'volume') return [`${(value / 1000000).toFixed(1)}M`, 'Volume'];
                      if (name === 'price_change') return [`${value}%`, 'Daily Change'];
                      return [value, name];
                    }}
                    labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
                  /> */}

                  <Tooltip 
  formatter={(value, name) => {
    if (name === 'price') return [`£${(value / 100).toFixed(2)}`, 'Market Average']; // FIXED
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
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        const stock = payload[0].payload;
                        return (
                          <Box sx={{ 
                            bgcolor: 'background.paper', 
                            p: 2, 
                            border: 1, 
                            borderColor: 'divider',
                            borderRadius: 1,
                            boxShadow: 3,
                            minWidth: 250
                          }}>
                            <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
                              {stock.company || stock.symbol}
                            </Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2">Symbol:</Typography>
                              <Typography variant="body2" fontWeight="bold">
                                {stock.symbol}
                              </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                              <Typography variant="body2">Performance:</Typography>
                              <Typography 
                                variant="body2" 
                                fontWeight="bold"
                                color={stock.change >= 0 ? 'success.main' : 'error.main'}
                              >
                                {stock.change}%
                              </Typography>
                            </Box>
                            {stock.volatility && (
                              <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                <Typography variant="body2">Volatility:</Typography>
                                <Typography variant="body2" fontWeight="bold">
                                  {stock.volatility}%
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        );
                      }
                      return null;
                    }}
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

// HistoricalTrendsTab - WIDER GRID VERSION
const HistoricalTrendsTab = ({ data }) => {
  const volatilityData = data.volatility_data || [];
  const movingAverages = data.moving_averages || [];

  return (
    <Box sx={{ width: '100%', maxWidth: '100%', overflow: 'hidden' }}>
      <Grid container spacing={2} sx={{ width: '100%', margin: 0 }}>
        {/* Volatility Chart - Wider */}
        <Grid item xs={12} lg={6} sx={{ 
          display: 'flex',
          padding: '8px !important', // Reduce padding to maximize space
          minWidth: { lg: '600px' } // Set minimum width
        }}>
          <Card elevation={2} sx={{ width: '100%', flex: 1 }}>
            <CardContent sx={{ width: '100%', p: 2 }}>
              <Typography variant="h6" gutterBottom color="primary">
                Volatility Analysis
              </Typography>
              {volatilityData.length > 0 ? (
                <Box sx={{ width: '100%', height: 350 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={volatilityData} margin={{ left: 0, right: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="date"
                        tick={{ fontSize: 10 }}
                        tickFormatter={(value) => {
                          try {
                            const date = new Date(value);
                            return date.toLocaleDateString('en-US', { 
                              month: 'short', 
                              day: 'numeric' 
                            });
                          } catch {
                            return value;
                          }
                        }}
                        interval={0}
                        angle={-30}
                        textAnchor="end"
                        height={50}
                      />
                      <YAxis 
                        tick={{ fontSize: 10 }}
                        tickFormatter={(value) => `${value}%`}
                        width={40}
                      />
                      <Tooltip 
                        formatter={(value, name) => {
                          if (name === 'volatility') return [`${value}%`, 'Volatility'];
                          return [value, name];
                        }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="volatility" 
                        stroke="#ff6b6b" 
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ height: 350, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography color="text.secondary">No volatility data available</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Moving Averages Chart - Wider */}
        <Grid item xs={12} lg={6} sx={{ 
          display: 'flex',
          padding: '8px !important', // Reduce padding to maximize space
          minWidth: { lg: '600px' } // Set minimum width
        }}>
          <Card elevation={2} sx={{ width: '100%', flex: 1 }}>
            <CardContent sx={{ width: '100%', p: 2 }}>
              <Typography variant="h6" gutterBottom color="primary">
                Moving Averages
              </Typography>
              {movingAverages.length > 0 ? (
                <Box sx={{ width: '100%', height: 350 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={movingAverages} margin={{ left: 0, right: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="date"
                        tick={{ fontSize: 10 }}
                        tickFormatter={(value) => {
                          try {
                            const date = new Date(value);
                            return date.toLocaleDateString('en-US', { 
                              month: 'short', 
                              day: 'numeric' 
                            });
                          } catch {
                            return value;
                          }
                        }}
                        interval={0}
                        angle={-30}
                        textAnchor="end"
                        height={50}
                      />
                      {/* <YAxis 
                        tick={{ fontSize: 10 }}
                        width={40}
                        tickFormatter={(value) => `£${value}`}
                      /> */}

                      <YAxis 
                      tick={{ fontSize: 10 }}
                      width={40}
                      tickFormatter={(value) => `£${(value / 100).toFixed(2)}`} // FIXED
                    />
                      {/* <Tooltip 
                        formatter={(value, name) => {
                          if (name === 'price') return [`£${value}`, 'Price'];
                          if (name === 'price_7d') return [`£${value}`, '7-Day MA'];
                          if (name === 'price_30d') return [`£${value}`, '30-Day MA'];
                          return [value, name];
                        }}
                      /> */}

                      <Tooltip 
                      formatter={(value, name) => {
                        if (name === 'price') return [`£${(value / 100).toFixed(2)}`, 'Price']; // FIXED
                        if (name === 'price_7d') return [`£${(value / 100).toFixed(2)}`, '7-Day MA']; // FIXED
                        if (name === 'price_30d') return [`£${(value / 100).toFixed(2)}`, '30-Day MA']; // FIXED
                        return [value, name];
                      }}
                    />
                      <Line 
                        type="monotone" 
                        dataKey="price" 
                        stroke="#8884d8" 
                        strokeWidth={2}
                        dot={false}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="price_7d" 
                        stroke="#4ecdc4" 
                        strokeWidth={1.5}
                        dot={false}
                        strokeDasharray="3 3"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="price_30d" 
                        stroke="#45b7d1" 
                        strokeWidth={1.5}
                        dot={false}
                        strokeDasharray="5 5"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ height: 350, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
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


// SectorAnalysisTab - WITH DYNAMIC UK COMPANY MAPPING
const SectorAnalysisTab = ({ data }) => {
  const sectorPerformance = data.sector_performance || [];
  const sectorRankings = data.sector_rankings || [];
  const stockPerformance = data.stock_performance || [];

  // Create UK sector mapping based on known company sectors (only sector mapping, no hardcoded performance)
  const ukSectorMapping = {
    "ULVR.L": { company: "Unilever", sector: "Consumer Goods" },
    "RIO.L": { company: "Rio Tinto", sector: "Mining & Resources" },
    "GSK.L": { company: "GSK", sector: "Pharmaceuticals" },
    "LLOY.L": { company: "Lloyds Banking", sector: "Banking" },
    "BARC.L": { company: "Barclays", sector: "Banking" },
    "TSCO.L": { company: "Tesco", sector: "Retail" },
    "AZN.L": { company: "AstraZeneca", sector: "Pharmaceuticals" },
    "BP.L": { company: "BP", sector: "Oil & Gas" },
    "HSBA.L": { company: "HSBC", sector: "Banking" }
  };

  // Map generic sectors to real sectors based on company data
  const sectorToRealName = {
    "Sector U": "Consumer Goods",      // Unilever
    "Sector R": "Mining & Resources",  // Rio Tinto
    "Sector G": "Pharmaceuticals",     // GSK
    "Sector L": "Banking",             // Lloyds
    "Sector T": "Retail",              // Tesco
    "Sector A": "Pharmaceuticals",     // AstraZeneca
    "Sector B": "Banking",             // Barclays + HSBC
    "Sector H": "Oil & Gas"            // BP
  };

  // Create a lookup of current stock performance from API data
  const currentStockPerformance = {};
  stockPerformance.forEach(stock => {
    if (stock.symbol) {
      currentStockPerformance[stock.symbol] = {
        company: stock.company,
        change: stock.change,
        performance: stock.change // Using the actual API performance data
      };
    }
  });

  // Enhanced sector data with real names and dynamic company performance
  const enhancedSectorPerformance = sectorPerformance.map(sector => {
    const realSector = sectorToRealName[sector.sector] || sector.sector;
    
    // Find companies in this sector with their current performance data
    const companies = Object.entries(ukSectorMapping)
      .filter(([symbol, companyData]) => companyData.sector === realSector)
      .map(([symbol, companyData]) => {
        const currentPerformance = currentStockPerformance[symbol];
        return {
          symbol: symbol,
          company: companyData.company,
          performance: currentPerformance ? currentPerformance.change : 0,
          ...currentPerformance
        };
      });

    return {
      ...sector,
      realSector: realSector,
      companies: companies
    };
  });

  const enhancedSectorRankings = sectorRankings.map(ranking => {
    const realSector = sectorToRealName[ranking.name] || ranking.name;
    
    // Find companies in this sector with their current performance data
    const companies = Object.entries(ukSectorMapping)
      .filter(([symbol, companyData]) => companyData.sector === realSector)
      .map(([symbol, companyData]) => {
        const currentPerformance = currentStockPerformance[symbol];
        return {
          symbol: symbol,
          company: companyData.company,
          performance: currentPerformance ? currentPerformance.change : 0,
          ...currentPerformance
        };
      });

    return {
      ...ranking,
      realSector: realSector,
      companies: companies
    };
  });

  // Calculate market summary dynamically
  const advancingSectors = enhancedSectorRankings.filter(s => s.change >= 0).length;
  const decliningSectors = enhancedSectorRankings.filter(s => s.change < 0).length;
  const bestPerformer = enhancedSectorRankings[0];
  const worstPerformer = enhancedSectorRankings[enhancedSectorRankings.length - 1];

  return (
    <Box sx={{ width: '100%', maxWidth: '100%', overflow: 'hidden' }}>
      <Grid container spacing={2} sx={{ width: '100%', margin: 0 }}>
        {/* Sector Performance Chart */}
        <Grid item xs={12} lg={8} sx={{ 
          display: 'flex',
          padding: '8px !important',
          minWidth: { lg: '800px' }
        }}>
          <Card elevation={2} sx={{ width: '100%', flex: 1 }}>
            <CardContent sx={{ width: '100%', p: 2 }}>
              <Typography variant="h6" gutterBottom color="primary">
                UK Sector Performance - FTSE 100 Companies
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                📈 {advancingSectors} Sectors Growing • 📉 {decliningSectors} Sectors Declining • Overall: Bearish
              </Typography>
              
              {enhancedSectorPerformance.length > 0 ? (
                <Box sx={{ width: '100%', height: 450 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart 
                      data={enhancedSectorPerformance} 
                      margin={{ top: 20, right: 30, left: 20, bottom: 120 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="realSector" 
                        tick={{ fontSize: 10 }}
                        angle={-45}
                        textAnchor="end"
                        height={120}
                        interval={0}
                      />
                      <YAxis 
                        tick={{ fontSize: 11 }}
                        tickFormatter={(value) => `${value}%`}
                        width={50}
                      />
                      <Tooltip 
                        content={({ active, payload, label }) => {
                          if (active && payload && payload.length) {
                            const performance = payload[0].value;
                            const stockCount = payload[0].payload.stock_count;
                            const companies = payload[0].payload.companies || [];
                            
                            return (
                              <Box sx={{ 
                                bgcolor: 'background.paper', 
                                p: 2, 
                                border: 1, 
                                borderColor: 'divider',
                                borderRadius: 1,
                                boxShadow: 3,
                                minWidth: 280
                              }}>
                                <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
                                  {label}
                                </Typography>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                                  <Typography variant="body2">Performance:</Typography>
                                  <Typography 
                                    variant="body2" 
                                    fontWeight="bold"
                                    color={performance >= 0 ? 'success.main' : 'error.main'}
                                  >
                                    {performance}%
                                  </Typography>
                                </Box>
                                
                                {/* Show companies in this sector */}
                                {companies.length > 0 ? (
                                  <Box sx={{ mt: 2 }}>
                                    <Typography variant="caption" fontWeight="bold" display="block" sx={{ mb: 1 }}>
                                      Companies ({companies.length}):
                                    </Typography>
                                    {companies.map((company, idx) => (
                                      <Box key={idx} sx={{ 
                                        display: 'flex', 
                                        justifyContent: 'space-between', 
                                        alignItems: 'center',
                                        py: 0.5,
                                        borderBottom: idx < companies.length - 1 ? '1px dashed' : 'none',
                                        borderColor: 'divider'
                                      }}>
                                        <Typography variant="caption" sx={{ flex: 1 }}>
                                          {company.company}
                                        </Typography>
                                        <Typography 
                                          variant="caption" 
                                          fontWeight="bold"
                                          color={company.performance >= 0 ? 'success.main' : 'error.main'}
                                          sx={{ minWidth: 50, textAlign: 'right' }}
                                        >
                                          {company.performance}%
                                        </Typography>
                                      </Box>
                                    ))}
                                  </Box>
                                ) : (
                                  <Typography variant="caption" color="text.secondary">
                                    No companies mapped
                                  </Typography>
                                )}
                              </Box>
                            );
                          }
                          return null;
                        }}
                      />
                      <Bar 
                        dataKey="performance" 
                        name="Performance"
                        fill={(entry) => entry.performance >= 0 ? '#4caf50' : '#f44336'}
                        radius={[4, 4, 0, 0]}
                        barSize={35}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Box sx={{ height: 450, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography color="text.secondary">No sector performance data available</Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
        
        {/* Sector Rankings with Companies */}
        <Grid item xs={12} lg={4} sx={{ 
          display: 'flex',
          padding: '8px !important',
          minWidth: { lg: '400px' }
        }}>
          <Card elevation={2} sx={{ width: '100%', flex: 1 }}>
            <CardContent sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', p: 2 }}>
              <Typography variant="h6" gutterBottom color="primary">
                UK Sector Rankings
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                FTSE 100 Companies by Sector Performance
              </Typography>
              
              {enhancedSectorRankings.length > 0 ? (
                <Box sx={{ flexGrow: 1, maxHeight: 450, overflow: 'auto' }}>
                  {enhancedSectorRankings.map((sector, index) => (
                    <Card 
                      key={index} 
                      sx={{ 
                        mb: 2,
                        border: 2,
                        borderColor: index < 3 ? 
                          (index === 0 ? 'success.main' : index === 1 ? 'primary.main' : 'secondary.main') : 
                          'divider',
                        bgcolor: index < 3 ? 'action.hover' : 'background.paper'
                      }}
                    >
                      <CardContent sx={{ p: 1.5 }}>
                        {/* Sector Header */}
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                          <Chip 
                            label={`#${index + 1}`}
                            size="small"
                            color={index === 0 ? 'success' : index === 1 ? 'primary' : index === 2 ? 'secondary' : 'default'}
                            sx={{ 
                              fontWeight: 'bold',
                              fontSize: '0.75rem'
                            }}
                          />
                          <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle2" fontWeight="bold" noWrap>
                              {sector.realSector}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {sector.name}
                            </Typography>
                          </Box>
                          <Chip 
                            label={`${sector.change}%`}
                            size="small"
                            color={sector.change >= 0 ? 'success' : 'error'}
                            variant="filled"
                            sx={{ fontWeight: 'bold' }}
                          />
                        </Box>
                        
                        {/* Companies in this sector */}
                        {sector.companies && sector.companies.length > 0 ? (
                          <Box>
                            <Typography variant="caption" fontWeight="bold" color="text.secondary" display="block" sx={{ mb: 1 }}>
                              Companies:
                            </Typography>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                              {sector.companies.map((company, idx) => (
                                <Box 
                                  key={idx}
                                  sx={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between', 
                                    alignItems: 'center',
                                    px: 1,
                                    py: 0.5,
                                    borderRadius: 0.5,
                                    bgcolor: 'background.default'
                                  }}
                                >
                                  <Typography variant="caption" sx={{ flex: 1 }}>
                                    {company.company}
                                  </Typography>
                                  <Typography 
                                    variant="caption" 
                                    fontWeight="bold"
                                    color={company.performance >= 0 ? 'success.main' : 'error.main'}
                                  >
                                    {company.performance}%
                                  </Typography>
                                </Box>
                              ))}
                            </Box>
                          </Box>
                        ) : (
                          <Typography variant="caption" color="text.secondary">
                            No company data mapped
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                  

                </Box>
              ) : (
                <Box sx={{ height: 450, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography color="text.secondary">No sector rankings available</Typography>
                </Box>
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
    // Use all_services_data for service listings and chart_data for the chart
    const allServices = data.all_services_data || data.chart_data || [];
    const serviceBreakdown = data.service_breakdown || {};
    
    // Categorize services from ALL services data
    const goodServices = allServices.filter(service => 
      service.status === 'Good Service' || 
      service.status?.toLowerCase().includes('good service')
    );
    
    const moderateServices = allServices.filter(service => 
      service.status === 'Minor Delays' || 
      service.status === 'Reduced Service' ||
      service.status?.toLowerCase().includes('minor delay') ||
      service.status?.toLowerCase().includes('reduced service')
    );
    
    const poorServices = allServices.filter(service => 
      service.status === 'Part Closure' || 
      service.status === 'Planned Closure' ||
      service.status === 'Part Suspended' ||
      service.status?.toLowerCase().includes('closure') ||
      service.status?.toLowerCase().includes('suspended') ||
      service.status?.toLowerCase().includes('severe delay')
    );

    return {
      title: 'Transportation',
      currentValue: `${data.delayed_lines || 0}/${data.total_lines || 0} lines delayed`,
      change: data.delay_percentage ? `${data.delay_percentage}%` : '0%',
      trend: data.trend || 'stable',
      chartData: data.chart_data || [], // Use the time-series chart data
      metrics: [
        { label: 'Total Lines', value: data.total_lines || 0 },
        { label: 'Delayed Lines', value: data.delayed_lines || 0 },
        { label: 'Delay %', value: data.delay_percentage ? `${data.delay_percentage}%` : '0%' }
      ],
      allServices: allServices, // Use all services data for listings
      goodServices: goodServices,
      moderateServices: moderateServices,
      poorServices: poorServices,
      serviceBreakdown: serviceBreakdown,
      majorIssues: data.major_issues || []
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
              displayData.trend === 'up' ? 'success' : 
              displayData.trend === 'down' ? 'error' : 
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
          return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric'
          });
        } catch (error) {
          if (typeof value === 'string') {
            const getMonthName = (monthNumber) => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return months[parseInt(monthNumber) - 1] || monthNumber;
};
            const datePart = value.split('T')[0];
            const [year, month, day] = datePart.split('-');
            return `${getMonthName(month)} ${day}`;
          }
          return value;
        }
      }}
      angle={0}
      height={40}
    />
    {/* FIXED Y-AXIS WITH UNITS FOR ALL SECTORS */}
    <YAxis 
      tickFormatter={(value) => {
        if (sector.toLowerCase() === 'finance') {
          return `£${(value / 100).toFixed(2)}`; // Finance: Pounds
        } else if (sector.toLowerCase() === 'transportation') {
          return `${value}m`; // Transportation: Minutes
        } else if (sector.toLowerCase() === 'weather') {
          return `${value}°C`; // Weather: Celsius
        }
        return value; // Other sectors: No units
      }}
    />
    <Tooltip 
      formatter={(value, name) => {
        if (sector.toLowerCase() === 'transportation') {
          return [`${value} min`, 'Delay'];
        } else if (sector.toLowerCase() === 'weather') {
          return [`${value}°C`, 'Temperature'];
        } else if (sector.toLowerCase() === 'finance') {
          return [`£${(value/100).toFixed(2)}`, 'Price'];
        }
        return [value, name];
      }}
      labelFormatter={(label) => {
        const date = new Date(label);
        return `Date: ${date.toLocaleDateString('en-US', { 
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })}`;
      }}
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
                            {service.line_name ||service.line}
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
                            {service.line_name || service.line}
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
                            {service.line_name || service.line}
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
                              £${(stock.current_price/100)?.toFixed(2)}
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
                    {displayData.advancing_stocks}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
                  <Typography variant="caption" display="block" fontWeight="bold" color="error.dark">
                    Declining
                  </Typography>
                  <Typography variant="h6" color="error.dark">
                    {displayData.declining_stocks}
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