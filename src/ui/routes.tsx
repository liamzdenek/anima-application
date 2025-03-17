/**
 * TanStack Router configuration
 */
import React from 'react';
import { createRootRoute, createRoute, createRouter, Outlet } from '@tanstack/react-router';
import { HomePage } from './pages/Home';
import { TestEntryPage } from './pages/TestEntry';
import { ResultsPage } from './pages/Results';
import styles from './App.module.css';

// Define the root layout component
const RootLayout: React.FC = () => (
  <div className={styles.appContainer}>
    <header className={styles.appHeader}>
      <h1>Active Patient Follow-Up Alert Dashboard</h1>
    </header>
    <main className={styles.appContent}>
      <Outlet/>
    </main>
    <footer className={styles.appFooter}>
      <p>© 2025 Liam Zdenek Demo for Anima Health</p>
    </footer>
  </div>
);

// Define the root route
export const rootRoute = createRootRoute({
  component: RootLayout,
});

// Define the index route (home page)
export const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
});

// Define the test entry route
export const testEntryRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/test-entry',
  component: TestEntryPage,
});

// Define the results route
export const resultsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/results',
  component: ResultsPage,
});

// Create the router instance
export const router = createRouter({
  routeTree: rootRoute.addChildren([
    indexRoute,
    testEntryRoute,
    resultsRoute,
  ]),
});

// Register the router for type safety
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}