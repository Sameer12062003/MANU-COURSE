# Course MCQ Generator - Frontend

Modern React application for generating and taking Multiple Choice Questions from course materials.

## Features

- **Course Selection**: Interactive course browser with availability status
- **MCQ Generation**: Intuitive interface for specifying question parameters
- **Interactive Quiz**: Take generated quizzes with real-time scoring
- **Results Export**: Download quiz results in JSON format
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Modern UI**: Built with Chakra UI for consistent design

## Prerequisites

- Node.js 18.0.0 or higher
- npm 8.0.0 or higher
- Backend API running on localhost:8000

## Installation

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Environment Setup:**
```bash
# .env file is already configured for local development
# Modify REACT_APP_API_URL if backend runs on different port
```

## Running the Application

### Development Mode
```bash
npm run dev
```
Application will be available at: http://localhost:5173

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## Environment Variables

Create `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENV=development
```

## Usage

### 1. Course Selection
- View available courses with PDF status indicators
- Select a course to enable MCQ generation
- Refresh course list to detect new courses

### 2. MCQ Generation
- Enter course code (auto-filled when course selected)
- Use slider or input field to specify number of questions (1-20)
- Click "Generate MCQs" and wait for processing

### 3. Taking Quiz
- Answer questions by selecting radio button options
- Track progress with answered/total counter
- Submit quiz when ready to see results

### 4. Results & Export
- View score and performance breakdown
- See correct/incorrect answers with explanations
- Export results as JSON file for record keeping

## Component Architecture

### Main Components

- **App.jsx**: Main application container and state management
- **CourseList.jsx**: Course selection and display
- **MCQGenerator.jsx**: MCQ generation interface
- **MCQDisplay.jsx**: Quiz interface and results display

### Services

- **api.js**: HTTP client for backend communication with error handling

### Styling

- **Chakra UI**: Component library for consistent design
- **Custom CSS**: Additional styling in App.css and MCQGenerator.css

## API Integration

The frontend communicates with the FastAPI backend through these endpoints:

```javascript
// Get available courses
GET /api/v1/courses

// Get course information
GET /api/v1/courses/{courseCode}

// Generate MCQs
POST /api/v1/generate-mcqs
{
  "course_code": "CS101",
  "num_questions": 5
}
```

## Customization

### Theming

Modify the Chakra UI theme in `src/index.js`:

```javascript
const theme = extendTheme({
  colors: {
    brand: {
      500: '#your-primary-color',
      // ... other shades
    },
  },
});
```

### API Configuration

Update API base URL in `src/services/api.js`:

```javascript
const API_BASE_URL = 'https://your-api-domain.com/api/v1';
```

## Features in Detail

### Interactive Quiz System
- Real-time answer selection
- Progress tracking
- Immediate feedback on submission
- Detailed explanations for learning

### Export Functionality
- JSON format for easy parsing
- Includes all question data and user responses
- Timestamped for record keeping
- Compatible with learning management systems

### Responsive Design
- Mobile-first approach
- Adaptive layouts for all screen sizes
- Touch-friendly interface elements
- Optimized performance on mobile devices

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Performance

- Code splitting with React lazy loading
- Optimized bundle size with Vite
- Efficient re-renders with React hooks
- API request optimization with Axios interceptors

## Troubleshooting

### Common Issues

1. **API Connection Error**
   - Verify backend is running on localhost:8000
   - Check CORS configuration in backend
   - Confirm REACT_APP_API_URL in .env

2. **Build Failures**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Update Node.js to version 18+
   - Check for TypeScript errors

3. **Styling Issues**
   - Verify Chakra UI installation
   - Check for CSS conflicts
   - Clear browser cache

### Development Tips

- Use React Developer Tools for debugging
- Monitor network requests in browser DevTools
- Check console for JavaScript errors
- Use ESLint for code quality

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Dependencies

### Main Dependencies
- React 19.1.1 - UI library
- Chakra UI 3.2.2 - Component library
- Axios 1.7.7 - HTTP client

### Development Dependencies
- Vite 6.1.1 - Build tool
- ESLint 9.15.0 - Code linting

## License

MIT License - see LICENSE file for details.
