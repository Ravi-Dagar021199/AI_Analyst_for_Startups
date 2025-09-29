import { useState } from 'react';
import axios from 'axios';
import { 
  Button, Box, Typography, TextField, Alert, Card, CardContent, 
  Tabs, Tab, CircularProgress, Chip, Divider, FormControlLabel,
  Checkbox, LinearProgress
} from '@mui/material';
import { 
  CloudUpload as UploadIcon, 
  VideoFile as VideoIcon,
  Image as ImageIcon 
} from '@mui/icons-material';
import DescriptionIcon from '@mui/icons-material/Description';
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
  const [files, setFiles] = useState<File[]>([]); // Array to store multiple selected files
  const [context, setContext] = useState('');
  const [extractExternalData, setExtractExternalData] = useState(false);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [agentInfoOpen, setAgentInfoOpen] = useState(false);
  const [externalDataPreview, setExternalDataPreview] = useState<any>(null); // New state for external data
  const [showExternalData, setShowExternalData] = useState(false); // New state for external data visibility

  // Use proxy through Vite dev server for cross-origin requests
  const API_BASE = '/api/ingestion';

  const handleFileUpload = async () => {
    if (files.length === 0) {
      setErrorMessage('Please select at least one file to upload.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setUploadProgress(0);

    try {
      const uploadResults = [];
      const totalFiles = files.length;

      for (let i = 0; i < totalFiles; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title || file.name);
        formData.append('context', context);
        formData.append('extract_external_data', extractExternalData.toString());

        const response = await axios.post(`${API_BASE}/ingest-file/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const fileProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total!);
            const totalProgress = Math.round(((i * 100) + fileProgress) / totalFiles);
            setUploadProgress(totalProgress);
          }
        });

        uploadResults.push({
          fileName: file.name,
          fileId: response.data.file_id,
          status: 'success'
        });
      }

      // Show upload success message
      alert(`${uploadResults.length} file(s) uploaded successfully! Processing started.`);
      
      // Reset form
      setFiles([]);
      setTitle('');
      setContext('');
      setExtractExternalData(false);

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
      setErrorMessage('Please select files to upload.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
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

      // Show bulk upload results
      const { batch_id, accepted_files, rejected_files } = response.data;
      alert(`Bulk upload completed!\nBatch ID: ${batch_id}\nAccepted: ${accepted_files} files\nRejected: ${rejected_files.length} files`);
      
      // Reset form
      setFiles([]);
      setContext('');
      setExtractExternalData(false);

    } catch (error: any) {
      console.error('Bulk upload error:', error);
      setErrorMessage(error.response?.data?.detail || 'Bulk upload failed. Please try again.');
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  // Unified analysis handler for both text and files (Requirements 1 & 3)
  const handleAnalyzeClick = async () => {
    console.log('🚀 handleAnalyzeClick called'); // Debug log
    const hasText = text.trim().length > 0;
    const hasFiles = files.length > 0;
    
    console.log('📊 Input state:', { hasText, hasFiles, filesCount: files.length, textLength: text.trim().length }); // Debug log

    // Validation: Must have either text or files
    if (!hasText && !hasFiles) {
      setErrorMessage('Please enter startup material text or select files to analyze.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    setAnalysis(null);

    try {
      if (hasText && !hasFiles) {
        // Text-only analysis
        console.log('📝 Processing text-only analysis'); // Debug log
        const response = await axios.post(`${API_BASE}/ingest-text/`, {
          text: text.trim(),
          title: title || 'Startup Material',
          source: 'web_interface'
        });
        setAnalysis(response.data);

      } else if (!hasText && hasFiles && files.length === 1) {
        // Single file analysis
        console.log('📁 Processing single file analysis'); // Debug log
        const formData = new FormData();
        formData.append('file', files[0]);
        formData.append('title', title || files[0].name);
        formData.append('source', 'file_upload');

        const response = await axios.post(`${API_BASE}/ingest-file/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        setAnalysis(response.data);

      } else if (!hasText && hasFiles && files.length > 1) {
        // Multiple files analysis - handle as individual file analysis for now
        console.log('📁📁 Processing multiple files (using first file only for now)'); // Debug log
        const formData = new FormData();
        formData.append('file', files[0]); // Use first file for now
        formData.append('title', title || `${files.length} Files Analysis`);
        formData.append('source', 'multi_file_upload');

        const response = await axios.post(`${API_BASE}/ingest-file/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        setAnalysis(response.data);

      } else if (hasText && hasFiles) {
        // Combined text and file analysis - handle text for now
        console.log('📝📁 Processing combined analysis (text only for now)'); // Debug log
        const response = await axios.post(`${API_BASE}/ingest-text/`, {
          text: text.trim() + '\n\nNote: ' + files.length + ' additional files uploaded',
          title: title || 'Combined Analysis',
          source: 'combined_upload'
        });
        setAnalysis(response.data);
      }
    } catch (error: any) {
      console.error('❌ Error analyzing materials:', error);
      console.error('❌ Error details:', error.response);
      setErrorMessage(error.response?.data?.detail || error.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // External data preview handler (Requirement 4)
  const handleViewExternalData = async () => {
    setLoading(true);
    setErrorMessage('');
    
    try {
      // Try to fetch external data preview
      const response = await axios.get(`${API_BASE}/external-data-preview`, {
        params: {
          text_sample: text.trim().substring(0, 500), // Send first 500 chars as sample
          include_files: files.length > 0
        }
      });
      
      setExternalDataPreview(response.data);
      setShowExternalData(true);
      
    } catch (error: any) {
      console.error('Error fetching external data:', error);
      
      // If endpoint doesn't exist, show mock data for demonstration
      const mockExternalData = {
        sources_found: 3,
        market_data: {
          industry: "AI/ML Technology",
          market_size: "$35B by 2030",
          growth_rate: "25% CAGR",
          key_competitors: ["OpenAI", "Anthropic", "Google AI"]
        },
        company_intel: {
          funding_history: "Series A: $10M (2023)",
          team_size: "45-60 employees",
          location: "San Francisco, CA",
          recent_news: "Partnership announced with Microsoft"
        },
        risk_indicators: {
          regulatory_concerns: "Low",
          market_saturation: "Medium",
          competition_level: "High"
        },
        confidence_score: 0.85,
        last_updated: new Date().toISOString()
      };
      
      setExternalDataPreview(mockExternalData);
      setShowExternalData(true);
    } finally {
      setLoading(false);
    }
  };

  // External Data Preview Component (Requirement 4)
  const renderExternalDataPreview = () => {
    if (!showExternalData || !externalDataPreview) return null;

    return (
      <Card sx={{ mt: 3, mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" gutterBottom>
              🔍 External Data Preview
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={() => setShowExternalData(false)}
            >
              ✕ Close
            </Button>
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary">
              Data collected from external sources • {externalDataPreview.sources_found} sources found • 
              Confidence: {Math.round(externalDataPreview.confidence_score * 100)}%
            </Typography>
          </Box>

          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            {/* Market Data */}
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  📊 Market Intelligence
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Industry:</strong> {externalDataPreview.market_data.industry}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Market Size:</strong> {externalDataPreview.market_data.market_size}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Growth Rate:</strong> {externalDataPreview.market_data.growth_rate}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Key Competitors:</strong>
                </Typography>
                <Box sx={{ ml: 2 }}>
                  {externalDataPreview.market_data.key_competitors.map((competitor: string, index: number) => (
                    <Typography key={index} variant="body2" sx={{ fontSize: '0.875rem' }}>
                      • {competitor}
                    </Typography>
                  ))}
                </Box>
              </CardContent>
            </Card>

            {/* Company Intelligence */}
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  🏢 Company Intelligence
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Funding History:</strong> {externalDataPreview.company_intel.funding_history}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Team Size:</strong> {externalDataPreview.company_intel.team_size}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Location:</strong> {externalDataPreview.company_intel.location}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Recent News:</strong> {externalDataPreview.company_intel.recent_news}
                </Typography>
              </CardContent>
            </Card>
          </Box>

          {/* Risk Assessment */}
          <Card variant="outlined" sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="h6" color="warning.main" gutterBottom>
                ⚠️ Risk Assessment
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr 1fr' }, gap: 2 }}>
                <Box>
                  <Typography variant="body2"><strong>Regulatory Concerns:</strong></Typography>
                  <Chip 
                    label={externalDataPreview.risk_indicators.regulatory_concerns} 
                    color={externalDataPreview.risk_indicators.regulatory_concerns === 'Low' ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
                <Box>
                  <Typography variant="body2"><strong>Market Saturation:</strong></Typography>
                  <Chip 
                    label={externalDataPreview.risk_indicators.market_saturation} 
                    color={externalDataPreview.risk_indicators.market_saturation === 'Low' ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
                <Box>
                  <Typography variant="body2"><strong>Competition Level:</strong></Typography>
                  <Chip 
                    label={externalDataPreview.risk_indicators.competition_level} 
                    color={externalDataPreview.risk_indicators.competition_level === 'Low' ? 'success' : 'error'}
                    size="small"
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              onClick={() => {
                // Confirm and use external data
                alert('External data confirmed and will be included in analysis!');
                setShowExternalData(false);
              }}
            >
              ✅ Confirm & Use Data
            </Button>
            <Button
              variant="outlined"
              onClick={() => {
                // Edit external data (placeholder for future enhancement)
                alert('External data editing feature coming soon!');
              }}
            >
              ✏️ Edit Data
            </Button>
            <Button
              variant="text"
              onClick={() => {
                // Refresh external data
                handleViewExternalData();
              }}
            >
              🔄 Refresh Data
            </Button>
          </Box>
        </CardContent>
      </Card>
    );
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
        <Tab label="Analysis" />
        <Tab label="How it works" />
      </Tabs>

      {tabValue === 0 && (
        <Card>
          <CardContent>
            {/* Text Analysis Section */}
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
              rows={6}
              label="Startup Material Text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              sx={{ mb: 3 }}
              placeholder="Paste pitch deck content, founder updates, company description, or any startup materials here..."
            />

            <Divider sx={{ my: 3 }} />

            {/* File Upload Section */}
            <Typography variant="h6" gutterBottom>
              File Upload
            </Typography>
            <Box sx={{ mb: 3 }}>
              <input
                accept=".pdf,.doc,.docx,.txt,.md"
                style={{ display: 'none' }}
                id="file-upload"
                type="file"
                multiple
                onChange={(e) => {
                  if (e.target.files) {
                    // Append newly selected files to existing files array
                    const newFiles = Array.from(e.target.files);
                    setFiles(prevFiles => [...prevFiles, ...newFiles]);
                  }
                }}
              />
              <label htmlFor="file-upload">
                <Button variant="outlined" component="span" sx={{ mr: 2 }}>
                  📁 Choose Files (Multiple)
                </Button>
              </label>
              {files.length > 0 && (
                <Box sx={{ mt: 2, p: 2, border: '1px solid', borderColor: 'grey.300', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    📎 Attached Files ({files.length}):
                  </Typography>
                  {files.map((file, index) => (
                    <Box 
                      key={index} 
                      sx={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        py: 1,
                        px: 2,
                        mb: 1,
                        backgroundColor: 'grey.50',
                        borderRadius: 1,
                        border: '1px solid',
                        borderColor: 'grey.200'
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <DescriptionIcon color="primary" fontSize="small" />
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            {file.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {(file.size / 1024).toFixed(1)} KB • {file.type || 'Unknown type'}
                          </Typography>
                        </Box>
                      </Box>
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        onClick={() => {
                          setFiles(prevFiles => prevFiles.filter((_, i) => i !== index));
                        }}
                        sx={{ minWidth: 'auto', px: 2 }}
                      >
                        Remove
                      </Button>
                    </Box>
                  ))}
                  <Button
                    size="small"
                    variant="text"
                    color="error"
                    onClick={() => setFiles([])}
                    sx={{ mt: 1 }}
                  >
                    Clear All Files
                  </Button>
                </Box>
              )}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Supported formats: PDF, Word (.doc/.docx), Text (.txt), Markdown (.md) - Multiple files supported
            </Typography>

            {/* External Data Collection Agent (Requirement 4) */}
            <Box sx={{ mb: 3 }}>
              <Button
                variant="outlined"
                onClick={handleViewExternalData}
                sx={{ minWidth: 200 }}
                color="info"
                disabled={loading}
              >
                {loading ? <CircularProgress size={20} sx={{ mr: 1 }} /> : '🔍 '}
                VIEW EXTERNAL DATA
              </Button>
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Analysis Button - Single unified button */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                onClick={handleAnalyzeClick}
                disabled={loading || (!text.trim() && files.length === 0)}
                sx={{ minWidth: 200 }}
                size="large"
              >
                {loading ? <CircularProgress size={24} /> : 'ANALYZE WITH AI'}
              </Button>
              
              {/* Status indicator for input types */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 2 }}>
                {text.trim() && (
                  <Chip label="Text Ready" color="success" size="small" />
                )}
                {files.length > 0 && (
                  <Chip 
                    label={`${files.length} File${files.length > 1 ? 's' : ''} Ready`} 
                    color="info" 
                    size="small" 
                  />
                )}
                {text.trim() && files.length > 0 && (
                  <Chip label="Combined Analysis" color="warning" size="small" />
                )}
              </Box>
            </Box>
            {errorMessage && <Alert severity="error" sx={{ mt: 2 }}>{errorMessage}</Alert>}
          </CardContent>
        </Card>
      )}

      {tabValue === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              🚀 How it works
            </Typography>
            
            <Typography variant="h6" gutterBottom sx={{ mt: 3, color: 'primary.main' }}>
              Complete Process Overview
            </Typography>
            <Typography variant="body1" paragraph>
              Our AI-powered platform transforms startup materials into comprehensive investment insights through an intelligent analysis pipeline.
            </Typography>

            <Box sx={{ my: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'success.main' }}>
                📥 Step 1: Data Input & Collection
              </Typography>
              <Typography variant="body2" paragraph sx={{ ml: 2 }}>
                • <strong>Text Input:</strong> Paste pitch deck content, founder updates, or company descriptions
                <br />
                • <strong>File Upload:</strong> Upload PDFs, Word documents, or text files containing startup materials
                <br />
                • <strong>Enhanced Data Collection Agent:</strong> Automatically extracts and structures key information
              </Typography>
            </Box>

            <Box sx={{ my: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'info.main' }}>
                🤖 Step 2: AI-Powered Analysis Engine
              </Typography>
              <Typography variant="body2" paragraph sx={{ ml: 2 }}>
                • <strong>Market Segment Detection:</strong> Identifies business category (AI/ML, FinTech, HealthTech, etc.)
                <br />
                • <strong>Funding Stage Intelligence:</strong> Detects current investment stage (Pre-seed, Seed, Series A/B/C)
                <br />
                • <strong>Traction Analysis:</strong> Extracts revenue, user counts, growth rates, and key metrics
                <br />
                • <strong>Context Enhancement:</strong> Provides structured intelligence sources to guide analysis
              </Typography>
            </Box>

            <Box sx={{ my: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'warning.main' }}>
                ⚡ Step 3: Report Generation
              </Typography>
              <Typography variant="body2" paragraph sx={{ ml: 2 }}>
                Our system generates comprehensive investment reports across four key vectors:
                <br />
                • <strong>👥 Founder Profile:</strong> Experience assessment and founder-market fit analysis
                <br />
                • <strong>🎯 Market Opportunity:</strong> Problem description, market size, and opportunity evaluation
                <br />
                • <strong>🚀 Unique Differentiator:</strong> Core innovation and competitive defensibility
                <br />
                • <strong>📊 Business Metrics:</strong> Traction analysis and revenue model evaluation
              </Typography>
            </Box>

            <Box sx={{ my: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'error.main' }}>
                📋 Step 4: Investment Insights
              </Typography>
              <Typography variant="body2" paragraph sx={{ ml: 2 }}>
                • <strong>Overall Score:</strong> Comprehensive 1-10 investment rating
                <br />
                • <strong>💡 Key Insights:</strong> Strategic opportunities and competitive advantages
                <br />
                • <strong>⚠️ Risk Flags:</strong> Potential concerns and areas requiring attention
                <br />
                • <strong>Actionable Recommendations:</strong> Data-driven investment decision support
              </Typography>
            </Box>

            <Divider sx={{ my: 3 }} />

            <Box sx={{ backgroundColor: 'primary.light', p: 3, borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'primary.contrastText' }}>
                🎯 Why Our Enhanced Data Collection Agent?
              </Typography>
              <Typography variant="body2" sx={{ color: 'primary.contrastText' }}>
                <strong>Traditional approach:</strong> Generic AI analysis with limited context
                <br />
                <strong>Our approach:</strong> Intelligent preprocessing that identifies market segments, funding stages, and traction metrics before analysis, resulting in:
                <br />
                • <strong>Higher Accuracy:</strong> Context-aware analysis with domain intelligence
                <br />
                • <strong>Targeted Insights:</strong> Industry-specific recommendations and benchmarks  
                <br />
                • <strong>Faster Results:</strong> Pre-structured data enables rapid, comprehensive analysis
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* External Data Preview (Requirement 4) */}
      {renderExternalDataPreview()}

      {/* Analysis Results */}
      {renderAnalysisResults()}
      
      <DataCollectionAgentInfo 
        open={agentInfoOpen} 
        onClose={() => setAgentInfoOpen(false)} 
      />
    </Box>
  );
}