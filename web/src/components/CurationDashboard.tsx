"""
React Frontend Components for Data Curation Interface
"""
import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, TextField, Button,
  Chip, Grid, Divider, Alert, LinearProgress, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions,
  Tabs, Tab, List, ListItem, ListItemText, ListItemSecondaryAction
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Visibility as ViewIcon,
  CheckCircle as ApproveIcon
} from '@mui/icons-material';
import axios from 'axios';

// Types
interface Dataset {
  dataset_id: string;
  dataset_name: string;
  status: string;
  raw_content: string;
  curated_content: string;
  excluded_sections: string[];
  added_content: string;
  user_notes: string;
  content_tags: string[];
  priority_sections: string[];
}

interface FileInfo {
  file_id: string;
  content_length: number;
  has_external_data: boolean;
}

// Main Curation Dashboard
const CurationDashboard: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [curationDialogOpen, setCurationDialogOpen] = useState(false);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await axios.get('/api/curation/datasets/');
      setDatasets(response.data.datasets);
    } catch (error) {
      console.error('Failed to fetch datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDatasetSelect = async (datasetId: string) => {
    try {
      const response = await axios.get(`/api/curation/datasets/${datasetId}`);
      setSelectedDataset(response.data);
      setCurationDialogOpen(true);
    } catch (error) {
      console.error('Failed to fetch dataset details:', error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2 }}>Loading datasets...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Data Curation Dashboard
      </Typography>
      
      <Alert severity="info" sx={{ mb: 3 }}>
        Review and curate your processed data before AI analysis. 
        Remove irrelevant sections, add context, and organize content for optimal results.
      </Alert>

      <Grid container spacing={3}>
        {datasets.map((dataset) => (
          <Grid item xs={12} md={6} lg={4} key={dataset.dataset_id}>
            <DatasetCard 
              dataset={dataset} 
              onSelect={() => handleDatasetSelect(dataset.dataset_id)}
            />
          </Grid>
        ))}
      </Grid>

      {selectedDataset && (
        <CurationDialog
          dataset={selectedDataset}
          open={curationDialogOpen}
          onClose={() => setCurationDialogOpen(false)}
          onSave={() => {
            setCurationDialogOpen(false);
            fetchDatasets();
          }}
        />
      )}
    </Box>
  );
};

// Individual Dataset Card
const DatasetCard: React.FC<{
  dataset: Dataset;
  onSelect: () => void;
}> = ({ dataset, onSelect }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'in_progress': return 'warning';
      case 'completed': return 'success';
      case 'ready_for_ai': return 'primary';
      default: return 'default';
    }
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {dataset.dataset_name}
        </Typography>
        
        <Chip 
          label={dataset.status.replace('_', ' ').toUpperCase()} 
          color={getStatusColor(dataset.status)}
          size="small"
          sx={{ mb: 2 }}
        />

        <Typography variant="body2" color="text.secondary" gutterBottom>
          Content Length: {dataset.curated_content?.length || 0} characters
        </Typography>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          Tags: {dataset.content_tags?.length || 0}
        </Typography>

        <Box sx={{ mt: 2 }}>
          <Button 
            variant="outlined" 
            startIcon={<EditIcon />}
            onClick={onSelect}
            fullWidth
          >
            {dataset.status === 'ready_for_ai' ? 'Review' : 'Edit'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

// Curation Dialog
const CurationDialog: React.FC<{
  dataset: Dataset;
  open: boolean;
  onClose: () => void;
  onSave: () => void;
}> = ({ dataset, open, onClose, onSave }) => {
  const [tabValue, setTabValue] = useState(0);
  const [curatedContent, setCuratedContent] = useState(dataset.curated_content);
  const [addedContent, setAddedContent] = useState(dataset.added_content || '');
  const [userNotes, setUserNotes] = useState(dataset.user_notes || '');
  const [contentTags, setContentTags] = useState<string[]>(dataset.content_tags || []);
  const [newTag, setNewTag] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`/api/curation/datasets/${dataset.dataset_id}/curate`, {
        curated_content: curatedContent,
        added_content: addedContent,
        user_notes: userNotes,
        content_tags: contentTags
      });
      onSave();
    } catch (error) {
      console.error('Failed to save curation:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleApproveForAnalysis = async () => {
    try {
      await axios.post(`/api/curation/datasets/${dataset.dataset_id}/approve`);
      onSave();
    } catch (error) {
      console.error('Failed to approve dataset:', error);
    }
  };

  const addTag = () => {
    if (newTag.trim() && !contentTags.includes(newTag.trim())) {
      setContentTags([...contentTags, newTag.trim()]);
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setContentTags(contentTags.filter(tag => tag !== tagToRemove));
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        Curate Dataset: {dataset.dataset_name}
      </DialogTitle>
      
      <DialogContent>
        <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
          <Tab label="Content Editor" />
          <Tab label="Additional Context" />
          <Tab label="Tags & Notes" />
          <Tab label="Preview" />
        </Tabs>

        <Box sx={{ mt: 2 }}>
          {tabValue === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Edit Content
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                Review and edit the unified content. Remove irrelevant sections or correct any errors.
              </Alert>
              <TextField
                multiline
                rows={20}
                fullWidth
                value={curatedContent}
                onChange={(e) => setCuratedContent(e.target.value)}
                variant="outlined"
              />
            </Box>
          )}

          {tabValue === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Add Additional Context
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                Add any additional information that wasn't captured from the original files.
              </Alert>
              <TextField
                multiline
                rows={15}
                fullWidth
                value={addedContent}
                onChange={(e) => setAddedContent(e.target.value)}
                placeholder="Add additional context, background information, or clarifications..."
                variant="outlined"
              />
            </Box>
          )}

          {tabValue === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Tags and Notes
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Content Tags
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  {contentTags.map((tag) => (
                    <Chip
                      key={tag}
                      label={tag}
                      onDelete={() => removeTag(tag)}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    size="small"
                    value={newTag}
                    onChange={(e) => setNewTag(e.target.value)}
                    placeholder="Add tag"
                    onKeyPress={(e) => e.key === 'Enter' && addTag()}
                  />
                  <Button onClick={addTag} variant="outlined" size="small">
                    Add Tag
                  </Button>
                </Box>
              </Box>

              <Typography variant="subtitle1" gutterBottom>
                Curation Notes
              </Typography>
              <TextField
                multiline
                rows={8}
                fullWidth
                value={userNotes}
                onChange={(e) => setUserNotes(e.target.value)}
                placeholder="Add notes about your curation decisions, important context, or analysis priorities..."
                variant="outlined"
              />
            </Box>
          )}

          {tabValue === 3 && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Preview Final Content
              </Typography>
              <Alert severity="success" sx={{ mb: 2 }}>
                This is how your curated content will appear to the AI analysis engine.
              </Alert>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                    {curatedContent}
                    {addedContent && (
                      <>
                        {'\n\n=== ADDITIONAL CONTEXT ===\n'}
                        {addedContent}
                      </>
                    )}
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          )}
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>
          Cancel
        </Button>
        <Button 
          onClick={handleSave} 
          disabled={saving}
          variant="outlined"
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
        {dataset.status === 'completed' && (
          <Button 
            onClick={handleApproveForAnalysis}
            variant="contained"
            color="primary"
            startIcon={<ApproveIcon />}
          >
            Approve for Analysis
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CurationDashboard;