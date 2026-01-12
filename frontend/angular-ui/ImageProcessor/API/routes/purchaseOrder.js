const express = require('express');
const multer = require('multer');
const { pool } = require('../config/database');

const router = express.Router();

// Configure multer for file uploads (in memory)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    // Accept image files
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed'), false);
    }
  }
});

// First endpoint: Create Purchase Order
// POST /api/purchase-order
router.post('/purchase-order', upload.single('image'), async (req, res) => {
  try {
    const { purchaseOrderNumber, text, imageDimension, vehicleNumber } = req.body;
    const image = req.file ? req.file.buffer : null;

    // Validate required fields
    if (!purchaseOrderNumber || !vehicleNumber) {
      return res.status(400).json({
        success: false,
        message: 'purchaseOrderNumber and vehicleNumber are required fields'
      });
    }

    // Insert into database
    const query = `
      INSERT INTO purchase_orders 
      (purchase_order_number, image, text, image_dimension, vehicle_number, status)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING id, purchase_order_number, vehicle_number, status, created_at
    `;

    const values = [
      purchaseOrderNumber,
      image,
      text || null,
      imageDimension || null,
      vehicleNumber,
      'Pending'
    ];

    const result = await pool.query(query, values);

    res.status(201).json({
      success: true,
      message: 'Purchase order created successfully',
      data: result.rows[0]
    });

  } catch (error) {
    console.error('Error creating purchase order:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message
    });
  }
});

// Second endpoint: Update Purchase Order Status to Delivered
// PUT /api/purchase-order/:vehicleNumber
router.put('/purchase-order/:vehicleNumber', async (req, res) => {
  try {
    const { vehicleNumber } = req.params;

    if (!vehicleNumber) {
      return res.status(400).json({
        success: false,
        message: 'vehicleNumber is required'
      });
    }

    // Update status to Delivered
    const query = `
      UPDATE purchase_orders
      SET status = 'Delivered',
          updated_at = CURRENT_TIMESTAMP
      WHERE vehicle_number = $1
      RETURNING id, purchase_order_number, vehicle_number, status, updated_at
    `;

    const result = await pool.query(query, [vehicleNumber]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: `No purchase order found with vehicle number: ${vehicleNumber}`
      });
    }

    res.json({
      success: true,
      message: 'Purchase order status updated to Delivered',
      data: result.rows
    });

  } catch (error) {
    console.error('Error updating purchase order:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message
    });
  }
});

// Optional: Get purchase order by vehicle number
router.get('/purchase-order/:vehicleNumber', async (req, res) => {
  try {
    const { vehicleNumber } = req.params;

    const query = `
      SELECT id, purchase_order_number, text, image_dimension, 
             vehicle_number, status, created_at, updated_at
      FROM purchase_orders
      WHERE vehicle_number = $1
      ORDER BY created_at DESC
    `;

    const result = await pool.query(query, [vehicleNumber]);

    // Don't return image in JSON response (can create separate endpoint if needed)
    res.json({
      success: true,
      data: result.rows
    });

  } catch (error) {
    console.error('Error fetching purchase order:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message
    });
  }
});

module.exports = router;
