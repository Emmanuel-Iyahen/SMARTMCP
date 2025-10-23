// import React, { useState } from 'react';
// import {
//   Box,
//   Typography,
//   Card,
//   CardContent,
//   Grid,
//   TextField,
//   Button,
//   Paper,
//   Divider,
//   Alert,
//   Tabs,
//   Tab,
//   Chip,
//   IconButton,
//   Snackbar
// } from '@mui/material';
// import {
//   ContentCopy as CopyIcon,
//   Code as CodeIcon,
//   Settings as SettingsIcon,
//   Link as LinkIcon
// } from '@mui/icons-material';

// const MCPConfiguration = () => {
//   const [activeTab, setActiveTab] = useState(0);
//   const [baseUrl, setBaseUrl] = useState('https://your-smartmcp-server.com');
//   const [apiKey, setApiKey] = useState('your-mcp-api-key');
//   const [copySuccess, setCopySuccess] = useState('');

//   const handleTabChange = (event, newValue) => {
//     setActiveTab(newValue);
//   };

//   const handleCopy = (text, message) => {
//     navigator.clipboard.writeText(text);
//     setCopySuccess(message);
//     setTimeout(() => setCopySuccess(''), 2000);
//   };

//   const discoveryEndpoint = `${baseUrl}/.well-known/mcp.json`;

//   const claudeConfig = {
//     "mcpServers": {
//       "smartmcp": {
//         "command": "npx",
//         "args": [
//           "@modelcontextprotocol/server-smartmcp",
//           "--url",
//           baseUrl,
//           "--token",
//           apiKey
//         ]
//       }
//     }
//   };

//   const httpConfig = {
//     "mcpServers": {
//       "smartmcp": {
//         "command": "http",
//         "args": {
//           "url": discoveryEndpoint,
//           "headers": {
//             "Authorization": `Bearer ${apiKey}`
//           }
//         }
//       }
//     }
//   };

//   const pythonClientCode = `import httpx

// class SmartMCPClient:
//     def __init__(self, base_url: str, api_key: str):
//         self.base_url = base_url
//         self.headers = {"Authorization": f"Bearer {api_key}"}
    
//     async def get_transport_data(self):
//         async with httpx.AsyncClient() as client:
//             response = await client.post(
//                 f"{self.base_url}/mcp/tools/get_transport_data",
//                 json={},
//                 headers=self.headers
//             )
//             return response.json()
    
//     async def get_weather_data(self):
//         async with httpx.AsyncClient() as client:
//             response = await client.post(
//                 f"{self.base_url}/mcp/tools/get_weather_data",
//                 json={},
//                 headers=self.headers
//             )
//             return response.json()
    
//     async def get_financial_data(self):
//         async with httpx.AsyncClient() as client:
//             response = await client.post(
//                 f"{self.base_url}/mcp/tools/get_financial_data",
//                 json={},
//                 headers=self.headers
//             )
//             return response.json()
    
//     async def list_tools(self):
//         async with httpx.AsyncClient() as client:
//             response = await client.get(
//                 f"{self.base_url}/mcp/tools",
//                 headers=self.headers
//             )
//             return response.json()

// # Usage
// client = SmartMCPClient("${baseUrl}", "${apiKey}")
// transport_data = await client.get_transport_data()`;

//   const availableTools = [
//     {
//       name: "get_transport_data",
//       description: "Get real-time transportation data including delays, service status, and line information",
//       parameters: "None",
//       returns: "Transportation data object"
//     },
//     {
//       name: "get_weather_data", 
//       description: "Get current weather conditions, forecasts, and alerts",
//       parameters: "None",
//       returns: "Weather data object"
//     },
//     {
//       name: "get_financial_data",
//       description: "Get stock market data, trends, and financial metrics",
//       parameters: "None", 
//       returns: "Financial data object"
//     },
//     {
//       name: "list_tools",
//       description: "Get list of all available MCP tools",
//       parameters: "None",
//       returns: "Array of tool definitions"
//     }
//   ];

