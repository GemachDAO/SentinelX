import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  LinearProgress,
  Alert
} from '@mui/material';
import { Security, Speed, Assessment, CloudQueue } from '@mui/icons-material';
import { apiService } from '../services/apiService';

interface TaskStats {
  total: number;
  categories: { [key: string]: number };
}

const Dashboard: React.FC = () => {
  const [taskStats, setTaskStats] = useState<TaskStats>({ total: 0, categories: {} });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const tasks = await apiService.getTasks();
        const categories: { [key: string]: number } = {};
        
        tasks.forEach(task => {
          categories[task.category] = (categories[task.category] || 0) + 1;
        });

        setTaskStats({
          total: tasks.length,
          categories
        });
      } catch (err) {
        setError('Failed to load dashboard stats');
        console.error('Dashboard error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    {
      title: 'Total Tasks',
      value: taskStats.total,
      icon: <Security fontSize="large" />,
      color: '#2c5aa0'
    },
    {
      title: 'Audit Tasks',
      value: taskStats.categories.audit || 0,
      icon: <Assessment fontSize="large" />,
      color: '#28a745'
    },
    {
      title: 'Exploit Tasks',
      value: taskStats.categories.exploit || 0,
      icon: <Speed fontSize="large" />,
      color: '#dc3545'
    },
    {
      title: 'Blockchain Tasks',
      value: taskStats.categories.blockchain || 0,
      icon: <CloudQueue fontSize="large" />,
      color: '#ffc107'
    }
  ];

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Loading Dashboard...
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 4 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        🏠 Dashboard
      </Typography>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="textSecondary" gutterBottom variant="h6">
                      {card.title}
                    </Typography>
                    <Typography variant="h4" component="h2">
                      {card.value}
                    </Typography>
                  </Box>
                  <Box sx={{ color: card.color }}>
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🚀 Quick Actions
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  href="/tasks"
                >
                  Execute Tasks
                </Button>
                <Button
                  variant="outlined"
                  color="primary"
                  href="/workflows"
                >
                  Manage Workflows
                </Button>
                <Button
                  variant="outlined"
                  color="secondary"
                  href="/reports"
                >
                  View Reports
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 System Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="textSecondary">
                  API Status: ✅ Online
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Tasks Loaded: {taskStats.total}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Active Executions: 0
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
