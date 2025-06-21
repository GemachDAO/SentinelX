import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

export interface Task {
  name: string;
  description: string;
  category: string;
  parameters: { [key: string]: any };
  enabled: boolean;
}

export interface TaskExecution {
  execution_id: string;
  task_name: string;
  status: string;
  start_time: string;
  result?: any;
}

export interface Workflow {
  name: string;
  description: string;
  template: string;
  steps: string[];
}

class ApiService {
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async getTasks(): Promise<Task[]> {
    const response = await this.axiosInstance.get('/tasks');
    return response.data.tasks || [];
  }

  async getTaskInfo(taskName: string): Promise<Task> {
    const response = await this.axiosInstance.get(`/tasks/${taskName}/info`);
    return response.data;
  }

  async executeTask(taskName: string, parameters: any = {}): Promise<TaskExecution> {
    const response = await this.axiosInstance.post(`/tasks/${taskName}/run`, {
      parameters,
      async_execution: true,
    });
    return response.data;
  }

  async getExecutionStatus(executionId: string): Promise<any> {
    const response = await this.axiosInstance.get(`/executions/${executionId}/status`);
    return response.data;
  }

  async getWorkflows(): Promise<Workflow[]> {
    const response = await this.axiosInstance.get('/workflows');
    return response.data.workflows || [];
  }

  async executeWorkflow(workflowName: string, parameters: any = {}): Promise<any> {
    const response = await this.axiosInstance.post('/workflows/run', {
      workflow_name: workflowName,
      parameters,
    });
    return response.data;
  }

  async getReports(): Promise<any[]> {
    const response = await this.axiosInstance.get('/reports');
    return response.data.reports || [];
  }

  async getHealth(): Promise<any> {
    const response = await this.axiosInstance.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
