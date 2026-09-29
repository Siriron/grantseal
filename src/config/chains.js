export const CONTRACT_ADDRESS = '0x257b34Eb0fc3C4fFBdd52775e08a95670C8382C7'
export const RPC_URL = 'https://studio.genlayer.com/api'
export const CHAIN_ID = 61999
export const EXPLORER_URL = 'https://explorer-studio.genlayer.com'
export const STUDIONET_CONFIG = {
  chainId: '0xF22F', chainName: 'GenLayer StudioNet', rpcUrls: [RPC_URL],
  nativeCurrency: { name: 'GEN', symbol: 'GEN', decimals: 18 }, blockExplorerUrls: [EXPLORER_URL]
}
export const explorerAddress = () => `${EXPLORER_URL}/address/${CONTRACT_ADDRESS}`
export const explorerTx = (hash) => `${EXPLORER_URL}/tx/${hash}`
