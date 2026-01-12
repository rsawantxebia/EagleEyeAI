# Purchase Order API

A RESTful web API for managing purchase orders with PostgreSQL database.

## Features

- Create purchase orders with image upload, text, dimensions, and vehicle number
- Update purchase order status to "Delivered" by vehicle number
- PostgreSQL database storage with image support

## Prerequisites

- Node.js (v14 or higher)
- PostgreSQL (v12 or higher)
- npm or yarn

## Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Update `.env` file with your PostgreSQL credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=purchase_order_db
DB_USER=postgres
DB_PASSWORD=your_password
PORT=3000
```

4. Create the PostgreSQL database:
```sql
CREATE DATABASE purchase_order_db;
```

5. Start the server:
```bash
npm start
```

The server will automatically create the required table on first run.

## API Endpoints

### 1. Create Purchase Order
**POST** `/api/purchase-order`

Creates a new purchase order record.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `purchaseOrderNumber` (required): Purchase order number
  - `image` (optional): Image file
  - `text` (optional): Text content
  - `imageDimension` (optional): Image dimensions as string
  - `vehicleNumber` (required): Vehicle number

**Example using cURL:**
```bash
curl -X POST http://localhost:3000/api/purchase-order \
  -F "purchaseOrderNumber=PO12345" \
  -F "text=Sample order text" \
  -F "imageDimension=1920x1080" \
  -F "vehicleNumber=ABC123" \
  -F "image=@/path/to/image.jpg"
```

**Example using JavaScript (FormData):**
```javascript
const formData = new FormData();
formData.append('purchaseOrderNumber', 'PO12345');
formData.append('text', 'Sample order text');
formData.append('imageDimension', '1920x1080');
formData.append('vehicleNumber', 'ABC123');
formData.append('image', imageFile);

fetch('http://localhost:3000/api/purchase-order', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

**Response:**
```json
{
  "success": true,
  "message": "Purchase order created successfully",
  "data": {
    "id": 1,
    "purchase_order_number": "PO12345",
    "vehicle_number": "ABC123",
    "status": "Pending",
    "created_at": "2024-01-15T10:30:00.000Z"
  }
}
```

### 2. Update Purchase Order Status
**PUT** `/api/purchase-order/:vehicleNumber`

Updates the status of purchase order(s) to "Delivered" based on vehicle number.

**Request:**
- Method: `PUT`
- URL Parameter: `vehicleNumber` (required)

**Example using cURL:**
```bash
curl -X PUT http://localhost:3000/api/purchase-order/ABC123
```

**Example using JavaScript:**
```javascript
fetch('http://localhost:3000/api/purchase-order/ABC123', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**Response:**
```json
{
  "success": true,
  "message": "Purchase order status updated to Delivered",
  "data": [
    {
      "id": 1,
      "purchase_order_number": "PO12345",
      "vehicle_number": "ABC123",
      "status": "Delivered",
      "updated_at": "2024-01-15T11:00:00.000Z"
    }
  ]
}
```

### 3. Get Purchase Orders (Bonus)
**GET** `/api/purchase-order/:vehicleNumber`

Retrieves all purchase orders for a given vehicle number.

**Example:**
```bash
curl http://localhost:3000/api/purchase-order/ABC123
```

## Database Schema

The API automatically creates the following table:

```sql
CREATE TABLE purchase_orders (
  id SERIAL PRIMARY KEY,
  purchase_order_number VARCHAR(255) NOT NULL,
  image BYTEA,
  text TEXT,
  image_dimension VARCHAR(255),
  vehicle_number VARCHAR(255) NOT NULL,
  status VARCHAR(50) DEFAULT 'Pending',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Error Handling

All endpoints return standardized JSON responses:

**Success Response:**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...}
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Error message",
  "error": "Detailed error information"
}
```

## Health Check

**GET** `/health`

Returns API health status.

```bash
curl http://localhost:3000/health
```

## Notes

- Maximum image file size: 10MB
- Only image files are accepted for upload
- Images are stored as BYTEA in PostgreSQL
- The status field defaults to "Pending" on creation
- Multiple purchase orders can have the same vehicle number
- Updating by vehicle number updates all orders with that vehicle number
