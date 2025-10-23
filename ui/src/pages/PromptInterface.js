import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Chip,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Alert,
} from '@mui/material';
import { promptService } from '../services/api';

const sectors = ['transportation', 'finance', 'weather'];

const PromptInterface = () => {
  const [prompt, setPrompt] = useState('');
  const [selectedSector, setSelectedSector] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await promptService.analyzePrompt(prompt, selectedSector || null);
      setResults(response.data);
    } catch (err) {
      setError('Failed to analyze prompt. Please try again.');
      console.error('Error analyzing prompt:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        AI-Powered Insights
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Enter your prompt"
                multiline
                rows={4}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                sx={{ mb: 2 }}
                placeholder="e.g., Show me current stock prices"
              />
              
              <Typography variant="h6" gutterBottom>
                Select Sector (Optional):
              </Typography>
              <Box sx={{ mb: 2 }}>
                {sectors.map((sector) => (
                  <Chip
                    key={sector}
                    label={sector.charAt(0).toUpperCase() + sector.slice(1)}
                    onClick={() => setSelectedSector(sector)}
                    color={selectedSector === sector ? 'primary' : 'default'}
                    sx={{ m: 0.5 }}
                  />
                ))}
              </Box>

              <Button
                type="submit"
                variant="contained"
                fullWidth
                disabled={loading}
                size="large"
              >
                {loading ? 'Analyzing...' : 'Get Insights'}
              </Button>
            </form>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          {loading && <LinearProgress />}
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {results && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom color="primary">
                  Analysis Results
                </Typography>
                
                <Typography variant="body1" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
                  {results.insights}
                </Typography>
                
                {results.recommendations && results.recommendations.length > 0 && (
                  <>
                    <Typography variant="h6" gutterBottom>
                      Recommendations
                    </Typography>
                    <ul>
                      {results.recommendations.map((rec, index) => (
                        <li key={index}>
                          <Typography variant="body1">{rec}</Typography>
                        </li>
                      ))}
                    </ul>
                  </>
                )}

                {results.related_questions && results.related_questions.length > 0 && (
                  <>
                    <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                      Related Questions
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {results.related_questions.map((question, index) => (
                        <Chip
                          key={index}
                          label={question}
                          variant="outlined"
                          onClick={() => setPrompt(question)}
                        />
                      ))}
                    </Box>
                  </>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default PromptInterface;