//   return (
//     <Box sx={{ p: 3, maxWidth: 1200, margin: '0 auto' }}>
//       {/* Header */}
//       <Box sx={{ mb: 4, textAlign: 'center' }}>
//         <Typography variant="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2 }}>
//           🔌 MCP Server Configuration
//         </Typography>
//         <Typography variant="h6" color="text.secondary" gutterBottom>
//           For MCP Client Developers
//         </Typography>
//         <Typography variant="body1" color="text.secondary">
//           SmartMCP exposes a standard MCP 1.0.0 compliant server that other MCP clients can connect to.
//         </Typography>
//       </Box>

//       {/* Configuration Settings */}
//       <Card sx={{ mb: 4 }}>
//         <CardContent>
//           <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
//             <SettingsIcon /> Server Configuration
//           </Typography>
//           <Grid container spacing={3}>
//             <Grid item xs={12} md={6}>
//               <TextField
//                 fullWidth
//                 label="Base URL"
//                 value={baseUrl}
//                 onChange={(e) => setBaseUrl(e.target.value)}
//                 margin="normal"
//                 helperText="Your SmartMCP server base URL"
//               />
//             </Grid>
//             <Grid item xs={12} md={6}>
//               <TextField
//                 fullWidth
//                 label="API Key"
//                 value={apiKey}
//                 onChange={(e) => setApiKey(e.target.value)}
//                 margin="normal"
//                 helperText="Your MCP API key"
//               />
//             </Grid>
//           </Grid>
          
//           <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
//             <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
//               <LinkIcon /> Discovery Endpoint
//             </Typography>
//             <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
//               <Typography variant="body2" fontFamily="monospace" sx={{ flexGrow: 1 }}>
//                 GET {discoveryEndpoint}
//               </Typography>
//               <IconButton 
//                 size="small" 
//                 onClick={() => handleCopy(discoveryEndpoint, 'Discovery endpoint copied!')}
//               >
//                 <CopyIcon />
//               </IconButton>
//             </Box>
//             <Chip 
//               label="No authentication required - returns server capabilities" 
//               size="small" 
//               variant="outlined" 
//               sx={{ mt: 1 }}
//             />
//           </Box>
//         </CardContent>
//       </Card>

//       <Paper sx={{ width: '100%', mb: 3 }}>
//         <Tabs
//           value={activeTab}
//           onChange={handleTabChange}
//           indicatorColor="primary"
//           textColor="primary"
//           centered
//         >
//           <Tab label="Claude Desktop" />
//           <Tab label="HTTP Clients" />
//           <Tab label="Python SDK" />
//           <Tab label="Available Tools" />
//         </Tabs>
//       </Paper>

//       {/* Claude Desktop Configuration */}
//       {activeTab === 0 && (
//         <Card>
//           <CardContent>
//             <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
//               <CodeIcon /> Claude Desktop Configuration
//             </Typography>
//             <Alert severity="info" sx={{ mb: 3 }}>
//               Add this configuration to your Claude Desktop config.json file
//             </Alert>
            
//             <Paper sx={{ p: 2, bgcolor: 'grey.100', position: 'relative' }}>
//               <IconButton 
//                 sx={{ position: 'absolute', top: 8, right: 8 }}
//                 onClick={() => handleCopy(JSON.stringify(claudeConfig, null, 2), 'Claude config copied!')}
//               >
//                 <CopyIcon />
//               </IconButton>
//               <pre style={{ margin: 0, fontSize: '0.9rem', overflow: 'auto' }}>
//                 {JSON.stringify(claudeConfig, null, 2)}
//               </pre>
//             </Paper>
            
//             <Box sx={{ mt: 3 }}>
//               <Typography variant="subtitle2" gutterBottom>
//                 Configuration Location:
//               </Typography>
//               <Typography variant="body2" color="text.secondary">
//                 • macOS: ~/Library/Application Support/Claude/claude_desktop_config.json<br/>
//                 • Windows: %APPDATA%/Claude/claude_desktop_config.json<br/>
//                 • Linux: ~/.config/Claude/claude_desktop_config.json
//               </Typography>
//             </Box>
//           </CardContent>
//         </Card>
//       )}

