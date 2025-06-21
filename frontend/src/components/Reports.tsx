import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  IconButton,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { 
  Download, 
  Visibility, 
  PictureAsPdf, 
  Code,
  Description,
  Refresh
} from '@mui/icons-material';
import { apiService } from '../services/apiService';

interface Report {
  id: string;
  name: string;
  type: string;
  task_name?: string;
  workflow_name?: string;
  created_at: string;
  file_size: number;
}

const Reports: React.FC = () => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const reportList = await apiService.getReports();
      setReports(reportList);
    } catch (err) {
      setError('Failed to load reports');
      console.error('Report loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getReportIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf': return <PictureAsPdf color="error" />;
      case 'html': return <Code color="primary" />;
      case 'json': return <Code color="secondary" />;
      case 'markdown': return <Description color="action" />;
      default: return <Description />;
    }
  };

  const getTypeColor = (type: string): any => {
    switch (type.toLowerCase()) {
      case 'pdf': return 'error';
      case 'html': return 'primary';
      case 'json': return 'secondary';
      case 'markdown': return 'default';
      default: return 'default';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  const filteredReports = reports.filter(report => 
    filterType === 'all' || report.type.toLowerCase() === filterType
  );

  const handleViewReport = (report: Report) => {
    setError(`Report viewing will be implemented in next phase for: ${report.name}`);
  };

  const handleDownloadReport = (report: Report) => {
    setError(`Report download will be implemented in next phase for: ${report.name}`);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Typography variant="h4">
          📊 Reports
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchReports}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="info" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Report Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Reports
              </Typography>
              <Typography variant="h4">
                {reports.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                PDF Reports
              </Typography>
              <Typography variant="h4">
                {reports.filter(r => r.type === 'pdf').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                HTML Reports
              </Typography>
              <Typography variant="h4">
                {reports.filter(r => r.type === 'html').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                JSON Reports
              </Typography>
              <Typography variant="h4">
                {reports.filter(r => r.type === 'json').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filter Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" gap={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Filter by Type</InputLabel>
              <Select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                label="Filter by Type"
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
                <MenuItem value="html">HTML</MenuItem>
                <MenuItem value="json">JSON</MenuItem>
                <MenuItem value="markdown">Markdown</MenuItem>
              </Select>
            </FormControl>
            <Typography variant="body2" color="textSecondary">
              Showing {filteredReports.length} of {reports.length} reports
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Reports Table */}
      <Card>
        <CardContent>
          {filteredReports.length === 0 ? (
            <Box textAlign="center" py={4}>
              <Typography variant="h6" color="textSecondary">
                {reports.length === 0 ? 'No reports available' : 'No reports match the current filter'}
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                {reports.length === 0 
                  ? 'Execute tasks or workflows to generate reports' 
                  : 'Try changing the filter to see more reports'}
              </Typography>
            </Box>
          ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Source</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Size</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredReports.map((report) => (
                  <TableRow key={report.id} hover>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getReportIcon(report.type)}
                        <Typography variant="body2">
                          {report.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={report.type.toUpperCase()} 
                        size="small"
                        color={getTypeColor(report.type)}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {report.task_name || report.workflow_name || 'Manual'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDate(report.created_at)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatFileSize(report.file_size)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <IconButton 
                        size="small" 
                        onClick={() => handleViewReport(report)}
                        title="View Report"
                      >
                        <Visibility />
                      </IconButton>
                      <IconButton 
                        size="small" 
                        onClick={() => handleDownloadReport(report)}
                        title="Download Report"
                      >
                        <Download />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Reports;
