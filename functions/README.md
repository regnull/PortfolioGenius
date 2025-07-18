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

The following Firebase functions are deployed:

| Function | Endpoint | Method |
|----------|----------|-------|
| `get_stock_price` | `/get_stock_price` | `POST` |
| `construct_portfolio` | `/construct_portfolio` | `POST` |
| `get_suggested_trades` | `/get_suggested_trades` | `GET` |
| `convert_suggested_trade` | `/convert_suggested_trade` | `POST` |
| `dismiss_suggested_trade` | `/dismiss_suggested_trade` | `POST` |
| `lookup_symbol` | `/lookup_symbol` | `POST` |
| `get_portfolio_advice` | `/get_portfolio_advice` | `POST` |

All endpoints expect a Firebase Auth bearer token and return JSON responses.

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
   firebase deploy --only functions:construct_portfolio
   ```

## Testing

1. **Run functions locally**:
   ```bash
   firebase emulators:start --only functions
   ```

2. **Test construct portfolio endpoint**:
   ```bash
   curl -X POST \
     http://localhost:5001/your-project-id/us-central1/construct_portfolio \
     -H "Content-Type: application/json" \
     -d '{"portfolio_goal": "Test goal"}'
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