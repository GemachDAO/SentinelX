import React from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { 
  Container, 
  AppBar, 
  Toolbar, 
  Typography, 
  Box, 
  Tabs, 
  Tab,
  IconButton
} from '@mui/material';
import { 
  Dashboard as DashboardIcon, 
  PlayArrow, 
  Workflow, 
  Assessment,
  Refresh 
} from '@mui/icons-material';
import Dashboard from './components/Dashboard';
import TaskExecution from './components/TaskExecution';
import WorkflowManager from './components/WorkflowManager';
import Reports from './components/Reports';
import './App.css';

function App() {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { label: 'Dashboard', path: '/', icon: <DashboardIcon /> },
    { label: 'Tasks', path: '/tasks', icon: <PlayArrow /> },
    { label: 'Workflows', path: '/workflows', icon: <Workflow /> },
    { label: 'Reports', path: '/reports', icon: <Assessment /> }
  ];

  const currentTab = tabs.findIndex(tab => tab.path === location.pathname);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    navigate(tabs[newValue].path);
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="App">
      <AppBar position="static" sx={{ backgroundColor: '#2c5aa0' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🛡️ SentinelX - Enterprise Security Framework
          </Typography>
          <IconButton color="inherit" onClick={handleRefresh}>
            <Refresh />
          </IconButton>
        </Toolbar>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider', backgroundColor: 'white' }}>
          <Tabs 
            value={currentTab >= 0 ? currentTab : 0} 
            onChange={handleTabChange}
            sx={{ px: 2 }}
          >
            {tabs.map((tab, index) => (
              <Tab 
                key={index}
                icon={tab.icon} 
                label={tab.label} 
                iconPosition="start"
              />
            ))}
          </Tabs>
        </Box>
      </AppBar>
      
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<TaskExecution />} />
          <Route path="/workflows" element={<WorkflowManager />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </Container>
    </div>
  );
}

export default App;
