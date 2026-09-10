export const shortAddress=(v='')=>v?`${v.slice(0,6)}…${v.slice(-4)}`:'—'
export const shortSha=(v='')=>v?`${v.slice(0,10)}…${v.slice(-6)}`:'—'
export const formatDate=(epoch)=>epoch?new Date(Number(epoch)*1000).toLocaleString(): '—'
export const lower=(v)=>String(v||'').toLowerCase()
export const sameAddress=(a,b)=>lower(a)===lower(b)
export const statusTone=(status='')=>({DRAFT:'slate',LOCKED:'blue',ACTIVE:'green',CLOSED:'slate',SUBMITTED:'amber',CHALLENGED:'red',RESOLVED:'purple',MET:'green',PARTIALLY_MET:'amber',NOT_MET:'red',INCONCLUSIVE:'slate'})[status]||'slate'
