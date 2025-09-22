import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { 
  Card, CardContent, Typography, CircularProgress, Box, Paper, 
  Chip, Divider, Grid, Alert
} from '@mui/material';

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
    processed_by: string;
  };
}

export default function ReportPage() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { id } = useParams<{ id: string }>();

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        setError('');
        // Use the correct API base URL for our backend
        const currentHost = window.location.hostname;
        let API_BASE;
        
        if (currentHost.includes('replit.dev')) {
          // In Replit environment, replace port in domain
          API_BASE = `https://${currentHost.replace('-5000-', '-8000-')}`;
        } else {
          // In local development
          API_BASE = 'http://localhost:8000';
        }
        
        const response = await axios.get(`${API_BASE}/analysis/${id}`);
        setAnalysis(response.data);
      } catch (error: any) {
        console.error('Error fetching analysis:', error);
        setError('Failed to load analysis. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchAnalysis();
    }
  }, [id]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading analysis...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!analysis) {
    return (
      <Box sx={{ mt: 4 }}>
        <Alert severity="warning">Analysis not found.</Alert>
      </Box>
    );
  }

  const { analysis: result } = analysis;

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 2 }}>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h4" gutterBottom>
            {analysis.metadata.title}
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 2 }}>
            <Chip 
              label={`Score: ${result.overall_score}/10`}
              color={result.overall_score >= 7 ? 'success' : result.overall_score >= 5 ? 'warning' : 'error'}
              size="large"
              sx={{ fontWeight: 'bold' }}
            />
            <Typography variant="body2" color="text.secondary">
              Analyzed: {new Date(analysis.created_at).toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Processed by: {analysis.metadata.processed_by}
            </Typography>
          </Box>
          
          <Divider sx={{ mb: 3 }} />
          
          <Grid container spacing={3}>
            {/* Founder Profile */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    👥 Founder Profile
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Experience:</strong> {result.founder_profile.experience}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Founder-Market Fit:</strong> {result.founder_profile.founder_market_fit}
                  </Typography>
                  
                  {result.founder_profile.strengths && result.founder_profile.strengths.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" color="success.main">Strengths:</Typography>
                      {result.founder_profile.strengths.map((strength: string, index: number) => (
                        <Typography key={index} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
                          • {strength}
                        </Typography>
                      ))}
                    </Box>
                  )}
                  
                  {result.founder_profile.concerns && result.founder_profile.concerns.length > 0 && (
                    <Box>
                      <Typography variant="subtitle2" color="warning.main">Concerns:</Typography>
                      {result.founder_profile.concerns.map((concern: string, index: number) => (
                        <Typography key={index} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
                          • {concern}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Market Opportunity */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    🎯 Market Opportunity
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Problem:</strong> {result.market_opportunity.problem_description}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Market Size:</strong> {result.market_opportunity.market_size}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Competition:</strong> {result.market_opportunity.competitive_landscape}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Validation:</strong> {result.market_opportunity.market_validation}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Unique Differentiator */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    🚀 Unique Differentiator
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Innovation:</strong> {result.unique_differentiator.core_innovation}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Defensibility:</strong> {result.unique_differentiator.defensibility}
                  </Typography>
                  
                  {result.unique_differentiator.competitive_advantages && 
                   result.unique_differentiator.competitive_advantages.length > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" color="success.main">Competitive Advantages:</Typography>
                      {result.unique_differentiator.competitive_advantages.map((advantage: string, index: number) => (
                        <Typography key={index} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
                          • {advantage}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Business Metrics */}
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    📊 Business Metrics
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Revenue Model:</strong> {result.business_metrics.revenue_model}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Traction:</strong> {result.business_metrics.traction}
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Growth:</strong> {result.business_metrics.growth_metrics}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Unit Economics:</strong> {result.business_metrics.unit_economics}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Divider sx={{ my: 4 }} />

          {/* Key Insights */}
          <Card variant="outlined" sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" color="success.main" gutterBottom>
                💡 Key Investment Insights
              </Typography>
              {result.key_insights.map((insight, index) => (
                <Typography key={index} variant="body2" sx={{ mb: 1.5, ml: 2 }}>
                  • {insight}
                </Typography>
              ))}
            </CardContent>
          </Card>

          {/* Risk Flags */}
          <Card variant="outlined">
            <CardContent>
              <Typography variant="h6" color="error.main" gutterBottom>
                ⚠️ Risk Flags & Concerns
              </Typography>
              {result.risk_flags.map((risk, index) => (
                <Typography key={index} variant="body2" sx={{ mb: 1.5, ml: 2 }}>
                  • {risk}
                </Typography>
              ))}
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </Box>
  );
}