//       {/* HTTP Configuration */}
//       {activeTab === 1 && (
//         <Card>
//           <CardContent>
//             <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
//               <CodeIcon /> Direct HTTP Configuration
//             </Typography>
//             <Alert severity="info" sx={{ mb: 3 }}>
//               For HTTP-based MCP clients that support direct server connections
//             </Alert>
            
//             <Paper sx={{ p: 2, bgcolor: 'grey.100', position: 'relative', mb: 3 }}>
//               <IconButton 
//                 sx={{ position: 'absolute', top: 8, right: 8 }}
//                 onClick={() => handleCopy(JSON.stringify(httpConfig, null, 2), 'HTTP config copied!')}
//               >
//                 <CopyIcon />
//               </IconButton>
//               <pre style={{ margin: 0, fontSize: '0.9rem', overflow: 'auto' }}>
//                 {JSON.stringify(httpConfig, null, 2)}
//               </pre>
//             </Paper>

//             <Typography variant="subtitle2" gutterBottom>
//               curl Example:
//             </Typography>
//             <Paper sx={{ p: 2, bgcolor: 'grey.100', position: 'relative' }}>
//               <IconButton 
//                 sx={{ position: 'absolute', top: 8, right: 8 }}
//                 onClick={() => handleCopy(`curl -H "Authorization: Bearer ${apiKey}" ${discoveryEndpoint}`, 'cURL command copied!')}
//               >
//                 <CopyIcon />
//               </IconButton>
//               <pre style={{ margin: 0, fontSize: '0.9rem', overflow: 'auto' }}>
// {`curl -H "Authorization: Bearer ${apiKey}" ${discoveryEndpoint}`}
//               </pre>
//             </Paper>
//           </CardContent>
//         </Card>
//       )}

//       {/* Python SDK */}
//       {activeTab === 2 && (
//         <Card>
//           <CardContent>
//             <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
//               <CodeIcon /> Python Client Usage
//             </Typography>
//             <Alert severity="info" sx={{ mb: 3 }}>
//               Complete Python client implementation for integrating with SmartMCP
//             </Alert>
            
//             <Paper sx={{ p: 2, bgcolor: 'grey.100', position: 'relative' }}>
//               <IconButton 
//                 sx={{ position: 'absolute', top: 8, right: 8 }}
//                 onClick={() => handleCopy(pythonClientCode, 'Python code copied!')}
//               >
//                 <CopyIcon />
//               </IconButton>
//               <pre style={{ margin: 0, fontSize: '0.85rem', overflow: 'auto' }}>
//                 {pythonClientCode}
//               </pre>
//             </Paper>

//             <Box sx={{ mt: 3 }}>
//               <Typography variant="subtitle2" gutterBottom>
//                 Installation:
//               </Typography>
//               <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
//                 <pre style={{ margin: 0, fontSize: '0.9rem' }}>pip install httpx</pre>
//               </Paper>
//             </Box>
//           </CardContent>
//         </Card>
//       )}

//       {/* Available Tools */}
//       {activeTab === 3 && (
//         <Card>
//           <CardContent>
//             <Typography variant="h6" gutterBottom>
//               Available MCP Tools
//             </Typography>
//             <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
//               These tools are available through the SmartMCP server interface
//             </Typography>
            
//             <Grid container spacing={2}>
//               {availableTools.map((tool, index) => (
//                 <Grid item xs={12} key={index}>
//                   <Paper sx={{ p: 2, border: 1, borderColor: 'divider' }}>
//                     <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
//                       <Typography variant="subtitle1" fontFamily="monospace" color="primary">
//                         {tool.name}
//                       </Typography>
//                       <Chip label="MCP Tool" size="small" variant="outlined" />
//                     </Box>
//                     <Typography variant="body2" sx={{ mb: 1 }}>
//                       {tool.description}
//                     </Typography>
//                     <Box sx={{ display: 'flex', gap: 2 }}>
//                       <Typography variant="caption" color="text.secondary">
//                         <strong>Parameters:</strong> {tool.parameters}
//                       </Typography>
//                       <Typography variant="caption" color="text.secondary">
//                         <strong>Returns:</strong> {tool.returns}
//                       </Typography>
//                     </Box>
//                   </Paper>
//                 </Grid>
//               ))}
//             </Grid>
//           </CardContent>
//         </Card>
//       )}

