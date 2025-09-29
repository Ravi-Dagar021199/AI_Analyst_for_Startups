import express from 'express';
import cors from 'cors';
import { createProxyMiddleware } from 'http-proxy-middleware';
import { Request, Response } from 'express';

const app = express();
const port = process.env.PORT || 3000;

// Environment configuration
const ENHANCED_INGESTION_URL = process.env.ENHANCED_INGESTION_URL || 'http://localhost:8000'; // Fixed to use port 8000
const DATA_CURATION_URL = process.env.DATA_CURATION_URL || 'http://localhost:3003';
const USER_SERVICE_URL = process.env.USER_SERVICE_URL || 'http://localhost:3001';
const REPORTING_SERVICE_URL = process.env.REPORTING_SERVICE_URL || 'http://localhost:3002';

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Enhanced routing with proxy middleware

// Enhanced Ingestion Service routes
app.use('/api/enhanced-ingestion', createProxyMiddleware({
  target: ENHANCED_INGESTION_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api/enhanced-ingestion': '',
  },
  onError: (err: any, req: Request, res: Response) => {
    console.error('Enhanced Ingestion Service proxy error:', err.message);
    res.status(503).json({ error: 'Enhanced Ingestion Service unavailable' });
  }
}));

// Data Curation Service routes
app.use('/api/curation', createProxyMiddleware({
  target: DATA_CURATION_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api/curation': '',
  },
  onError: (err: any, req: Request, res: Response) => {
    console.error('Data Curation Service proxy error:', err.message);
    res.status(503).json({ error: 'Data Curation Service unavailable' });
  }
}));

// User Service routes
app.use('/api/users', createProxyMiddleware({
  target: USER_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api/users': '',
  },
  onError: (err: any, req: Request, res: Response) => {
    console.error('User Service proxy error:', err.message);
    res.status(503).json({ error: 'User Service unavailable' });
  }
}));

// Reporting Service routes
app.use('/api/reports', createProxyMiddleware({
  target: REPORTING_SERVICE_URL,
  changeOrigin: true,
  pathRewrite: {
    '^/api/reports': '',
  },
  onError: (err: any, req: Request, res: Response) => {
    console.error('Reporting Service proxy error:', err.message);
    res.status(503).json({ error: 'Reporting Service unavailable' });
  }
}));

// Legacy routes (backward compatibility)
app.use('/api/ingest-text', createProxyMiddleware({
  target: 'http://localhost:8000', // Original ingestion service
  changeOrigin: true,
  pathRewrite: {
    '^/api': '',
  }
}));

// Health check with service status
app.get('/health', async (req: Request, res: Response) => {
  const services = {
    'enhanced-ingestion': ENHANCED_INGESTION_URL,
    'data-curation': DATA_CURATION_URL,
    'user-service': USER_SERVICE_URL,
    'reporting-service': REPORTING_SERVICE_URL
  };

  const status = {
    gateway: 'healthy',
    timestamp: new Date().toISOString(),
    services: {} as Record<string, string>
  };

  // Check service health (simplified)
  for (const [name, url] of Object.entries(services)) {
    try {
      const response = await fetch(`${url}/health`, { method: 'GET', signal: AbortSignal.timeout(2000) });
      status.services[name] = response.ok ? 'healthy' : 'unhealthy';
    } catch (error) {
      status.services[name] = 'unreachable';
    }
  }

  res.json(status);
});

// Enhanced system info endpoint
app.get('/api/system-info', (req: Request, res: Response) => {
  res.json({
    system: 'AI Startup Analyst - Enhanced',
    version: '2.0.0',
    features: [
      'Multi-modal file processing',
      'OCR and transcription',
      'Data curation interface',
      'External data integration',
      'Bulk upload support',
      'Real-time processing status'
    ],
    endpoints: {
      'POST /api/enhanced-ingestion/upload/single': 'Upload single file',
      'POST /api/enhanced-ingestion/upload/bulk': 'Bulk file upload',
      'POST /api/enhanced-ingestion/external-data/collect': 'Collect external data',
      'GET /api/enhanced-ingestion/files/status/{id}': 'Check file processing status',
      'POST /api/curation/datasets/create': 'Create curation dataset',
      'GET /api/curation/datasets/': 'List curation datasets',
      'PUT /api/curation/datasets/{id}/curate': 'Update dataset curation',
      'POST /api/curation/datasets/{id}/approve': 'Approve for analysis'
    },
    supported_formats: {
      documents: ['PDF', 'DOC', 'DOCX', 'TXT', 'MD'],
      presentations: ['PPT', 'PPTX'],
      images: ['JPG', 'PNG', 'TIFF', 'BMP'],
      videos: ['MP4', 'AVI', 'MOV', 'MKV'],
      audio: ['MP3', 'WAV', 'M4A', 'FLAC']
    }
  });
});

app.get('/', (req, res) => {
  res.send('Enhanced AI Startup Analyst API Gateway is running');
});

app.listen(port, () => {
  console.log(`🚀 Enhanced API Gateway running on port ${port}`);
  console.log(`📊 System endpoints:`);
  console.log(`   Health: http://localhost:${port}/health`);
  console.log(`   System Info: http://localhost:${port}/api/system-info`);
  console.log(`   Enhanced Ingestion: http://localhost:${port}/api/enhanced-ingestion/*`);
  console.log(`   Data Curation: http://localhost:${port}/api/curation/*`);
});