import { ExternalLink, CheckCircle2, Clock3, XCircle, LoaderCircle } from 'lucide-react'

const copy={
 SUBMITTING:['Submitting transaction','Waiting for your wallet/provider to submit the contract call.'],
 SUBMITTED:['Transaction submitted','The transaction hash is available.'],
 WAITING_FOR_CONSENSUS:['Waiting for consensus','Do not resubmit the same write while consensus is processing.'],
 CONSENSUS_ACCEPTED:['Consensus accepted','The network accepted the transaction for execution.'],
 EXECUTION_SUCCEEDED:['Execution succeeded','The contract write completed without a reported execution error.'],
 EXECUTION_FAILED:['Execution failed','The contract/provider returned an execution error.'],
 REFRESHING_STATE:['Refreshing contract state','Reading the contract again to confirm the resulting state.'],
 STATE_REFRESHED:['State refreshed','The latest contract state was successfully loaded.'],
 STATE_REFRESH_FAILED:['State refresh failed','The transaction progressed, but the frontend could not confirm the latest state.'],
 SUBMISSION_FAILED:['Transaction submission failed','No successful transaction submission was confirmed.'],
 TIMEOUT:['Consensus is still processing','Do not blindly resubmit the same write. Check the explorer first.'],
}

export default function TxNotice({tx,explorerTx}){
 if(!tx)return null
 const [title,detail]=copy[tx.status]||['Transaction update',tx.status]
 const failed=/FAILED/.test(tx.status)
 const waiting=/SUBMITTING|WAITING|REFRESHING|TIMEOUT/.test(tx.status)
 const Icon=failed?XCircle:waiting?LoaderCircle:CheckCircle2
 return <div className={`tx-notice ${failed?'error':waiting?'amber':''}`}>
   <div><Icon/><div><b>{title}</b><span>{tx.functionName} · {detail}</span>{tx.error&&<pre className="tx-error">{tx.error}</pre>}</div></div>
   {tx.hash&&<a href={explorerTx(tx.hash)} target="_blank" rel="noreferrer">View transaction <ExternalLink size={14}/></a>}
 </div>
}
