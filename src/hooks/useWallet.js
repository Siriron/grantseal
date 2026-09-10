import { useEffect, useState } from 'react'
import { STUDIONET_CONFIG } from '../config/chains'

export function useWallet(){
 const [account,setAccount]=useState(null); const [busy,setBusy]=useState(false); const [error,setError]=useState('')
 useEffect(()=>{ const eth=window.ethereum; if(!eth)return; eth.request({method:'eth_accounts'}).then(a=>setAccount(a?.[0]||null)).catch(()=>{}); const h=a=>setAccount(a?.[0]||null); eth.on?.('accountsChanged',h); return()=>eth.removeListener?.('accountsChanged',h) },[])
 const ensureChain=async()=>{ const eth=window.ethereum; if(!eth) throw new Error('No browser wallet detected. Install or enable an EIP-1193 wallet.'); try{ await eth.request({method:'wallet_switchEthereumChain',params:[{chainId:STUDIONET_CONFIG.chainId}]}) }catch(err){ if(err?.code===4902){ await eth.request({method:'wallet_addEthereumChain',params:[STUDIONET_CONFIG]}); await eth.request({method:'wallet_switchEthereumChain',params:[{chainId:STUDIONET_CONFIG.chainId}]}) }else if(err?.code===-32002){ await new Promise(r=>setTimeout(r,3000)) }else throw err } }
 const connect=async()=>{ const eth=window.ethereum; if(!eth){setError('No browser wallet detected.');return null}; setBusy(true);setError(''); try{await ensureChain();const a=await eth.request({method:'eth_requestAccounts'});setAccount(a?.[0]||null);return a?.[0]||null}catch(e){setError(e?.message||'Wallet connection failed');throw e}finally{setBusy(false)} }
 return {account,busy,error,connect,ensureChain}
}
