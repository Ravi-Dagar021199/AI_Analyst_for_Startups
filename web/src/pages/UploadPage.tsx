import { useState } from 'react';
import axios from 'axios';
import { 
  Button, Box, Typography, TextField, Alert, Card, CardContent, 
  Tabs, Tab, CircularProgress, Chip, Divider
} from '@mui/material';
import DataCollectionAgentInfo from '../components/DataCollectionAgentInfo';

interface Analysis {
  analysis_id: string;
  status: string;
  created_at: string;
  analysis: {
    founder_profile: any;
    market_opportunity: any;
    unique_differentiator: any;
    business_metrics: any;
    overall_score: number;
    key_insights: string[];
    risk_flags: string[];
  };
  metadata: {
    title: string;
    source: string;
    text_length: string;
    processed_by: string;
    file_name?: string;
    data_sources_found?: number;
    enhanced_analysis?: boolean;
  };
}

export default function UploadPage() {
  const [tabValue, setTabValue] = useState(0);
  const [text, setText] = useState('');
  const [title, setTitle] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [agentInfoOpen, setAgentInfoOpen] = useState(false);

  // Use API proxy configuration for backend calls
  const API_BASE = '/api';

  const handleTextAnalysis = async () => {
    if (!text.trim()) {
      setErrorMessage('Please enter startup material text to analyze.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setAnalysis(null);

    try {
      const response = await axios.post(`${API_BASE}/ingest-text/`, {
        text: text.trim(),
        title: title || 'Startup Material',
        source: 'web_interface'
      });
      
      setAnalysis(response.data);
    } catch (error: any) {
      console.error('Error analyzing text:', error);
      setErrorMessage(error.response?.data?.detail || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileAnalysis = async () => {
    if (!file) {
      setErrorMessage('Please select a file to analyze.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setAnalysis(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', title || file.name);
      formData.append('source', 'file_upload');

      const response = await axios.post(`${API_BASE}/ingest-file/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setAnalysis(response.data);
    } catch (error: any) {
      console.error('Error analyzing file:', error);
      setErrorMessage(error.response?.data?.detail || 'File analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderAnalysisResults = () => {
    if (!analysis) return null;

    const { analysis: result } = analysis;

    return (
      <Box sx={{ mt: 3 }}>
        <Typography variant="h5" gutterBottom>
          Analysis Results
        </Typography>
        
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Overall Investment Score:</Typography>
              <Chip 
                label={`${result.overall_score}/10`}
                color={result.overall_score >= 7 ? 'success' : result.overall_score >= 5 ? 'warning' : 'error'}
                sx={{ ml: 2, fontWeight: 'bold' }}
              />
            </Box>
            
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
              {/* Founder Profile */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    👥 Founder Profile
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Experience:</strong> {result.founder_profile.experience}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Founder-Market Fit:</strong> {result.founder_profile.founder_market_fit}
                  </Typography>
                </CardContent>
              </Card>

              {/* Market Opportunity */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    🎯 Market Opportunity
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Problem:</strong> {result.market_opportunity.problem_description}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Market Size:</strong> {result.market_opportunity.market_size}
                  </Typography>
                </CardContent>
              </Card>

              {/* Unique Differentiator */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    🚀 Unique Differentiator
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Innovation:</strong> {result.unique_differentiator.core_innovation}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Defensibility:</strong> {result.unique_differentiator.defensibility}
                  </Typography>
                </CardContent>
              </Card>

              {/* Business Metrics */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    📊 Business Metrics
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Traction:</strong> {result.business_metrics.traction}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    <strong>Revenue Model:</strong> {result.business_metrics.revenue_model}
                  </Typography>
                </CardContent>
              </Card>
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Key Insights */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" color="success.main" gutterBottom>
                💡 Key Insights
              </Typography>
              {result.key_insights.map((insight, index) => (
                <Typography key={index} variant="body2" sx={{ mb: 1, ml: 2 }}>
                  • {insight}
                </Typography>
              ))}
            </Box>

            {/* Risk Flags */}
            <Box>
              <Typography variant="h6" color="error.main" gutterBottom>
                ⚠️ Risk Flags
              </Typography>
              {result.risk_flags.map((risk, index) => (
                <Typography key={index} variant="body2" sx={{ mb: 1, ml: 2 }}>
                  • {risk}
                </Typography>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Box>
    );
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 2 }}>
      <Typography variant="h4" gutterBottom>
        AI Startup Analyst - Data Collection Agent
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Upload founder materials to generate structured investment insights using AI analysis.
      </Typography>

      <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)} sx={{ mb: 3 }}>
        <Tab label="Text Analysis" />
        <Tab label="File Upload" />
      </Tabs>

      {tabValue === 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Enter Startup Material Text
            </Typography>
            <TextField
              fullWidth
              label="Document Title (optional)"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              sx={{ mb: 2 }}
              placeholder="e.g., EcoTech Pitch Deck, Series A Presentation"
            />
            <TextField
              fullWidth
              multiline
              rows={8}
              label="Startup Material Text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              sx={{ mb: 3 }}
              placeholder="Paste pitch deck content, founder updates, company description, or any startup materials here..."
            />
            <Button
              variant="contained"
              onClick={handleTextAnalysis}
              disabled={loading || !text.trim()}
              sx={{ minWidth: 200 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Analyze with AI'}
            </Button>
            {errorMessage && <Alert severity="error" sx={{ mt: 2 }}>{errorMessage}</Alert>}
          </CardContent>
        </Card>
      )}

      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Upload Document File
            </Typography>
            <TextField
              fullWidth
              label="Document Title (optional)"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              sx={{ mb: 2 }}
              placeholder="e.g., EcoTech Pitch Deck, Series A Presentation"
            />
            <Box sx={{ mb: 3 }}>
              <input
                accept=".pdf,.doc,.docx,.txt,.md"
                style={{ display: 'none' }}
                id="file-upload"
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <label htmlFor="file-upload">
                <Button variant="outlined" component="span" sx={{ mr: 2 }}>
                  📁 Choose File
                </Button>
              </label>
              {file && (
                <Typography variant="body2" component="span">
                  Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                </Typography>
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Supported formats: PDF, Word (.doc/.docx), Text (.txt), Markdown (.md)
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                onClick={handleFileAnalysis}
                disabled={loading || !file}
                sx={{ minWidth: 200 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Analyze File with AI'}
              </Button>
              <Button
                variant="outlined"
                onClick={() => setAgentInfoOpen(true)}
                sx={{ minWidth: 200 }}
                color="info"
              >
                🤖 Data Collection Agent
              </Button>
            </Box>
            {errorMessage && <Alert severity="error" sx={{ mt: 2 }}>{errorMessage}</Alert>}
          </CardContent>
        </Card>
      )}

      {renderAnalysisResults()}
      
      <DataCollectionAgentInfo 
        open={agentInfoOpen} 
        onClose={() => setAgentInfoOpen(false)} 
      />
    </Box>
  );
}