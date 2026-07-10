import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, test, vi } from 'vitest';
import App from '../App';

beforeEach(() => {
  vi.restoreAllMocks();
  history.pushState(null, '', '/');
});

test('dashboard loading and empty state', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (u: RequestInfo | URL) => {
    const path = String(u);
    if (path.includes('/market/universe')) return Response.json([]);
    if (path.includes('/market/data-health')) {
      return Response.json({
        status: 'unavailable',
        latest_candle: null,
        stale_markets: 0,
        message: 'No data',
      });
    }
    return Response.json({ status: 'healthy', details: { database: 'healthy' } });
  });

  render(<App />);

  expect(screen.getByText(/Loading dashboard/)).toBeInTheDocument();
  await screen.findByText(/No market data yet/);
});

test('universe rendering', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (u: RequestInfo | URL) => {
    const path = String(u);
    if (path.includes('/market/universe')) {
      return Response.json([
        {
          exchange: 'kraken',
          symbol: 'BTC/USD',
          base_currency: 'BTC',
          quote_currency: 'USD',
          active: true,
        },
      ]);
    }
    if (path.includes('/market/data-health')) {
      return Response.json({
        status: 'healthy',
        latest_candle: null,
        stale_markets: 0,
        message: null,
      });
    }
    return Response.json({ status: 'healthy', details: { database: 'healthy' } });
  });

  render(<App />);

  const bitcoinCells = await screen.findAllByText('BTC/USD');
  expect(bitcoinCells.length).toBeGreaterThan(0);
});

test('api error state', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 500 }));

  render(<App />);

  await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('API error'));
});