//       {/* Quick Start Guide */}
//       <Card sx={{ mt: 4 }}>
//         <CardContent>
//           <Typography variant="h6" gutterBottom>
//             🚀 Quick Start Guide
//           </Typography>
//           <Grid container spacing={3}>
//             <Grid item xs={12} md={4}>
//               <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
//                 <Typography variant="h6" color="primary">1</Typography>
//                 <Typography variant="subtitle2" gutterBottom>Get API Key</Typography>
//                 <Typography variant="body2" color="text.secondary">
//                   Obtain your MCP API key from the SmartMCP administrator
//                 </Typography>
//               </Paper>
//             </Grid>
//             <Grid item xs={12} md={4}>
//               <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
//                 <Typography variant="h6" color="primary">2</Typography>
//                 <Typography variant="subtitle2" gutterBottom>Configure Client</Typography>
//                 <Typography variant="body2" color="text.secondary">
//                   Choose your preferred client configuration method above
//                 </Typography>
//               </Paper>
//             </Grid>
//             <Grid item xs={12} md={4}>
//               <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
//                 <Typography variant="h6" color="primary">3</Typography>
//                 <Typography variant="subtitle2" gutterBottom>Start Building</Typography>
//                 <Typography variant="body2" color="text.secondary">
//                   Use the available tools to integrate data into your applications
//                 </Typography>
//               </Paper>
//             </Grid>
//           </Grid>
//         </CardContent>
//       </Card>

//       {/* Copy Success Snackbar */}
//       <Snackbar
//         open={!!copySuccess}
//         autoHideDuration={2000}
//         onClose={() => setCopySuccess('')}
//         message={copySuccess}
//         anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
//       />
//     </Box>
//   );
// };

// export default MCPConfiguration;



import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Paper,
  Divider,
  Alert,
  Tabs,
  Tab,
  Chip,
  IconButton,
  Snackbar,
  useTheme
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Code as CodeIcon,
  Settings as SettingsIcon,
  Link as LinkIcon
} from '@mui/icons-material';

