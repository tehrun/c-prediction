import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getJson } from '../api/client';
import type { DataQualityEvent, IngestionRun, Overview } from '../types/api';

const STALE_AFTER_MINUTES = 15;

function formatDateTime(value: string | null | undefined) {
  if (!value) return 'Never';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined) return '—';
  return new Intl.NumberFormat().format(value);
}

function isStale(value: string | null | undefined) {
  if (!value) return true;
  const timestamp = new Date(value).getTime();
  return Number.isNaN(timestamp) || Date.now() - timestamp > STALE_AFTER_MINUTES * 60 * 1000;
}

function StateMessage({ title, detail, role }: { title: string; detail?: string; role?: 'alert' | 'status' }) {
  return (
    <div className="state-message" role={role}>
      <strong>{title}</strong>
      {detail ? <p>{detail}</p> : null}
    </div>
  );
}

function KpiCard({ label, value, helper, tone = 'neutral' }: { label: string; value: string | number; helper?: string; tone?: 'neutral' | 'good' | 'warn' | 'bad' }) {
  return (
    <article className={`card kpi-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      {helper ? <small>{helper}</small> : null}
    </article>
  );
}

function ExchangeStatusCard({ exchange }: { exchange: Overview['exchanges'][number] }) {
  const stale = isStale(exchange.last_seen_at);
  const tone = exchange.status === 'online' && !stale ? 'good' : exchange.status === 'degraded' || stale ? 'warn' : 'bad';

  return (
    <article className={`card exchange-card ${tone}`}>
      <div>
        <h3>{exchange.exchange}</h3>
        <span className="pill">{stale ? 'stale' : exchange.status}</span>
      </div>
      <p>Markets: {formatNumber(exchange.active_markets)}</p>
      <p>Last seen: {formatDateTime(exchange.last_seen_at)}</p>
      {exchange.message ? <small>{exchange.message}</small> : null}
    </article>
  );
}

function DashboardSkeleton() {
  return (
    <main>
      <h1>CryptoPilot Overview</h1>
      <StateMessage role="status" title="Loading overview…" detail="Fetching market, ingestion, and quality signals." />
      <section className="grid kpi-grid" aria-label="Loading KPI cards">
        {['Markets', 'Candles', 'Ingestion', 'Quality'].map((label) => (
          <div className="card skeleton" key={label}>{label}</div>
        ))}
      </section>
    </main>
  );
}

export function Dashboard() {
  const overview = useQuery({ queryKey: ['overview'], queryFn: () => getJson<Overview>('/api/v1/overview') });
  const runs = useQuery({ queryKey: ['ingestion-runs'], queryFn: () => getJson<IngestionRun[]>('/api/v1/ingestion/runs?limit=5') });
  const quality = useQuery({ queryKey: ['data-quality-events'], queryFn: () => getJson<DataQualityEvent[]>('/api/v1/data-quality/events?status=open&limit=5') });

  const error = overview.error ?? runs.error ?? quality.error;
  const staleOverview = useMemo(() => isStale(overview.data?.generated_at), [overview.data?.generated_at]);

  if (overview.isLoading || runs.isLoading || quality.isLoading) return <DashboardSkeleton />;
  if (error) return <main><h1>CryptoPilot Overview</h1><StateMessage role="alert" title="API error" detail={(error as Error).message} /></main>;
  if (!overview.data) return <main><h1>CryptoPilot Overview</h1><StateMessage title="No overview available" detail="The overview endpoint returned no payload." /></main>;

  const markets = overview.data.markets;
  const recentRuns = runs.data ?? [];
  const events = quality.data ?? [];

  return (
    <main>
      <header className="page-header">
        <div>
          <h1>CryptoPilot Overview</h1>
          <p>Operational snapshot for configured markets, exchanges, ingestion, and data quality.</p>
        </div>
        <span className={`pill ${staleOverview ? 'warn' : 'good'}`}>{staleOverview ? 'stale' : 'fresh'} · {formatDateTime(overview.data.generated_at)}</span>
      </header>

      {staleOverview ? <StateMessage title="Overview may be stale" detail={`The last overview was generated more than ${STALE_AFTER_MINUTES} minutes ago.`} /> : null}

      <section className="grid kpi-grid" aria-label="Key performance indicators">
        <KpiCard label="Active markets" value={formatNumber(overview.data.kpis.active_markets)} helper={`${formatNumber(overview.data.kpis.configured_markets)} configured`} tone="good" />
        <KpiCard label="Candles (24h)" value={formatNumber(overview.data.kpis.candles_24h)} helper="OHLCV rows ingested" />
        <KpiCard label="Stale markets" value={formatNumber(overview.data.kpis.stale_markets)} helper="Past freshness SLA" tone={overview.data.kpis.stale_markets ? 'warn' : 'good'} />
        <KpiCard label="Open warnings" value={formatNumber(overview.data.kpis.open_quality_events)} helper="Data-quality events" tone={overview.data.kpis.open_quality_events ? 'bad' : 'good'} />
      </section>

      <section>
        <h2>Exchange status</h2>
        {!overview.data.exchanges.length ? <StateMessage title="No exchanges configured" detail="Configure exchange connectors to populate this section." /> : <div className="grid exchange-grid">{overview.data.exchanges.map((exchange) => <ExchangeStatusCard exchange={exchange} key={exchange.exchange} />)}</div>}
      </section>

      <section className="panel">
        <h2>Market overview</h2>
        {!markets.length ? <StateMessage title="No market data yet" detail="Run backend bootstrap and OHLCV ingestion commands to populate markets." /> : (
          <table>
            <thead><tr><th>Exchange</th><th>Symbol</th><th>Last candle</th><th>24h candles</th><th>Status</th></tr></thead>
            <tbody>{markets.map((market) => <tr key={`${market.exchange}:${market.symbol}`}><td>{market.exchange}</td><td>{market.symbol}</td><td>{formatDateTime(market.latest_candle_at)}</td><td>{formatNumber(market.candles_24h)}</td><td><span className={`pill ${market.status === 'healthy' ? 'good' : market.status === 'stale' ? 'warn' : 'bad'}`}>{market.status}</span></td></tr>)}</tbody>
          </table>
        )}
      </section>

      <div className="grid two-column">
        <section className="panel"><h2>Recent ingestion runs</h2>{!recentRuns.length ? <StateMessage title="No ingestion runs" detail="Scheduled or manual ingestion runs will appear here." /> : <ul className="event-list">{recentRuns.map((run) => <li key={run.id}><strong>{run.exchange} · {run.symbol ?? 'all markets'}</strong><span className={`pill ${run.status === 'success' ? 'good' : run.status === 'running' ? 'warn' : 'bad'}`}>{run.status}</span><small>{formatDateTime(run.started_at)} → {formatDateTime(run.finished_at)} · rows {formatNumber(run.rows_ingested)}</small>{run.message ? <p>{run.message}</p> : null}</li>)}</ul>}</section>
        <section className="panel"><h2>Data-quality warnings</h2>{!events.length ? <StateMessage title="No open warnings" detail="No active data-quality events were returned." /> : <ul className="event-list">{events.map((event) => <li key={event.id}><strong>{event.severity.toUpperCase()} · {event.exchange} · {event.symbol}</strong><span className={`pill ${event.severity === 'info' ? 'good' : event.severity === 'warning' ? 'warn' : 'bad'}`}>{event.event_type}</span><small>{formatDateTime(event.detected_at)}</small><p>{event.message}</p></li>)}</ul>}</section>
      </div>
    </main>
  );
}
