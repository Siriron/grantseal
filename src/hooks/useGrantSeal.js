import { useCallback, useEffect, useMemo, useState } from 'react'
import { createClient } from 'genlayer-js'
import { studionet } from 'genlayer-js/chains'
import { CONTRACT_ADDRESS, explorerTx } from '../config/chains'
import { TimeoutError } from '../lib/errors'

const parse=(v)=>typeof v==='string'?JSON.parse(v):v
const readClient=createClient({chain:studionet})
const errorText=(e)=>e?.shortMessage||e?.message||String(e||'Unknown contract error')

export function useGrantSeal(account,ensureChain){
 const [counts,setCounts]=useState(null),[programs,setPrograms]=useState([]),[milestones,setMilestones]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState(''),[tx,setTx]=useState(null)
 const read=useCallback(async(fn,args=[])=>parse(await readClient.readContract({address:CONTRACT_ADDRESS,functionName:fn,args})),[])
 const refresh=useCallback(async()=>{ setLoading(true);setError('');try{const c=await read('get_counts');setCounts(c);const nextP=Math.max(1,Number(c.next_program_id||1));const nextM=Math.max(1,Number(c.next_milestone_id||1));const ps=await Promise.all([...Array(nextP-1)].map((_,i)=>read('get_program',[BigInt(i+1)]).catch(()=>null)));const ms=await Promise.all([...Array(nextM-1)].map((_,i)=>read('get_milestone',[BigInt(i+1)]).catch(()=>null)));setPrograms(ps.filter(Boolean).sort((a,b)=>Number(b.program_id)-Number(a.program_id)));setMilestones(ms.filter(Boolean).sort((a,b)=>Number(b.milestone_id)-Number(a.milestone_id)))}catch(e){setError(errorText(e));throw e}finally{setLoading(false)} },[read])
 useEffect(()=>{refresh().catch(()=>{})},[refresh])
 const getCounts=useCallback(async()=>read('get_counts'),[read]); const getProgram=useCallback(async id=>read('get_program',[BigInt(id)]),[read]); const getMilestone=useCallback(async id=>read('get_milestone',[BigInt(id)]),[read])
 const write=useCallback(async(functionName,args)=>{
   if(!account) throw new Error('Connect your wallet first.')
   await ensureChain()
   const client=createClient({chain:studionet,account,provider:window.ethereum})
   if(typeof client.connect==='function') await client.connect('studionet')
   let hash
   try{
     setTx({status:'SUBMITTING',functionName})
     hash=await client.writeContract({address:CONTRACT_ADDRESS,functionName,args,value:BigInt(0)})
     setTx({hash,status:'SUBMITTED',functionName})
     setTx({hash,status:'WAITING_FOR_CONSENSUS',functionName})
   }catch(e){
     setTx({hash,status:'SUBMISSION_FAILED',functionName,error:errorText(e)})
     throw e
   }
   try{
     const receipt=await client.waitForDecision({hash,retries:120,interval:4000})
     setTx({hash,status:'CONSENSUS_ACCEPTED',functionName,receipt})
     // Consensus acceptance is not execution success. The 1.1.x SDK does
     // not export the newer isSuccessful helper, so inspect the materialized
     // execution result directly and never treat ACCEPTED alone as success.
     const executionResultName = receipt?.txExecutionResultName
       ?? receipt?.executionResult?.name
       ?? receipt?.executionResult
       ?? null
     const executionError = receipt?.executionError
       ?? receipt?.error
       ?? receipt?.revertReason
       ?? null
     if(executionError || (executionResultName && executionResultName !== 'FINISHED_WITH_RETURN')){
       const detail = executionError
         ? errorText(executionError)
         : `execution result: ${executionResultName}`
       const message = `Contract execution failed: ${detail}`
       setTx({hash,status:'EXECUTION_FAILED',functionName,receipt,error:message})
       throw new Error(message)
     }
     if(!executionResultName){
       const message = 'Consensus accepted, but the SDK did not expose a materialized execution result. Open the explorer transaction for the execution outcome.'
       setTx({hash,status:'EXECUTION_STATUS_UNKNOWN',functionName,receipt,error:message})
       throw new Error(message)
     }
     setTx({hash,status:'EXECUTION_SUCCEEDED',functionName,receipt})
     setTx({hash,status:'REFRESHING_STATE',functionName,receipt})
     try{
       await refresh()
       setTx({hash,status:'STATE_REFRESHED',functionName,receipt})
     }catch(e){
       setTx({hash,status:'STATE_REFRESH_FAILED',functionName,receipt,error:errorText(e)})
       throw e
     }
     return {hash,receipt}
   }catch(e){
     if(e instanceof TimeoutError) throw e
     const message=errorText(e)
     if(/timeout/i.test(message)){
       setTx({hash,status:'TIMEOUT',functionName,error:message})
       throw new TimeoutError(hash)
     }
     setTx(current=>current?.status==='EXECUTION_FAILED'||current?.status==='STATE_REFRESH_FAILED'?current:{hash,status:'EXECUTION_FAILED',functionName,error:message})
     throw e
   }
 },[account,ensureChain,refresh])
 return useMemo(()=>({counts,programs,milestones,loading,error,tx,refresh,getCounts,getProgram,getMilestone,write,explorerTx}),[counts,programs,milestones,loading,error,tx,refresh,getCounts,getProgram,getMilestone,write])
}
