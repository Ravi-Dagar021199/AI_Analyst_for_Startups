import { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import axios from 'axios';
import { List, ListItem, ListItemText, Typography, Paper } from '@mui/material';

interface Report {
  analysis_id: string;
  title: string;
  created_at: string;
  overall_score: number;
}

export default function DashboardPage() {
  const [reports, setReports] = useState<Report[]>([]);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        // Use the correct API base URL for our backend
        const API_BASE = `https://${window.location.hostname.replace('-5000-', '-8000-')}`;
        const response = await axios.get(`${API_BASE}/analyses/`);
        setReports(response.data.analyses || []);
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
            <ListItem key={report.analysis_id} component={RouterLink} to={`/report/${report.analysis_id}`}>
              <ListItemText 
                primary={report.title} 
                secondary={`Score: ${report.overall_score}/10 • Analyzed: ${new Date(report.created_at).toLocaleString()}`}
              />
            </ListItem>
          ))
        )}
      </List>
    </Paper>
  );
}