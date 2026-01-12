const express = require('express');
const cors = require('cors');
const multer = require('multer');
require('dotenv').config();
const { initializeDatabase } = require('./config/database');
const purchaseOrderRoutes = require('./routes/purchaseOrder');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/api', purchaseOrderRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'API is running',
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        message: 'File size too large. Maximum size is 10MB'
      });
    }
  }
  
  if (err.message === 'Only image files are allowed') {
    return res.status(400).json({
      success: false,
      message: err.message
    });
  }

  console.error('Error:', err);
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: err.message
  });
});

// Initialize database and start server
const startServer = async () => {
  try {
    await initializeDatabase();
    
    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
      console.log(`Health check: http://localhost:${PORT}/health`);
      console.log(`API endpoints:`);
      console.log(`  POST   /api/purchase-order`);
      console.log(`  PUT    /api/purchase-order/:vehicleNumber`);
      console.log(`  GET    /api/purchase-order/:vehicleNumber`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

startServer();
