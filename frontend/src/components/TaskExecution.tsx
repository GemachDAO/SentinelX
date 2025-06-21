import React, { useState, useEffect, useCallback } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Alert,
  LinearProgress,
  Chip,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import { PlayArrow, Stop, ExpandMore, Info, Wifi, WifiOff } from '@mui/icons-material';
import { apiService, Task, TaskExecution as TaskExecutionType } from '../services/apiService';
import websocketService, { ExecutionUpdate } from '../services/websocketService';

const TaskExecution: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<string>('');
  const [parameters, setParameters] = useState<{ [key: string]: string }>({});
  const [loading, setLoading] = useState(false);
  const [execution, setExecution] = useState<TaskExecutionType | null>(null);
  const [executionStatus, setExecutionStatus] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState<string>('');

  // WebSocket event handlers
  const handleExecutionUpdate = useCallback((update: ExecutionUpdate) => {
    if (execution && update.execution_id === execution.execution_id) {
      setExecutionStatus(prev => ({
        ...prev,
        status: update.status,
        progress: update.progress || prev?.progress || 0,
        message: update.message || prev?.message || '',
        result: update.result || prev?.result,
        error: update.error || prev?.error
      }));

      setProgress(update.progress || 0);
      setStatusMessage(update.message || '');

      if (update.status === 'completed') {
        setResult(update.result);
        setLoading(false);
      } else if (update.status === 'failed') {
        setError(update.error || 'Task execution failed');
        setLoading(false);
      }
    }
  }, [execution]);

  const handleTaskStarted = useCallback((data: any) => {
    if (execution && data.execution_id === execution.execution_id) {
      setLoading(true);
      setProgress(0);
      setStatusMessage('Task started...');
    }
  }, [execution]);

  const handleTaskCompleted = useCallback((data: any) => {
    if (execution && data.execution_id === execution.execution_id) {
      setLoading(false);
      setProgress(100);
      setStatusMessage('Task completed successfully');
      setResult(data.result);
    }
  }, [execution]);

  const handleTaskFailed = useCallback((data: any) => {
    if (execution && data.execution_id === execution.execution_id) {
      setLoading(false);
      setError(data.error || 'Task execution failed');
      setStatusMessage('Task failed');
    }
  }, [execution]);

  const handleProgressUpdate = useCallback((data: any) => {
    if (execution && data.execution_id === execution.execution_id) {
      setProgress(data.progress || 0);
      setStatusMessage(data.message || '');
    }
  }, [execution]);

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const taskList = await apiService.getTasks();
        setTasks(taskList);
      } catch (err) {
        setError('Failed to load tasks');
        console.error('Task loading error:', err);
      }
    };

    fetchTasks();
  }, []);

  // WebSocket connection management
  useEffect(() => {
    const unsubscribeConnected = websocketService.subscribe('connected', () => {
      setWsConnected(true);
    });

    const unsubscribeDisconnected = websocketService.subscribe('disconnected', () => {
      setWsConnected(false);
    });

    const unsubscribeExecutionUpdate = websocketService.subscribe('execution_update', handleExecutionUpdate);
    const unsubscribeTaskStarted = websocketService.subscribe('task_started', handleTaskStarted);
    const unsubscribeTaskCompleted = websocketService.subscribe('task_completed', handleTaskCompleted);
    const unsubscribeTaskFailed = websocketService.subscribe('task_failed', handleTaskFailed);
    const unsubscribeProgressUpdate = websocketService.subscribe('progress_update', handleProgressUpdate);

    // Set initial connection status
    setWsConnected(websocketService.getConnectionStatus());

    return () => {
      unsubscribeConnected();
      unsubscribeDisconnected();
      unsubscribeExecutionUpdate();
      unsubscribeTaskStarted();
      unsubscribeTaskCompleted();
      unsubscribeTaskFailed();
      unsubscribeProgressUpdate();
    };
  }, [handleExecutionUpdate, handleTaskStarted, handleTaskCompleted, handleTaskFailed, handleProgressUpdate]);

  // Fallback polling for when WebSocket is not available
  useEffect(() => {
    let interval: number;
    
    // Only use polling fallback when WebSocket is not connected
    if (!wsConnected && execution && execution.status !== 'completed' && execution.status !== 'failed') {
      interval = window.setInterval(async () => {
        try {
          const status = await apiService.getExecutionStatus(execution.execution_id);
          setExecutionStatus(status);
          
          if (status.status === 'completed') {
            setResult(status.result);
            setLoading(false);
            setProgress(100);
          } else if (status.status === 'failed') {
            setError(status.error || 'Task execution failed');
            setLoading(false);
          }
        } catch (err) {
          console.error('Status check error:', err);
        }
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [execution, wsConnected]);

  const handleTaskSelect = async (taskName: string) => {
    setSelectedTask(taskName);
    setParameters({});
    setError(null);
    setResult(null);
    setExecution(null);
    setExecutionStatus(null);

    // Load task parameters
    try {
      const taskInfo = await apiService.getTaskInfo(taskName);
      const paramDefaults: { [key: string]: string } = {};
      
      Object.keys(taskInfo.parameters || {}).forEach(param => {
        paramDefaults[param] = '';
      });
      
      setParameters(paramDefaults);
    } catch (err) {
      console.error('Failed to load task info:', err);
    }
  };

  const handleParameterChange = (param: string, value: string) => {
    setParameters(prev => ({
      ...prev,
      [param]: value
    }));
  };

  const executeTask = async () => {
    if (!selectedTask) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const execution = await apiService.executeTask(selectedTask, parameters);
      setExecution(execution);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to execute task');
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'running': return 'primary';
      default: return 'default';
    }
  };

  const selectedTaskInfo = tasks.find(t => t.name === selectedTask);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        🎯 Task Execution
      </Typography>

      <Grid container spacing={3}>
        {/* Task Selection */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Select Task
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Task</InputLabel>
                <Select
                  value={selectedTask}
                  onChange={(e) => handleTaskSelect(e.target.value)}
                  label="Task"
                >
                  {tasks.map((task) => (
                    <MenuItem key={task.name} value={task.name}>
                      <Box>
                        <Typography variant="body1">{task.name}</Typography>
                        <Typography variant="caption" color="textSecondary">
                          {task.category} - {task.description.substring(0, 50)}...
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedTaskInfo && (
                <Box>
                  <Chip 
                    label={selectedTaskInfo.category} 
                    size="small" 
                    color="primary" 
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="textSecondary">
                    {selectedTaskInfo.description}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Parameters */}
        {selectedTask && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Parameters
                </Typography>
                
                {Object.keys(parameters).length === 0 ? (
                  <Typography variant="body2" color="textSecondary">
                    No parameters required for this task
                  </Typography>
                ) : (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {Object.keys(parameters).map((param) => (
                      <TextField
                        key={param}
                        label={param}
                        value={parameters[param]}
                        onChange={(e) => handleParameterChange(param, e.target.value)}
                        fullWidth
                        size="small"
                        helperText={`Parameter: ${param}`}
                      />
                    ))}
                  </Box>
                )}

                <Box sx={{ mt: 3 }}>
                  <Button
                    variant="contained"
                    startIcon={<PlayArrow />}
                    onClick={executeTask}
                    disabled={loading || !selectedTask}
                    fullWidth
                  >
                    {loading ? 'Executing...' : 'Execute Task'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Execution Status */}
        {(execution || loading) && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Execution Status
                </Typography>
                
                {executionStatus && (
                  <Box sx={{ mb: 2 }}>
                    <Box display="flex" alignItems="center" gap={2} sx={{ mb: 1 }}>
                      <Chip 
                        label={executionStatus.status} 
                        color={getStatusColor(executionStatus.status)}
                        size="small"
                      />
                      <Typography variant="body2">
                        Progress: {executionStatus.progress || 0}%
                      </Typography>
                    </Box>
                    
                    <LinearProgress 
                      variant="determinate" 
                      value={executionStatus.progress || 0}
                      sx={{ mb: 1 }}
                    />
                    
                    <Typography variant="caption" color="textSecondary">
                      Execution ID: {executionStatus.execution_id}
                    </Typography>
                  </Box>
                )}

                {loading && !executionStatus && (
                  <Box>
                    <LinearProgress />
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Starting task execution...
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Results */}
        {result && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  🎉 Execution Results
                </Typography>
                
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>View Results</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                      <pre style={{ whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </Paper>
                  </AccordionDetails>
                </Accordion>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Error Display */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default TaskExecution;
