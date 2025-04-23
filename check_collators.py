import json
from pathlib import Path
from substrateinterface import SubstrateInterface
from decimal import Decimal, getcontext
from datetime import datetime

def load_config():
    with open(Path(__file__).parent / "system_chains_config.json", encoding='utf-8') as f:
        return json.load(f)

def format_deposit(chain_name, raw_deposit):
    """Convert raw Planck deposit to proper token format"""
    getcontext().prec = 8  # Set sufficient precision
    
    # Define token decimals for different chains
    decimals = {
        'polkadot': 10,
        'kusama': 12,
        'asset-hub-polkadot': 10,
        'bridge-hub-polkadot': 10,
        'collectives-polkadot': 10,
        'coretime-polkadot': 10,
        'people-polkadot': 10,
        'asset-hub-kusama': 12,
        'bridge-hub-kusama': 12,
        'coretime-kusama': 12,
        'encointer-kusama': 12,
        'people-kusama': 12,
    }
    
    # Find the appropriate decimal places
    dec_places = 10  # Default fallback
    for key in decimals:
        if key in chain_name.lower():
            dec_places = decimals[key]
            break
    
    # Convert from Planck to main units
    if raw_deposit:
        amount = Decimal(raw_deposit) / (10 ** dec_places)
        # Format with 4 decimal places and commas
        return f"{amount:,.4f}"
    return "0.0000"

def check_chain(chain_config):
    print(f"\n{'='*50}")
    print(f"🔍 Checking {chain_config['name']}")
    print(f"📡 RPC: {chain_config['rpc_url']}")
    print(f"{'='*50}")
    
    try:
        # Load collators for this chain
        with open(Path(__file__).parent / chain_config["collator_file"], encoding='utf-8') as f:
            collators = json.load(f)
        
        # Get current collators
        substrate = SubstrateInterface(url=chain_config["rpc_url"])
        invulnerables = substrate.query("CollatorSelection", "Invulnerables").value
        candidate_data = substrate.query("CollatorSelection", "CandidateList").value
        
        # Extract candidate addresses and deposits
        candidates = [c['who'] for c in candidate_data]
        deposits = {c['who']: c['deposit'] for c in candidate_data}
        
        # Get token symbol
        properties = substrate.rpc_request("system_properties", [])
        token_symbol = properties['result']['tokenSymbol'][0] if 'result' in properties else 'TOKEN'
        
        # Print results
        print(f"\n🔷 Invulnerable Collators ({len(invulnerables)})")
        for addr in invulnerables:
            print(f"  {addr[:10]}...{addr[-6:]} ({collators.get(addr, 'UNKNOWN')})")
        
        print(f"\n🔶 Candidate Collators ({len(candidates)}) [Deposit in {token_symbol}]")
        for addr in candidates:
            deposit = format_deposit(chain_config['name'], deposits.get(addr, 0))
            print(f"  {addr[:10]}...{addr[-6:]} ({collators.get(addr, 'UNKNOWN')}) - {deposit} {token_symbol}")
        
        # Check specific collators
        check_collator("LUCKYFRIDAY.IO", invulnerables, candidates, collators)
        
        # Detect unknowns
        unknown = [addr for addr in invulnerables + candidates if addr not in collators]
        if unknown:
            print("\n⚠️ Unknown Collators Detected:")
            for addr in unknown:
                deposit = format_deposit(chain_config['name'], deposits.get(addr, 0))
                print(f"  {addr} - {deposit} {token_symbol}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error checking {chain_config['name']}: {str(e)}")
        return False

def check_collator(name, invulnerables, candidates, collators):
    target_address = None
    for address, collator_name in collators.items():
        if name.lower() in collator_name.lower():
            target_address = address
            break
    
    if not target_address:
        print(f"\n❌ {name} not found in collator registry")
        return
    
    if target_address in invulnerables:
        print(f"\n✅ {name} found in Invulnerables")
    elif target_address in candidates:
        print(f"\n✅ {name} found in Candidates")
    else:
        print(f"\n❌ {name} not currently active")

print(f"🚀 Starting Collator Checks - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
config = load_config()
    
# Check all Polkadot chains
print("\n" + "🌐 POLKADOT CHAINS".center(50, "="))
for chain in config["polkadot_chains"]:
    check_chain(chain)
    
# Check all Kusama chains
print("\n" + "🔴 KUSAMA CHAINS".center(50, "="))
for chain in config["kusama_chains"]:
    check_chain(chain)
    
print("\n" + "✅ ALL CHECKS COMPLETE".center(50, "="))