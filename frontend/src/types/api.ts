export type Health = { status: string; details: Record<string, unknown> };
export type Market = { exchange: string; symbol: string; base_currency: string; quote_currency: string; active: boolean };
export type Candle = { opened_at: string; open: string; high: string; low: string; close: string; volume: string; trade_count: number | null };
export type DataHealth = { status: string; latest_candle: string | null; stale_markets: number; message: string | null };

export type Overview = {
  generated_at: string;
  kpis: {
    configured_markets: number;
    active_markets: number;
    candles_24h: number;
    stale_markets: number;
    open_quality_events: number;
  };
  exchanges: Array<{
    exchange: string;
    status: 'online' | 'degraded' | 'offline' | string;
    active_markets: number;
    last_seen_at: string | null;
    message?: string | null;
  }>;
  markets: Array<{
    exchange: string;
    symbol: string;
    latest_candle_at: string | null;
    candles_24h: number;
    status: 'healthy' | 'stale' | 'empty' | 'error' | string;
  }>;
};

export type IngestionRun = {
  id: string;
  exchange: string;
  symbol: string | null;
  status: 'success' | 'running' | 'failed' | string;
  started_at: string;
  finished_at: string | null;
  rows_ingested: number;
  message?: string | null;
};

export type DataQualityEvent = {
  id: string;
  exchange: string;
  symbol: string;
  event_type: string;
  severity: 'info' | 'warning' | 'critical' | string;
  detected_at: string;
  message: string;
};
