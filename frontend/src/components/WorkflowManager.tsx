import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material';
import { 
  PlayArrow, 
  Security, 
  Speed, 
  Assessment,
  Add,
  Visibility
} from '@mui/icons-material';
import { apiService, Workflow } from '../services/apiService';

const WorkflowManager: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);

  useEffect(() => {
    const fetchWorkflows = async () => {
      try {
        const workflowList = await apiService.getWorkflows();
        setWorkflows(workflowList);
      } catch (err) {
        setError('Failed to load workflows');
        console.error('Workflow loading error:', err);
      }
    };

    fetchWorkflows();
  }, []);

  const handleExecuteWorkflow = async (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    setExecuteDialogOpen(true);
  };

  const executeWorkflow = async () => {
    if (!selectedWorkflow) return;

    setLoading(true);
    setError(null);

    try {
      const result = await apiService.executeWorkflow(selectedWorkflow.name, {});
      setExecutionResult(result);
      setExecuteDialogOpen(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to execute workflow');
    } finally {
      setLoading(false);
    }
  };

  const getWorkflowIcon = (template: string) => {
    switch (template) {
      case 'audit': return <Security color="primary" />;
      case 'smart_contract': return <Assessment color="secondary" />;
      case 'performance': return <Speed color="warning" />;
      default: return <PlayArrow />;
    }
  };

  const getStepChips = (steps: string[]) => {
    return steps.map((step, index) => (
      <Chip 
        key={index}
        label={step}
        size="small"
        variant="outlined"
        sx={{ mr: 0.5, mb: 0.5 }}
      />
    ));
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        ⚡ Workflow Manager
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setError('Workflow creation will be implemented in next phase')}
        >
          Create New Workflow
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {executionResult && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Workflow executed successfully! Execution ID: {executionResult.execution_id}
        </Alert>
      )}

      {loading && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress />
          <Typography variant="body2" sx={{ mt: 1 }}>
            Executing workflow...
          </Typography>
        </Box>
      )}

      <Grid container spacing={3}>
        {workflows.map((workflow, index) => (
          <Grid item xs={12} md={6} lg={4} key={index}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" alignItems="center" sx={{ mb: 2 }}>
                  {getWorkflowIcon(workflow.template)}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {workflow.name}
                  </Typography>
                </Box>

                <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                  {workflow.description}
                </Typography>

                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Steps ({workflow.steps.length}):
                </Typography>
                <Box sx={{ mb: 2 }}>
                  {getStepChips(workflow.steps)}
                </Box>

                <Box display="flex" gap={1}>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<PlayArrow />}
                    onClick={() => handleExecuteWorkflow(workflow)}
                    disabled={loading}
                  >
                    Execute
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={<Visibility />}
                    onClick={() => setError('Workflow details view will be implemented')}
                  >
                    View
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {workflows.length === 0 && !loading && (
        <Card>
          <CardContent>
            <Typography variant="body1" color="textSecondary" align="center">
              No workflows available. Create your first workflow to get started!
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Workflow Execution Dialog */}
      <Dialog 
        open={executeDialogOpen} 
        onClose={() => setExecuteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Execute Workflow: {selectedWorkflow?.name}
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            {selectedWorkflow?.description}
          </Typography>
          
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            This workflow will execute the following steps:
          </Typography>
          
          <List dense>
            {selectedWorkflow?.steps.map((step, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <Typography variant="body2">{index + 1}.</Typography>
                </ListItemIcon>
                <ListItemText primary={step} />
              </ListItem>
            ))}
          </List>

          <Alert severity="info" sx={{ mt: 2 }}>
            Workflow execution will start immediately and run in the background.
            You can monitor progress in real-time.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setExecuteDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={executeWorkflow}
            variant="contained"
            disabled={loading}
          >
            Execute Workflow
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowManager;
