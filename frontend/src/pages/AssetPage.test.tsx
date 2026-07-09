import { render, screen } from '@testing-library/react';
import { beforeEach, test, vi } from 'vitest';
import App from '../App';

beforeEach(() => {
  vi.restoreAllMocks();
  history.pushState(null, '', '/asset?symbol=BTC');
});

test('asset chart empty state', async () => {
  vi.spyOn(globalThis, 'fetch').mockImplementation(async (u: RequestInfo | URL) =>
    String(u).includes('candles')
      ? Response.json([])
      : Response.json({ status: 'unavailable', latest_candle: null, stale_markets: 0, message: null }),
  );

  render(<App />);

  await screen.findByText(/No candles available/);
});
