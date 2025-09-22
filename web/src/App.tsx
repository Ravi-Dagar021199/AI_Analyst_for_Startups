import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CircularProgress, Box } from '@mui/material';
import { useAuth } from './auth/AuthProvider';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ReportPage from './pages/ReportPage';
import UploadPage from './pages/UploadPage';
import Layout from './components/Layout';

const theme = createTheme();

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Routes>
          <Route path="/login" element={!user ? <LoginPage /> : <Navigate to="/" />} />
          <Route path="/register" element={!user ? <RegisterPage /> : <Navigate to="/" />} />
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="upload" element={<UploadPage />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="report/:id" element={<ReportPage />} />
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;