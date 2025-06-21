import React from 'react';
import { Typography, Box } from '@mui/material';

const Reports: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        📊 Reports
      </Typography>
      <Typography variant="body1">
        Report management interface will be implemented here.
        This will include report generation, viewing, and export capabilities.
      </Typography>
    </Box>
  );
};

export default Reports;
