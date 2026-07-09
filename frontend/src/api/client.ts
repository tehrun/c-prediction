const base=import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
export async function getJson<T>(path:string):Promise<T>{const r=await fetch(`${base}${path}`); if(!r.ok) throw new Error(`API ${r.status}`); return r.json();}
