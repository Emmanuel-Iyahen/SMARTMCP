import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Chip,
} from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import DataObjectIcon from '@mui/icons-material/DataObject';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: <AnalyticsIcon /> },
    { path: '/prompt', label: 'AI Analysis', icon: <SmartToyIcon /> },
    { path: '/data-sources', label: 'Data Sources', icon: <DataObjectIcon /> },
  ];

  return (
    <AppBar position="static" elevation={2}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
          MCP Platform
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              component={Link}
              to={item.path}
              startIcon={item.icon}
              sx={{
                color: 'white',
                backgroundColor: location.pathname === item.path ? 'primary.dark' : 'transparent',
                '&:hover': {
                  backgroundColor: 'primary.dark',
                },
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        <Chip 
          label="Live" 
          color="success" 
          size="small" 
          sx={{ ml: 2 }} 
        />
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;