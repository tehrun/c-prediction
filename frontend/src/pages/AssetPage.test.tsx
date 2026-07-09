import {render,screen} from '@testing-library/react'; import {vi,test,expect,beforeEach} from 'vitest'; import App from '../App';
beforeEach(()=>{vi.restoreAllMocks(); history.pushState(null,'','/asset?symbol=BTC')});
test('asset chart empty state',async()=>{vi.spyOn(global,'fetch').mockImplementation((async (u:RequestInfo|URL)=>String(u).includes('candles')?Response.json([]):Response.json({status:'unavailable',latest_candle:null,stale_markets:0,message:null})) as typeof fetch); render(<App/>); await screen.findByText(/No candles available/);});
