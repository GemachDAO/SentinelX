import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material';
import Dashboard from './components/Dashboard';
import TaskExecution from './components/TaskExecution';
import WorkflowManager from './components/WorkflowManager';
import Reports from './components/Reports';
import './App.css';

function App() {
  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            🛡️ SentinelX - Enterprise Security Framework
          </Typography>
        </Toolbar>
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
