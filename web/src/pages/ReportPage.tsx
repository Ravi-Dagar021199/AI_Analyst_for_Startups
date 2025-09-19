import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, Typography, CircularProgress, Box, Paper } from '@mui/material';

interface ReportDetails {
  id: string;
  file_name: string;
  investment_memo: string;
}

export default function ReportPage() {
  const [report, setReport] = useState<ReportDetails | null>(null);
  const { id } = useParams<{ id: string }>();

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await axios.get(`http://localhost:3002/reports/${id}`);
        setReport(response.data);
      } catch (error) {
        console.error('Error fetching report:', error);
      }
    };
    if (id) {
      fetchReport();
    }
  }, [id]);

  if (!report) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" component="div" gutterBottom>
          {report.file_name}
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Investment Memo
        </Typography>
        <Paper variant="outlined" sx={{ p: 2, mt: 1, whiteSpace: 'pre-wrap', background: '#f9f9f9' }}>
          <Typography variant="body2">
            {report.investment_memo}
          </Typography>
        </Paper>
      </CardContent>
    </Card>
  );
}