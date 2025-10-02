import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { store } from './store/store';
import Dashboard from './components/dashboard/Dashboard';
import PDFUpload from './components/pdf/PDFUpload';
import PDFList from './components/pdf/PDFList';
import AnalysisResults from './components/analysis/AnalysisResults';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Layout from './components/layout/Layout';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/"
              element={
                <Layout>
                  <Dashboard />
                </Layout>
              }
            />
            <Route
              path="/upload"
              element={
                <Layout>
                  <PDFUpload />
                </Layout>
              }
            />
            <Route
              path="/pdfs"
              element={
                <Layout>
                  <PDFList />
                </Layout>
              }
            />
            <Route
              path="/analysis/:pdfId"
              element={
                <Layout>
                  <AnalysisResults />
                </Layout>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Router>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;
