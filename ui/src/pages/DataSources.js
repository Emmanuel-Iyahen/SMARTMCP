import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from '@mui/material';
import { dataSourcesService } from '../services/api';

const DataSources = () => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadDataSources = async () => {
      try {
        setLoading(true);
        const response = await dataSourcesService.getSources();
        setSources(response.data.data_sources);
        setError(null);
      } catch (err) {
        setError('Failed to load data sources');
        console.error('Error loading data sources:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDataSources();
  }, []);

  if (loading) return <LinearProgress />;

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Data Sources
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Real-time data sources powering the MCP Platform
      </Typography>

      <Grid container spacing={3}>
        {sources.map((source) => (
          <Grid item xs={12} md={6} key={source.id}>
            <DataSourceCard source={source} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

const DataSourceCard = ({ source }) => (
  <Card>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">{source.name}</Typography>
        <Chip label={source.update_frequency} size="small" color="primary" />
      </Box>
      
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        {source.description}
      </Typography>

      <Typography variant="body2" sx={{ mb: 1 }}>
        <strong>Provider:</strong> {source.provider}
      </Typography>
      
      <Typography variant="body2" sx={{ mb: 1 }}>
        <strong>Available from:</strong> {source.available_from}
      </Typography>

      <Typography variant="body2" sx={{ mb: 2 }}>
        <strong>Fields:</strong> {source.fields.join(', ')}
      </Typography>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <Chip label="API" size="small" variant="outlined" />
        <Chip label="Real-time" size="small" variant="outlined" />
      </Box>
    </CardContent>
  </Card>
);

export default DataSources;