import {QueryClient,QueryClientProvider} from '@tanstack/react-query'; import {Dashboard} from './pages/Dashboard'; import {AssetPage} from './pages/AssetPage';
const qc=new QueryClient(); export default function App(){return <QueryClientProvider client={qc}>{location.pathname.startsWith('/asset')?<AssetPage/>:<Dashboard/>}</QueryClientProvider>}
