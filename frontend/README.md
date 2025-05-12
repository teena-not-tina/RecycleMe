# RecycleMe Frontend

## Project Setup

### Prerequisites
- npm or yarn
- Node.js

### Installation
1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies
```bash
npm install
# or
yarn install
```

### Required Dependencies
- React
- Axios (for API calls)
- Firebase
- Tailwind CSS (for styling)

### Environment Setup
1. Create a `.env` file in the frontend directory
2. Add your Firebase configuration:
```
REACT_APP_FIREBASE_API_KEY=your_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_auth_domain
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
# Add other Firebase config values
```

### Running the Application
```bash
npm start
# or
yarn start
```

### Key Components
- StartPage: Initial landing page
- Scanner: Camera/upload interface for recyclable items
- Results: Display classification results
- Login: User authentication
- BatteryRedirect: Special handling for battery recycling

### API Integration
- Uses axios for backend communication
- Endpoints defined in `src/services/api.js`

### Firebase Integration
- Authentication managed in `src/services/firebase.js`
- Configured with Firebase SDK

## Troubleshooting
- Ensure all dependencies are installed
- Check console for any error messages
- Verify backend API is running
