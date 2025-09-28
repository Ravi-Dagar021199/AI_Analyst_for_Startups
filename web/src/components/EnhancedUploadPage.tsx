"""
Enhanced Upload Page Component with Multi-Modal Support
"""
import React, { useState, useRef } from 'react';
import {
  Box, Card, CardContent, Typography, Button, TextField, 
  Tabs, Tab, Alert, CircularProgress, LinearProgress, FormControlLabel,
  Checkbox, Grid, Chip, List, ListItem, ListItemIcon, ListItemText,
  Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as DocIcon,
  VideoFile as VideoIcon,
  Image as ImageIcon,
  AudioFile as AudioIcon,
  PictureAsPdf as PdfIcon,
  InsertDriveFile as FileIcon
} from '@mui/icons-material';
import axios from 'axios';

interface UploadResponse {
  file_id: string;
  status: string;
  message: string;
  processing_started: boolean;
  estimated_completion: string;
}

interface BulkUploadResponse {
  batch_id: string;
  total_files: number;
  accepted_files: number;
  rejected_files: string[];
  processing_started: boolean;
}

const EnhancedUploadPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [files, setFiles] = useState<File[]>([]);
  const [context, setContext] = useState('');
  const [extractExternalData, setExtractExternalData] = useState(true);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResults, setUploadResults] = useState<any[]>([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);

  const API_BASE = '/api/enhanced-ingestion';

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const selectedFiles = Array.from(event.target.files);
      setFiles(selectedFiles);
      setErrorMessage('');
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    if (event.dataTransfer.files) {
      const droppedFiles = Array.from(event.dataTransfer.files);
      setFiles([...files, ...droppedFiles]);
      setErrorMessage('');
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    
    switch (extension) {
      case 'pdf':
        return <PdfIcon color="error" />;
      case 'doc':
      case 'docx':
        return <DocIcon color="primary" />;
      case 'ppt':
      case 'pptx':
        return <FileIcon color="warning" />;
      case 'mp4':
      case 'avi':
      case 'mov':
      case 'mkv':
        return <VideoIcon color="secondary" />;
      case 'mp3':
      case 'wav':
      case 'm4a':
        return <AudioIcon color="info" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'tiff':
        return <ImageIcon color="success" />;
      default:
        return <FileIcon />;
    }
  };

  const handleSingleUpload = async () => {
    if (files.length === 0) {
      setErrorMessage('Please select at least one file.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    setUploadProgress(0);
    setUploadResults([]);

    try {
      const results = [];

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', file.name);
        formData.append('context', context);
        formData.append('extract_external_data', extractExternalData.toString());

        const response = await axios.post(`${API_BASE}/upload/single`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
            const totalProgress = Math.round(((i * 100) + fileProgress) / files.length);
            setUploadProgress(totalProgress);
          }
        });

        results.push({
          fileName: file.name,
          fileId: response.data.file_id,
          status: response.data.status,
          estimatedCompletion: response.data.estimated_completion
        });
      }

      setUploadResults(results);
      setSuccessMessage(`Successfully uploaded ${results.length} files for processing!`);
      setFiles([]);
      setContext('');

    } catch (error: any) {
      console.error('Upload error:', error);
      setErrorMessage(error.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const handleBulkUpload = async () => {
    if (files.length === 0) {
      setErrorMessage('Please select files for bulk upload.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    setUploadProgress(0);

    try {
      const formData = new FormData();
      
      files.forEach(file => {
        formData.append('files', file);
      });
      formData.append('context', context);
      formData.append('extract_external_data', extractExternalData.toString());

      const response = await axios.post(`${API_BASE}/upload/bulk`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
          setUploadProgress(percentCompleted);
        }
      });

      const result: BulkUploadResponse = response.data;
      setSuccessMessage(
        `Bulk upload completed! Batch ID: ${result.batch_id}. ` +
        `Accepted: ${result.accepted_files} files. ` +
        `Rejected: ${result.rejected_files.length} files.`
      );

      if (result.rejected_files.length > 0) {
        setErrorMessage(`Rejected files: ${result.rejected_files.join(', ')}`);
      }

      setFiles([]);
      setContext('');

    } catch (error: any) {
      console.error('Bulk upload error:', error);
      setErrorMessage(error.response?.data?.detail || 'Bulk upload failed. Please try again.');
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const getSupportedFormatsHelp = () => (
    <Card variant="outlined" sx={{ mt: 2 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Supported File Formats
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" color="primary">Documents</Typography>
            <List dense>
              <ListItem>
                <ListItemIcon><PdfIcon fontSize="small" /></ListItemIcon>
                <ListItemText primary="PDF (with OCR support)" />
              </ListItem>
              <ListItem>
                <ListItemIcon><DocIcon fontSize="small" /></ListItemIcon>
                <ListItemText primary="Word (.doc, .docx)" />
              </ListItem>
              <ListItem>
                <ListItemIcon><FileIcon fontSize="small" /></ListItemIcon>
                <ListItemText primary="Text (.txt, .md)" />
              </ListItem>
            </List>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" color="secondary">Media</Typography>
            <List dense>
              <ListItem>
                <ListItemIcon><VideoIcon fontSize="small" /></ListItemIcon>
                <ListItemText primary="Video (.mp4, .avi, .mov)" />
              </ListItem>
              <ListItem>
                <ListItemIcon><AudioIcon fontSize="small" /></ListItemIcon>
                <ListItemText primary="Audio (.mp3, .wav, .m4a)" />
              </ListItem>
              <ListItem>
                <ListItemIcon><ImageIcon fontSize="small" /></ListItemIcon>
                <ListItemText primary="Images (.jpg, .png, .tiff)" />
              </ListItem>
            </List>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Enhanced Data Ingestion
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Upload startup materials for AI-powered analysis. Supports documents, presentations, 
        videos, audio files, and images with OCR and transcription capabilities.
      </Alert>

      <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
        <Tab label="File Upload" />
        <Tab label="Bulk Upload" />
        <Tab label="Help & Formats" />
      </Tabs>

      {/* File Upload Tab */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Single/Multiple File Upload
                </Typography>

                {/* File Drop Zone */}
                <Box
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  sx={{
                    border: '2px dashed #ccc',
                    borderRadius: 2,
                    p: 4,
                    textAlign: 'center',
                    cursor: 'pointer',
                    mb: 2,
                    '&:hover': {
                      backgroundColor: '#f5f5f5'
                    }
                  }}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <UploadIcon sx={{ fontSize: 48, color: '#ccc', mb: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Drop files here or click to browse
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Supports documents, presentations, videos, audio, and images
                  </Typography>
                </Box>

                <input
                  type="file"
                  ref={fileInputRef}
                  style={{ display: 'none' }}
                  multiple
                  onChange={handleFileSelect}
                  accept=".pdf,.doc,.docx,.txt,.md,.ppt,.pptx,.mp4,.avi,.mov,.mkv,.mp3,.wav,.m4a,.jpg,.jpeg,.png,.tiff,.bmp"
                />

                {/* Selected Files */}
                {files.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                      Selected Files ({files.length})
                    </Typography>
                    <List>
                      {files.map((file, index) => (
                        <ListItem key={index} divider>
                          <ListItemIcon>
                            {getFileIcon(file.name)}
                          </ListItemIcon>
                          <ListItemText
                            primary={file.name}
                            secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                          />
                          <Button
                            size="small"
                            onClick={() => removeFile(index)}
                            color="error"
                          >
                            Remove
                          </Button>
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {/* Context and Options */}
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Context (Optional)"
                  placeholder="Provide context about these files to improve processing accuracy..."
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  sx={{ mt: 2, mb: 2 }}
                />

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={extractExternalData}
                      onChange={(e) => setExtractExternalData(e.target.checked)}
                    />
                  }
                  label="Extract external data (company info, market data, etc.)"
                />

                {/* Upload Progress */}
                {loading && (
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress variant="determinate" value={uploadProgress} />
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Uploading... {uploadProgress}%
                    </Typography>
                  </Box>
                )}

                {/* Upload Button */}
                <Button
                  variant="contained"
                  size="large"
                  startIcon={loading ? <CircularProgress size={20} /> : <UploadIcon />}
                  onClick={handleSingleUpload}
                  disabled={loading || files.length === 0}
                  fullWidth
                  sx={{ mt: 2 }}
                >
                  {loading ? 'Uploading...' : `Upload ${files.length} File${files.length !== 1 ? 's' : ''}`}
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            {/* Results Panel */}
            {(successMessage || errorMessage || uploadResults.length > 0) && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Upload Results
                  </Typography>

                  {successMessage && (
                    <Alert severity="success" sx={{ mb: 2 }}>
                      {successMessage}
                    </Alert>
                  )}

                  {errorMessage && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      {errorMessage}
                    </Alert>
                  )}

                  {uploadResults.length > 0 && (
                    <List>
                      {uploadResults.map((result, index) => (
                        <ListItem key={index} divider>
                          <ListItemText
                            primary={result.fileName}
                            secondary={
                              <Box>
                                <Chip
                                  label={result.status}
                                  size="small"
                                  color={result.status === 'processing' ? 'primary' : 'default'}
                                />
                                <Typography variant="caption" display="block">
                                  ID: {result.fileId}
                                </Typography>
                                <Typography variant="caption" display="block">
                                  ETA: {result.estimatedCompletion}
                                </Typography>
                              </Box>
                            }
                          />
                        </ListItem>
                      ))}
                    </List>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      )}

      {/* Bulk Upload Tab */}
      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Bulk File Upload
            </Typography>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              Upload multiple files at once for batch processing. All files will be processed 
              with the same context and settings.
            </Alert>

            {/* Similar file selection UI but optimized for bulk */}
            <Box
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              sx={{
                border: '2px dashed #ccc',
                borderRadius: 2,
                p: 6,
                textAlign: 'center',
                cursor: 'pointer',
                mb: 3,
                '&:hover': {
                  backgroundColor: '#f5f5f5'
                }
              }}
              onClick={() => fileInputRef.current?.click()}
            >
              <UploadIcon sx={{ fontSize: 64, color: '#ccc', mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Drop Multiple Files Here
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Or click to select files for bulk upload
              </Typography>
              <Typography variant="body2" sx={{ mt: 2 }}>
                Selected: {files.length} files
              </Typography>
            </Box>

            <TextField
              fullWidth
              multiline
              rows={4}
              label="Batch Context"
              placeholder="Provide context that applies to all files in this batch..."
              value={context}
              onChange={(e) => setContext(e.target.value)}
              sx={{ mb: 2 }}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={extractExternalData}
                  onChange={(e) => setExtractExternalData(e.target.checked)}
                />
              }
              label="Extract external data for all files"
            />

            {loading && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress variant="determinate" value={uploadProgress} />
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Bulk uploading... {uploadProgress}%
                </Typography>
              </Box>
            )}

            <Button
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} /> : <UploadIcon />}
              onClick={handleBulkUpload}
              disabled={loading || files.length === 0}
              fullWidth
              sx={{ mt: 2 }}
            >
              {loading ? 'Uploading Batch...' : `Upload Batch (${files.length} files)`}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Help Tab */}
      {tabValue === 2 && (
        <Box>
          {getSupportedFormatsHelp()}
          
          <Card variant="outlined" sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Processing Features
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="OCR (Optical Character Recognition)"
                    secondary="Extracts text from image-based PDFs and image files"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Video/Audio Transcription"
                    secondary="Converts speech to text from video and audio files"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Document Parsing"
                    secondary="Extracts structured content from presentations and documents"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="External Data Integration"
                    secondary="Collects relevant external information based on content analysis"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

export default EnhancedUploadPage;