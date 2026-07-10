import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, expect, test, vi } from 'vitest';
import App from '../App';

const overview = {
  generated_at: new Date().toISOString(),
  kpis: {
    configured_markets: 2,
    active_markets: 1,
    candles_24h: 1440,
    stale_markets: 0,
    open_quality_events: 0,
  },
  exchanges: [
    {
      exchange: 'kraken',
      status: 'online',
      active_markets: 1,
      last_seen_at: new Date().toISOString(),
    },
  ],
  markets: [
    {
      exchange: 'kraken',
      symbol: 'BTC/USD',
      latest_candle_at: new Date().toISOString(),
      candles_24h: 24,
      status: 'healthy',
    },
  ],
};

beforeEach(() => {
  vi.restoreAllMocks();
  history.pushState(null, '', '/');
});

test('dashboard loading and empty state', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (u: RequestInfo | URL) => {
    const path = String(u);
    if (path.includes('/api/v1/overview')) return Response.json({ ...overview, exchanges: [], markets: [] });
    if (path.includes('/api/v1/ingestion/runs')) return Response.json([]);
    if (path.includes('/api/v1/data-quality/events')) return Response.json([]);
    return new Response('', { status: 404 });
  });

  render(<App />);

  expect(screen.getByText(/Loading overview/)).toBeInTheDocument();
  await screen.findByText(/No market data yet/);
  expect(screen.getByText(/No ingestion runs/)).toBeInTheDocument();
  expect(screen.getByText(/No open warnings/)).toBeInTheDocument();
});

test('overview rendering', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (u: RequestInfo | URL) => {
    const path = String(u);
    if (path.includes('/api/v1/overview')) return Response.json(overview);
    if (path.includes('/api/v1/ingestion/runs')) {
      return Response.json([
        {
          id: 'run-1',
          exchange: 'kraken',
          symbol: 'BTC/USD',
          status: 'success',
          started_at: new Date().toISOString(),
          finished_at: new Date().toISOString(),
          rows_ingested: 24,
        },
      ]);
    }
    if (path.includes('/api/v1/data-quality/events')) {
      return Response.json([
        {
          id: 'event-1',
          exchange: 'kraken',
          symbol: 'BTC/USD',
          event_type: 'gap',
          severity: 'warning',
          detected_at: new Date().toISOString(),
          message: 'Missing candle detected',
        },
      ]);
    }
    return new Response('', { status: 404 });
  });

  render(<App />);

  const bitcoinCells = await screen.findAllByText('BTC/USD');
  expect(bitcoinCells.length).toBeGreaterThan(0);
  expect(screen.getByRole('heading', { name: 'CryptoPilot Overview' })).toBeInTheDocument();
  expect(screen.getByText('2 configured')).toBeInTheDocument();
  expect(screen.getByText(/Missing candle detected/)).toBeInTheDocument();
});

test('api error state', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response('', { status: 500 }));

  render(<App />);

  await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('API error'));
});
