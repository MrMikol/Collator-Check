import json
from pathlib import Path
from substrateinterface import SubstrateInterface
from datetime import datetime

def load_config():
    with open(Path(__file__).parent / "system_chains_config.json", encoding='utf-8') as f:
        return json.load(f)

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
        candidates = [c['who'] for c in substrate.query("CollatorSelection", "CandidateList").value]
        
        # Print results
        print(f"\n🔷 Invulnerable Collators ({len(invulnerables)})")
        for addr in invulnerables:
            print(f"  {addr[:10]}...{addr[-6:]} ({collators.get(addr, 'UNKNOWN')})")
        
        print(f"\n🔶 Candidate Collators ({len(candidates)})")
        for addr in candidates:
            print(f"  {addr[:10]}...{addr[-6:]} ({collators.get(addr, 'UNKNOWN')})")
        
        # Check specific collators
        check_collator("PARANODES.IO", invulnerables, candidates, collators)
        
        # Detect unknowns
        unknown = [addr for addr in invulnerables + candidates if addr not in collators]
        if unknown:
            print("\n⚠️ Unknown Collators Detected:")
            for addr in unknown:
                print(f"  {addr}")
        
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