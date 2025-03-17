/**
 * Main App component
 */
import React, { useEffect } from 'react';
import { RouterProvider } from '@tanstack/react-router';
import { router } from './routes';
import { checkApiHealth } from './api/client';

export function App() {
  // Check API health on app load
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const isHealthy = await checkApiHealth();
        if (!isHealthy) {
          console.error('API health check failed. The API may be unavailable.');
        }
      } catch (error) {
        console.error('Error checking API health:', error);
      }
    };
    
    checkHealth();
  }, []);
  
  return <RouterProvider router={router} />;
}