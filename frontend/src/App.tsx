import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import { Dashboard } from './pages/Dashboard';
import { AssetPage } from './pages/AssetPage';

export default function App() {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { retry: false } },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      {location.pathname.startsWith('/asset') ? <AssetPage /> : <Dashboard />}
    </QueryClientProvider>
  );
}
