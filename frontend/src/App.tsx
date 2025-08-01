import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';

// Components
import Layout from './components/Layout/Layout';
import Overview from './pages/Overview';
import ExpertRecommendations from './pages/ExpertRecommendations';
import PortfolioAnalysis from './pages/PortfolioAnalysis';
import CompanyMetrics from './pages/CompanyMetrics';
import ExpertPerformance from './pages/ExpertPerformance';


// Context
import { DataProvider } from './context/DataContext';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 8,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <DataProvider>
        <Router>
          <Box sx={{ display: 'flex', minHeight: '100vh', width: '100%' }}>
            <Layout>
              <Routes>
                <Route path="/" element={<Overview />} />
                <Route path="/overview" element={<Overview />} />
                <Route path="/expert-recommendations" element={<ExpertRecommendations />} />
                <Route path="/portfolio-analysis" element={<PortfolioAnalysis />} />
                <Route path="/company-metrics" element={<CompanyMetrics />} />
                                        <Route path="/expert-performance" element={<ExpertPerformance />} />
              </Routes>
            </Layout>
          </Box>
        </Router>
      </DataProvider>
    </ThemeProvider>
  );
}

export default App;
