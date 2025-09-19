import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

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
    return <div>Loading report...</div>;
  }

  return (
    <div>
      <h2>{report.file_name}</h2>
      <h3>Investment Memo</h3>
      <pre style={{ whiteSpace: 'pre-wrap', background: '#f4f4f4', padding: '1rem' }}>
        {report.investment_memo}
      </pre>
    </div>
  );
}