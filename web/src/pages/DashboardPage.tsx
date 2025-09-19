import { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import axios from 'axios';
import { List, ListItem, ListItemText, Typography, Paper, Link } from '@mui/material';

interface Report {
  id: string;
  file_name: string;
  created_at: { _seconds: number };
}

export default function DashboardPage() {
  const [reports, setReports] = useState<Report[]>([]);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const response = await axios.get('http://localhost:3002/reports');
        setReports(response.data);
      } catch (error) {
        console.error('Error fetching reports:', error);
      }
    };
    fetchReports();
  }, []);

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Analysis Reports
      </Typography>
      <List>
        {reports.length === 0 ? (
          <Typography>No reports found. Upload a document to get started.</Typography>
        ) : (
          reports.map(report => (
            <ListItem key={report.id} component={RouterLink} to={`/report/${report.id}`}>
              <ListItemText 
                primary={report.file_name} 
                secondary={`Analyzed on: ${new Date(report.created_at._seconds * 1000).toLocaleString()}`}
              />
            </ListItem>
          ))
        )}
      </List>
    </Paper>
  );
}