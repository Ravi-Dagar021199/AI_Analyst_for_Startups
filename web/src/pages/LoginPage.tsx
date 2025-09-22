import React, { useState } from 'react';
import { Box, Button, Typography, Alert, Paper, Divider } from '@mui/material';
import { useAuth } from '../auth/AuthProvider';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signInWithGoogle } = useAuth();
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError('');
      await signInWithGoogle();
      navigate('/upload'); // Redirect to main app after login
    } catch (error: any) {
      setError('Failed to sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 400, mx: 'auto', mt: 8, p: 3 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" gutterBottom align="center" color="primary">
          Welcome Back
        </Typography>
        <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
          Sign in to your AI Startup Analyst account
        </Typography>
        
        <Divider sx={{ mb: 3 }} />
        
        <Button
          fullWidth
          variant="contained"
          size="large"
          onClick={handleGoogleLogin}
          disabled={loading}
          sx={{ 
            py: 1.5,
            fontSize: '1.1rem',
            textTransform: 'none',
            mb: 2
          }}
        >
          {loading ? 'Signing in...' : '🔐 Continue with Google'}
        </Button>

        <Button
          fullWidth
          variant="outlined"
          size="large"
          onClick={() => navigate('/upload')}
          sx={{ 
            py: 1.5,
            fontSize: '1.1rem',
            textTransform: 'none'
          }}
        >
          🚀 Try Demo Mode
        </Button>
        
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}
        
        <Typography variant="body2" align="center" color="text.secondary" sx={{ mt: 3 }}>
          Secure authentication powered by Firebase
        </Typography>
      </Paper>
    </Box>
  );
}