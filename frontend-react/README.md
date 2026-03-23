# Model Integration Demo - React Frontend

Modern React frontend with Vite for the Model Integration Demo application.

## Features

- **Two Separate Tabs**: Dedicated interfaces for T5 and CodeGen models
- **T5 Lexical Simplification**:
  - Input sentence and complex word
  - Adjustable parameters (k, num_beams)
  - Single model or comparison mode (V1 vs V2)
  - Example sentences for quick testing
  
- **CodeGen Code Generation**:
  - Code prompt input with syntax highlighting
  - Adjustable parameters (max_length, temperature, top_p)
  - Single model or comparison mode (V1 vs V2)
  - Example prompts for quick testing

- **Backend Health Monitoring**: Real-time status indicator
- **Model Information**: Display available models

## Tech Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client for API calls
- **CSS-in-JS**: Inline styling for component-based design

## Installation

### Using npm:

```bash
cd frontend-react
npm install
```

### Using yarn:

```bash
cd frontend-react
yarn install
```

## Running the Application

### Development Mode:

```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:5173`

### Using the startup script:

```bash
chmod +x ../start_frontend_react.sh
../start_frontend_react.sh
```

### Production Build:

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend-react/
├── src/
│   ├── components/
│   │   ├── T5Tab.jsx          # T5 lexical simplification interface
│   │   └── CodeGenTab.jsx     # CodeGen code generation interface
│   ├── services/
│   │   └── api.js             # API client functions
│   ├── App.jsx                # Main app with tab navigation
│   ├── main.jsx               # React entry point
│   └── index.css              # Global styles
├── public/
├── index.html
├── vite.config.js
└── package.json
```

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`. The Vite proxy configuration handles CORS automatically in development.

### Endpoints Used:

- `POST /predict/flan-t5`: T5 lexical simplification
- `POST /predict/codegen`: CodeGen code generation
- `POST /compare`: Model comparison (V1 vs V2)
- `GET /health`: Backend health check
- `GET /models`: Available models information

## Configuration

The API base URL can be configured in `src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## Development

The application uses hot module replacement (HMR) for instant updates during development. Changes to any component will be reflected immediately without page refresh.

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Troubleshooting

### Backend Connection Issues:

1. Ensure the FastAPI backend is running on port 8000
2. Check the API base URL in `src/services/api.js`
3. Verify CORS settings in the backend

### Port Already in Use:

If port 5173 is occupied, Vite will automatically try the next available port (5174, 5175, etc.)

## Notes

- The frontend expects the backend API to be running
- Model loading happens on the backend; first requests may be slower
- Large model responses may take time depending on parameters
