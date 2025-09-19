import { useState } from 'react';
import axios from 'axios';
import { Button, Box, Typography, TextField, Alert } from '@mui/material';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setErrorMessage('Please select a file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    setStatusMessage('Uploading...');
    setErrorMessage('');

    try {
      const response = await axios.post('http://localhost:8000/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setStatusMessage(response.data.message);
    } catch (error) {
      console.error('Error uploading file:', error);
      setErrorMessage('Error uploading file. Please try again.');
      setStatusMessage('');
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Pitch Deck
      </Typography>
      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
        <Button
          variant="contained"
          component="label"
        >
          Choose File
          <input
            type="file"
            hidden
            onChange={handleFileChange}
          />
        </Button>
        <TextField
          disabled
          value={file ? file.name : 'No file selected'}
          sx={{ ml: 2, flexGrow: 1 }}
        />
      </Box>
      <Button
        variant="contained"
        onClick={handleUpload}
        disabled={!file}
        sx={{ mt: 2 }}
      >
        Upload and Analyze
      </Button>
      {statusMessage && <Alert severity="success" sx={{ mt: 2 }}>{statusMessage}</Alert>}
      {errorMessage && <Alert severity="error" sx={{ mt: 2 }}>{errorMessage}</Alert>}
    </Box>
  );
}