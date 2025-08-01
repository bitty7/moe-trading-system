# MoE Dashboard - React Frontend

A comprehensive, interactive React-based dashboard for visualizing MoE (Mixture of Experts) backtesting results. Built with TypeScript, Material-UI, and Recharts for a professional, enterprise-grade experience.

## Features

### 🎯 Core Dashboard Tabs
- **📊 Overview**: High-level system performance and key metrics
- **🧠 Expert Recommendations**: Expert recommendations and insights by year
- **⏰ Time Analysis**: Temporal analysis of system performance and patterns
- **💼 Portfolio Analysis**: Comprehensive portfolio performance and risk metrics
- **🏢 Company Metrics**: Individual company performance analysis with selection
- **🔍 Expert Performance**: Expert performance comparison by company
- **📈 Decision Analysis**: Expert decisions, confidence levels, and aggregation

### 🚀 Interactive Features
- **Rich Visualizations**: Interactive charts with zoom, pan, and hover details
- **Real-time Data**: Dynamic data loading and updates
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Professional UI**: Material-UI components with custom theming
- **Export Capabilities**: PNG, PDF, CSV export functionality

## Technology Stack

### Core Framework
- **React 18+**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **Material-UI (MUI)**: Professional UI components and theming
- **React Router**: Client-side routing and navigation

### Visualization Libraries
- **Recharts**: Interactive charts and graphs
- **MUI X Charts**: Advanced charting capabilities
- **MUI X Data Grid**: Professional data tables

### Data & State Management
- **Axios**: HTTP client for API calls
- **React Context**: Local state management
- **TypeScript Interfaces**: Type-safe data handling

## Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend API running (or mock data)

### Installation

1. **Install dependencies**:
```bash
cd frontend
npm install
```

2. **Start the development environment** (both server and React app):
```bash
npm run dev
```

3. **Open your browser** and navigate to `http://localhost:3000`

**Note**: The dashboard now includes a local Express server that reads JSON files from the `../logs/` directory. The server runs on port 3001 and serves the React app on port 3000.

### Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/                 # Static files
├── src/
│   ├── components/         # Reusable components
│   │   └── Layout/        # Layout components
│   ├── context/           # React context providers
│   │   └── DataContext.tsx # Data management
│   ├── pages/             # Page components
│   │   ├── Overview.tsx
│   │   ├── ExpertRecommendations.tsx
│   │   ├── TimeAnalysis.tsx
│   │   ├── PortfolioAnalysis.tsx
│   │   ├── CompanyMetrics.tsx
│   │   ├── ExpertPerformance.tsx
│   │   └── DecisionAnalysis.tsx
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── App.tsx            # Main app component
│   └── index.tsx          # App entry point
├── package.json
└── README.md
```

## Data Integration

### Data Integration

The dashboard includes a local Express server that reads JSON files directly from the `../logs/` directory structure:

```
logs/
├── backtest_20250801_132111_aa_aaau_aacg/
│   ├── config.json
│   ├── portfolio_daily.json
│   ├── tickers_daily.json
│   ├── trades.json
│   └── results.json
└── backtest_20250801_134341_aa_aaau_aacg/
    └── ...
```

### API Endpoints
The local server provides the following endpoints:

- `GET /api/runs` - List available backtest runs (scans logs directory)
- `GET /api/runs/{runId}` - Get specific run data (loads all JSON files)

### Data Structure
The dashboard works with the data structure defined in `docs/PERFORMANCE_LOGGING.md`:

```typescript
interface BacktestData {
  config: BacktestConfig;
  portfolio_daily: PortfolioDaily[];
  tickers_daily: Record<string, TickerDaily[]>;
  trades: Trade[];
  results: BacktestResults;
}
```

### Environment Variables
Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Development

### Adding New Features

1. **Create new page component** in `src/pages/`
2. **Add route** in `src/App.tsx`
3. **Add navigation item** in `src/components/Layout/Layout.tsx`
4. **Update types** in `src/context/DataContext.tsx` if needed

### Styling
- Use Material-UI's `sx` prop for component-specific styles
- Follow the theme defined in `src/App.tsx`
- Use the color palette and typography from the theme

### State Management
- Use `useData()` hook for accessing global state
- Add new state to `DataContext` if needed
- Keep component state local when possible

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## Performance Optimization

### Code Splitting
- Pages are automatically code-split by React Router
- Lazy load heavy components when needed

### Data Loading
- Implement caching for expensive API calls
- Use React Query for server state management
- Optimize chart rendering for large datasets

### Bundle Size
- Tree-shaking enabled for Material-UI
- Dynamic imports for heavy libraries
- Optimize images and assets

## Deployment

### Build
```bash
npm run build
```

### Serve
The build folder can be served by any static file server:
- Nginx
- Apache
- Netlify
- Vercel
- AWS S3 + CloudFront

### Environment Configuration
Set production environment variables:
```env
REACT_APP_API_URL=https://your-api-domain.com
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Kill existing process
   lsof -ti:3000 | xargs kill -9
   ```

2. **Dependencies issues**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **TypeScript errors**
   ```bash
   npm run build
   # Check for type errors
   ```

4. **API connection issues**
   - Check `REACT_APP_API_URL` environment variable
   - Verify backend is running
   - Check CORS configuration

## Future Enhancements

### Planned Features
- [ ] Advanced filtering and search
- [ ] Real-time data updates
- [ ] User authentication
- [ ] Custom dashboards
- [ ] Advanced export options
- [ ] Mobile app

### Performance Improvements
- [ ] Virtual scrolling for large datasets
- [ ] Web Workers for data processing
- [ ] Service Worker for caching
- [ ] Progressive Web App features

## License

This project is licensed under the MIT License.

## Support

For questions and support:
- Check the documentation in `docs/`
- Review the performance logging specification
- Open an issue on GitHub

---

**Note**: This React dashboard is designed to work with the MoE backtesting system. Ensure your backend API provides data in the format specified in `docs/PERFORMANCE_LOGGING.md`.
