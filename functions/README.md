# Portfolio Genius Cloud Functions

This directory contains Firebase Cloud Functions written in Python for the Portfolio Genius application.

## Structure

```
functions/
├── main.py              # Main functions file
├── requirements.txt     # Python dependencies
├── firebase.json        # Firebase configuration
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Functions

### Health Check
- **Function**: `health`
- **Endpoint**: `/health`
- **Method**: GET
- **Description**: Basic health check that returns "OK" status
- **Response**: 
  ```json
  {
    "status": "OK",
    "message": "Portfolio Genius API is healthy",
    "timestamp": "2025-01-16T00:00:00Z"
  }
  ```

### API Gateway
- **Function**: `api`
- **Endpoint**: `/api/*`
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Description**: Main API gateway with CORS support and routing
- **Features**:
  - CORS headers for cross-origin requests
  - Route handling for different endpoints
  - 404 responses for unhandled routes
  - Preflight OPTIONS request handling

## Setup

1. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   ```

2. **Login to Firebase**:
   ```bash
   firebase login
   ```

3. **Initialize Firebase** (if not already done):
   ```bash
   firebase init functions
   ```

4. **Install Python dependencies**:
   ```bash
   cd functions
   pip install -r requirements.txt
   ```

## Deployment

1. **Deploy all functions**:
   ```bash
   firebase deploy --only functions
   ```

2. **Deploy specific function**:
   ```bash
   firebase deploy --only functions:health
   firebase deploy --only functions:api
   ```

## Testing

1. **Run functions locally**:
   ```bash
   firebase emulators:start --only functions
   ```

2. **Test health endpoint**:
   ```bash
   curl http://localhost:5001/your-project-id/us-central1/health
   ```

3. **Test API endpoint**:
   ```bash
   curl http://localhost:5001/your-project-id/us-central1/api/health
   ```

## Environment Variables

To set environment variables for your functions:

```bash
firebase functions:config:set someservice.key="THE API KEY"
```

## Adding New Functions

1. Create a new function in `main.py`:
   ```python
   @https_fn.on_request()
   def my_new_function(req):
       return jsonify({"message": "Hello from new function"})
   ```

2. Deploy the new function:
   ```bash
   firebase deploy --only functions:my_new_function
   ```

## Security

- Functions include CORS headers for web access
- Consider adding authentication middleware for protected endpoints
- Use Firebase Auth tokens for user authentication
- Validate all incoming requests

## Monitoring

- View function logs: `firebase functions:log`
- Monitor function performance in Firebase Console
- Set up alerting for function failures