import { statusTone } from '../lib/format'
export default function StatusPill({children}){return <span className={`pill ${statusTone(children)}`}>{String(children||'UNKNOWN').replaceAll('_',' ')}</span>}
