import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  Chip,
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
} from 'recharts';
import { useParams } from 'react-router-dom';
import { dashboardService } from '../services/api';

const SectorAnalysis = () => {
  const { sector } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    const loadSectorData = async () => {
      try {
        setLoading(true);
        const response = await dashboardService.getSectorData(sector);
        setData(response.data.data);
        setError(null);
      } catch (err) {
        setError(`Failed to load ${sector} data`);
        console.error('Error loading sector data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadSectorData();
  }, [sector]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (loading) return <LinearProgress />;

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!data) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">No data available for {sector}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          {sector.charAt(0).toUpperCase() + sector.slice(1)} Analysis
        </Typography>
        <Chip label={data.trends?.overall || 'Stable'} color="primary" />
      </Box>

      <Tabs value={tabValue} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Metrics" />
        <Tab label="Trends" />
        <Tab label="Alerts" />
      </Tabs>

      {tabValue === 0 && <OverviewTab data={data} sector={sector} />}
      {tabValue === 1 && <MetricsTab data={data} />}
      {tabValue === 2 && <TrendsTab data={data} />}
      {tabValue === 3 && <AlertsTab data={data} />}
    </Box>
  );
};

const OverviewTab = ({ data, sector }) => (
  <Grid container spacing={3}>
    <Grid item xs={12} md={8}>
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Historical Trends
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.timeseries || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </Grid>
    
    <Grid item xs={12} md={4}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Key Metrics
          </Typography>
          {data.metrics && Object.entries(data.metrics).map(([key, value]) => (
            <Box key={key} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">{key}:</Typography>
              <Typography variant="body2" fontWeight="bold">
                {typeof value === 'number' ? value.toFixed(2) : value}
              </Typography>
            </Box>
          ))}
        </CardContent>
      </Card>
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Status
          </Typography>
          <Chip 
            label={data.trends?.overall || 'Unknown'} 
            color={
              data.trends?.overall === 'Improving' ? 'success' : 
              data.trends?.overall === 'Declining' ? 'error' : 'default'
            } 
          />
        </CardContent>
      </Card>
    </Grid>
  </Grid>
);

const MetricsTab = ({ data }) => (
  <Grid container spacing={3}>
    {data.metrics && Object.entries(data.metrics).map(([key, value]) => (
      <Grid item xs={12} sm={6} md={3} key={key}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              {key.replace(/_/g, ' ').toUpperCase()}
            </Typography>
            <Typography variant="h4" color="primary">
              {typeof value === 'number' ? value.toFixed(2) : value}
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    ))}
  </Grid>
);

const TrendsTab = ({ data }) => (
  <Card>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Trend Analysis
      </Typography>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={data.timeseries || []}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="timestamp" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="value" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </CardContent>
  </Card>
);

const AlertsTab = ({ data }) => (
  <Card>
    <CardContent>
      <Typography variant="h6" gutterBottom>
        Active Alerts
      </Typography>
      {data.alerts && data.alerts.length > 0 ? (
        data.alerts.map((alert, index) => (
          <Alert key={index} severity={alert.severity || 'info'} sx={{ mb: 2 }}>
            {alert.message}
          </Alert>
        ))
      ) : (
        <Typography>No active alerts</Typography>
      )}
    </CardContent>
  </Card>
);

export default SectorAnalysis;