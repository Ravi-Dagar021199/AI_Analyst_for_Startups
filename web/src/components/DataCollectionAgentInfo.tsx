import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Card,
  CardContent,
  Chip,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Psychology as AIIcon,
  TrendingUp as TrendingIcon,
  Assessment as MetricsIcon,
  Business as BusinessIcon,
  DataObject as DataIcon,
  SmartToy as AgentIcon,
  Insights as InsightsIcon
} from '@mui/icons-material';

interface DataCollectionAgentInfoProps {
  open: boolean;
  onClose: () => void;
}

export default function DataCollectionAgentInfo({ open, onClose }: DataCollectionAgentInfoProps) {
  const dataSourceTypes = [
    {
      icon: <BusinessIcon color="primary" />,
      name: "Market Segment Detection",
      description: "Automatically identifies business category",
      examples: ["AI/ML", "FinTech", "HealthTech", "EdTech", "SaaS", "E-commerce"],
      confidence: "High Accuracy"
    },
    {
      icon: <TrendingIcon color="success" />,
      name: "Funding Stage Intelligence", 
      description: "Detects current investment stage",
      examples: ["Pre-seed", "Seed", "Series A", "Series B/C", "Growth"],
      confidence: "Pattern Recognition"
    },
    {
      icon: <MetricsIcon color="info" />,
      name: "Traction Analysis",
      description: "Extracts key business metrics",
      examples: ["Revenue figures", "User counts", "Growth rates", "Customer metrics"],
      confidence: "Data Extraction"
    }
  ];

  const aiUsageSteps = [
    {
      step: 1,
      title: "Document Processing",
      description: "Agent reads PDF/text and identifies document type (pitch deck, business plan, etc.)"
    },
    {
      step: 2, 
      title: "Intelligent Analysis",
      description: "Creates structured data sources with market segment, funding stage, and traction indicators"
    },
    {
      step: 3,
      title: "Context Enhancement", 
      description: "Provides organized templates and confidence scores to guide AI analysis"
    },
    {
      step: 4,
      title: "AI Integration",
      description: "Gemini AI uses enhanced context to generate more accurate investment insights"
    }
  ];

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <AgentIcon color="primary" fontSize="large" />
          <Box>
            <Typography variant="h5">Enhanced Data Collection Agent</Typography>
            <Typography variant="subtitle2" color="text.secondary">
              Intelligent Document Analysis & Context Enhancement
            </Typography>
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DataIcon color="primary" />
            What Data Does the Agent Collect?
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            The Enhanced Data Collection Agent automatically extracts and structures key information from your documents:
          </Typography>
          
          <Grid container spacing={2}>
            {dataSourceTypes.map((source, index) => (
              <Grid item key={index} xs={12} md={4}>
                <Card variant="outlined" sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      {source.icon}
                      <Typography variant="h6" sx={{ ml: 1, fontSize: '1rem' }}>
                        {source.name}
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ mb: 2 }}>
                      {source.description}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      {source.examples.map((example, idx) => (
                        <Chip 
                          key={idx}
                          label={example} 
                          size="small" 
                          sx={{ mr: 0.5, mb: 0.5 }}
                          variant="outlined"
                        />
                      ))}
                    </Box>
                    <Chip 
                      label={source.confidence} 
                      color="success" 
                      size="small"
                      variant="filled"
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AIIcon color="primary" />
            How AI Uses This Enhanced Data
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            The agent creates structured intelligence sources that guide AI analysis for more accurate insights:
          </Typography>
          
          <List>
            {aiUsageSteps.map((step, index) => (
              <ListItem key={index} sx={{ pl: 0 }}>
                <ListItemIcon>
                  <Box 
                    sx={{ 
                      width: 32, 
                      height: 32, 
                      borderRadius: '50%', 
                      backgroundColor: 'primary.main',
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 'bold'
                    }}
                  >
                    {step.step}
                  </Box>
                </ListItemIcon>
                <ListItemText 
                  primary={step.title}
                  secondary={step.description}
                />
              </ListItem>
            ))}
          </List>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Box>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <InsightsIcon color="primary" />
            Benefits in Your Investment Reports
          </Typography>
          
          <Card sx={{ backgroundColor: 'success.light', color: 'success.contrastText', mb: 2 }}>
            <CardContent>
              <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                ✅ More Accurate Analysis
              </Typography>
              <Typography variant="body2">
                AI receives structured context about market positioning, funding readiness, and traction metrics for precise evaluation.
              </Typography>
            </CardContent>
          </Card>

          <Card sx={{ backgroundColor: 'info.light', color: 'info.contrastText', mb: 2 }}>
            <CardContent>
              <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                🎯 Targeted Insights
              </Typography>
              <Typography variant="body2">
                Reports focus on relevant investment criteria based on detected business stage and market segment.
              </Typography>
            </CardContent>
          </Card>

          <Card sx={{ backgroundColor: 'warning.light', color: 'warning.contrastText' }}>
            <CardContent>
              <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
                ⚡ Enhanced Speed
              </Typography>
              <Typography variant="body2">
                Pre-structured data reduces AI processing time while improving analysis quality and consistency.
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} variant="contained">
          Got it!
        </Button>
      </DialogActions>
    </Dialog>
  );
}