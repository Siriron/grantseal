import { useCallback, useEffect, useMemo, useState } from 'react'
import { createClient } from 'genlayer-js'
import { studionet } from 'genlayer-js/chains'
import { TransactionStatus } from 'genlayer-js/types'
import { CONTRACT_ADDRESS, explorerTx } from '../config/chains'
import { TimeoutError } from '../lib/errors'

const parse=(v)=>typeof v==='string'?JSON.parse(v):v
const readClient=createClient({chain:studionet})

export function useGrantSeal(account,ensureChain){
 const [counts,setCounts]=useState(null),[programs,setPrograms]=useState([]),[milestones,setMilestones]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState(''),[tx,setTx]=useState(null)
 const read=useCallback(async(fn,args=[])=>parse(await readClient.readContract({address:CONTRACT_ADDRESS,functionName:fn,args})),[])
 const refresh=useCallback(async()=>{ setLoading(true);setError('');try{const c=await read('get_counts');setCounts(c);const nextP=Math.max(1,Number(c.next_program_id||1));const nextM=Math.max(1,Number(c.next_milestone_id||1));const ps=await Promise.all([...Array(nextP-1)].map((_,i)=>read('get_program',[BigInt(i+1)]).catch(()=>null)));const ms=await Promise.all([...Array(nextM-1)].map((_,i)=>read('get_milestone',[BigInt(i+1)]).catch(()=>null)));setPrograms(ps.filter(Boolean).sort((a,b)=>Number(b.program_id)-Number(a.program_id)));setMilestones(ms.filter(Boolean).sort((a,b)=>Number(b.milestone_id)-Number(a.milestone_id)))}catch(e){setError(e?.message||'Unable to read GrantSeal')}finally{setLoading(false)} },[read])
 useEffect(()=>{refresh()},[refresh])
 const getCounts=useCallback(async()=>read('get_counts'),[read]); const getProgram=useCallback(async id=>read('get_program',[BigInt(id)]),[read]); const getMilestone=useCallback(async id=>read('get_milestone',[BigInt(id)]),[read])
 const write=useCallback(async(functionName,args)=>{ if(!account) throw new Error('Connect your wallet first.'); await ensureChain(); const client=createClient({chain:studionet,account,provider:window.ethereum}); if(typeof client.connect==='function') await client.connect('studionet'); let hash; try{hash=await client.writeContract({address:CONTRACT_ADDRESS,functionName,args,value:BigInt(0)})}catch(e){throw e}; setTx({hash,status:'PENDING',functionName}); try{const receipt=await client.waitForTransactionReceipt({hash,status:TransactionStatus.ACCEPTED,retries:120,interval:4000});setTx({hash,status:'ACCEPTED',functionName,receipt});await refresh();return {hash,receipt}}catch(e){setTx({hash,status:'TIMEOUT',functionName});throw new TimeoutError(hash)} },[account,ensureChain,refresh])
 return useMemo(()=>({counts,programs,milestones,loading,error,tx,refresh,getCounts,getProgram,getMilestone,write,explorerTx}),[counts,programs,milestones,loading,error,tx,refresh,getCounts,getProgram,getMilestone,write])
}
