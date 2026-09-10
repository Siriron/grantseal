export class TimeoutError extends Error {
  constructor(hash){ super('Consensus is taking longer than expected. Your transaction was submitted — check it directly in the explorer.'); this.name='TimeoutError'; this.txHash=hash; this.isTimeout=true }
}
export const messageFromError=(error)=>{
  if(!error) return 'Unknown error'
  if(error.shortMessage) return error.shortMessage
  if(error.message) return error.message
  return String(error)
}
