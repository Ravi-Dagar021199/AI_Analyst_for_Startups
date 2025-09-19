import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

interface Report {
  id: string;
  file_name: string;
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
    <div>
      <h2>Analysis Reports</h2>
      <ul>
        {reports.map(report => (
          <li key={report.id}>
            <Link to={`/report/${report.id}`}>{report.file_name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
}