const MCPConfiguration = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [baseUrl, setBaseUrl] = useState('https://your-smartmcp-server.com');
  const [apiKey, setApiKey] = useState('your-mcp-api-key');
  const [copySuccess, setCopySuccess] = useState('');
  const theme = useTheme();

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleCopy = (text, message) => {
    navigator.clipboard.writeText(text);
    setCopySuccess(message);
    setTimeout(() => setCopySuccess(''), 2000);
  };

  const discoveryEndpoint = `${baseUrl}/.well-known/mcp.json`;

  const claudeConfig = {
    "mcpServers": {
      "smartmcp": {
        "command": "npx",
        "args": [
          "@modelcontextprotocol/server-smartmcp",
          "--url",
          baseUrl,
          "--token",
          apiKey
        ]
      }
    }
  };

  const httpConfig = {
    "mcpServers": {
      "smartmcp": {
        "command": "http",
        "args": {
          "url": discoveryEndpoint,
          "headers": {
            "Authorization": `Bearer ${apiKey}`
          }
        }
      }
    }
  };

  const pythonClientCode = `import httpx

class SmartMCPClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def get_transport_data(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/tools/get_transport_data",
                json={},
                headers=self.headers
            )
            return response.json()
    
    async def get_weather_data(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/tools/get_weather_data",
                json={},
                headers=self.headers
            )
            return response.json()
    
    async def get_financial_data(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/mcp/tools/get_financial_data",
                json={},
                headers=self.headers
            )
            return response.json()
    
    async def list_tools(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/mcp/tools",
                headers=self.headers
            )
            return response.json()

# Usage
client = SmartMCPClient("${baseUrl}", "${apiKey}")
transport_data = await client.get_transport_data()`;

  const availableTools = [
    {
      name: "get_transport_data",
      description: "Get real-time transportation data including delays, service status, and line information",
      parameters: "None",
      returns: "Transportation data object"
    },
    {
      name: "get_weather_data", 
      description: "Get current weather conditions, forecasts, and alerts",
      parameters: "None",
      returns: "Weather data object"
    },
    {
      name: "get_financial_data",
      description: "Get stock market data, trends, and financial metrics",
      parameters: "None", 
      returns: "Financial data object"
    },
    {
      name: "list_tools",
      description: "Get list of all available MCP tools",
      parameters: "None",
      returns: "Array of tool definitions"
    }
  ];

  // Styles for code blocks with proper contrast
  const codeBlockStyle = {
    p: 2,
    bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'grey.100',
    border: `1px solid ${theme.palette.divider}`,
    borderRadius: 1,
    position: 'relative',
    overflow: 'auto',
    maxHeight: '400px'
  };

  const codeTextStyle = {
    margin: 0,
    fontSize: '0.85rem',
    fontFamily: "'Monaco', 'Menlo', 'Ubuntu Mono', monospace",
    lineHeight: 1.5,
    color: theme.palette.mode === 'dark' ? 'grey.100' : 'grey.800',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-all'
  };

  const inlineCodeStyle = {
    fontFamily: "'Monaco', 'Menlo', 'Ubuntu Mono', monospace",
    backgroundColor: theme.palette.mode === 'dark' ? 'grey.800' : 'grey.200',
    padding: '2px 6px',
    borderRadius: 1,
    fontSize: '0.85rem',
    color: theme.palette.mode === 'dark' ? 'grey.100' : 'grey.800'
  };

  return (
    <Box sx={{ p: 3, maxWidth: 1200, margin: '0 auto' }}>
      {/* Header */}
      <Box sx={{ mb: 4, textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2 }}>
          🔌 MCP Server Configuration
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          For MCP Client Developers
        </Typography>
        <Typography variant="body1" color="text.secondary">
          SmartMCP exposes a standard MCP 1.0.0 compliant server that other MCP clients can connect to.
        </Typography>
      </Box>

      {/* Configuration Settings */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsIcon /> Server Configuration
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Base URL"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                margin="normal"
                helperText="Your SmartMCP server base URL"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="API Key"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                margin="normal"
                helperText="Your MCP API key"
              />
            </Grid>
          </Grid>
          
          <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', border: 1, borderColor: 'divider', borderRadius: 1 }}>
            <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <LinkIcon /> Discovery Endpoint
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" sx={inlineCodeStyle} component="span">
                GET {discoveryEndpoint}
              </Typography>
              <IconButton 
                size="small" 
                onClick={() => handleCopy(discoveryEndpoint, 'Discovery endpoint copied!')}
              >
                <CopyIcon />
              </IconButton>
            </Box>
            <Chip 
              label="No authentication required - returns server capabilities" 
              size="small" 
              variant="outlined" 
              sx={{ mt: 1 }}
            />
          </Box>
        </CardContent>
      </Card>

      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          centered
        >
          <Tab label="Claude Desktop" />
          <Tab label="HTTP Clients" />
          <Tab label="Python SDK" />
          <Tab label="Available Tools" />
        </Tabs>
      </Paper>

      {/* Claude Desktop Configuration */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CodeIcon /> Claude Desktop Configuration
            </Typography>
            <Alert severity="info" sx={{ mb: 3 }}>
              Add this configuration to your Claude Desktop config.json file
            </Alert>
            
            <Box sx={codeBlockStyle}>
              <IconButton 
                sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'background.paper' }}
                onClick={() => handleCopy(JSON.stringify(claudeConfig, null, 2), 'Claude config copied!')}
              >
                <CopyIcon />
              </IconButton>
              <pre style={codeTextStyle}>
                {JSON.stringify(claudeConfig, null, 2)}
              </pre>
            </Box>
            
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Configuration Location:
              </Typography>
              <Box sx={inlineCodeStyle}>
                <Typography variant="body2" component="div">
                  • macOS: ~/Library/Application Support/Claude/claude_desktop_config.json<br/>
                  • Windows: %APPDATA%/Claude/claude_desktop_config.json<br/>
                  • Linux: ~/.config/Claude/claude_desktop_config.json
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* HTTP Configuration */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CodeIcon /> Direct HTTP Configuration
            </Typography>
            <Alert severity="info" sx={{ mb: 3 }}>
              For HTTP-based MCP clients that support direct server connections
            </Alert>
            
            <Box sx={{ ...codeBlockStyle, mb: 3 }}>
              <IconButton 
                sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'background.paper' }}
                onClick={() => handleCopy(JSON.stringify(httpConfig, null, 2), 'HTTP config copied!')}
              >
                <CopyIcon />
              </IconButton>
              <pre style={codeTextStyle}>
                {JSON.stringify(httpConfig, null, 2)}
              </pre>
            </Box>

            <Typography variant="subtitle2" gutterBottom>
              curl Example:
            </Typography>
            <Box sx={codeBlockStyle}>
              <IconButton 
                sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'background.paper' }}
                onClick={() => handleCopy(`curl -H "Authorization: Bearer ${apiKey}" ${discoveryEndpoint}`, 'cURL command copied!')}
              >
                <CopyIcon />
              </IconButton>
              <pre style={codeTextStyle}>
{`curl -H "Authorization: Bearer ${apiKey}" ${discoveryEndpoint}`}
              </pre>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Python SDK */}
      {activeTab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CodeIcon /> Python Client Usage
            </Typography>
            <Alert severity="info" sx={{ mb: 3 }}>
              Complete Python client implementation for integrating with SmartMCP
            </Alert>
            
            <Box sx={codeBlockStyle}>
              <IconButton 
                sx={{ position: 'absolute', top: 8, right: 8, bgcolor: 'background.paper' }}
                onClick={() => handleCopy(pythonClientCode, 'Python code copied!')}
              >
                <CopyIcon />
              </IconButton>
              <pre style={codeTextStyle}>
                {pythonClientCode}
              </pre>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Installation:
              </Typography>
              <Box sx={codeBlockStyle}>
                <pre style={codeTextStyle}>pip install httpx</pre>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Available Tools */}
      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Available MCP Tools
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              These tools are available through the SmartMCP server interface
            </Typography>
            
            <Grid container spacing={2}>
              {availableTools.map((tool, index) => (
                <Grid item xs={12} key={index}>
                  <Paper sx={{ p: 2, border: 1, borderColor: 'divider' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="subtitle1" sx={inlineCodeStyle}>
                        {tool.name}
                      </Typography>
                      <Chip label="MCP Tool" size="small" variant="outlined" />
                    </Box>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      {tool.description}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                      <Typography variant="caption" sx={inlineCodeStyle}>
                        <strong>Parameters:</strong> {tool.parameters}
                      </Typography>
                      <Typography variant="caption" sx={inlineCodeStyle}>
                        <strong>Returns:</strong> {tool.returns}
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Quick Start Guide */}
      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🚀 Quick Start Guide
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="h6" color="primary">1</Typography>
                <Typography variant="subtitle2" gutterBottom>Get API Key</Typography>
                <Typography variant="body2" color="text.secondary">
                  Obtain your MCP API key from the SmartMCP administrator
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="h6" color="primary">2</Typography>
                <Typography variant="subtitle2" gutterBottom>Configure Client</Typography>
                <Typography variant="body2" color="text.secondary">
                  Choose your preferred client configuration method above
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
                <Typography variant="h6" color="primary">3</Typography>
                <Typography variant="subtitle2" gutterBottom>Start Building</Typography>
                <Typography variant="body2" color="text.secondary">
                  Use the available tools to integrate data into your applications
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Copy Success Snackbar */}
      <Snackbar
        open={!!copySuccess}
        autoHideDuration={2000}
        onClose={() => setCopySuccess('')}
        message={copySuccess}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
};

export default MCPConfiguration;