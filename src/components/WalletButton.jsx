import { Wallet, LoaderCircle } from 'lucide-react'; import { shortAddress } from '../lib/format'
export default function WalletButton({wallet}){return <button className="wallet-btn" onClick={wallet.connect} disabled={wallet.busy}>{wallet.busy?<LoaderCircle className="spin" size={17}/>:<Wallet size={17}/>}{wallet.account?shortAddress(wallet.account):'Connect wallet'}</button>}
