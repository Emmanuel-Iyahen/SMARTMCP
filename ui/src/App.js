import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { SnackbarProvider } from 'notistack';

import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import PromptInterface from './pages/PromptInterface';
import SectorAnalysis from './pages/SectorAnalysis';
import DataSources from './pages/DataSources';
import MCPConfiguration from './pages/MCPConfiguration';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00b4d8',
      light: '#48cae4',
      dark: '#0096c7',
    },
    secondary: {
      main: '#0077b6',
      light: '#0096c7',
      dark: '#023e8a',
    },
    background: {
      default: '#0a1929',
      paper: '#132f4c',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider 
        maxSnack={3}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
      >
        <Router>
          <div className="App">
            <Navigation />
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/prompt" element={<PromptInterface />} />
              <Route path="/sector/:sector" element={<SectorAnalysis />} />
              <Route path="/data-sources" element={<DataSources />} />
               <Route path="/mcp-configuration" element={<MCPConfiguration />} />
            </Routes>
          </div>
        </Router>
      </SnackbarProvider>
    </ThemeProvider>
  );
}

export default App;