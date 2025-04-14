import json
from pathlib import Path
from substrateinterface import SubstrateInterface
from datetime import datetime
from collections import defaultdict

def load_config():
    with open(Path(__file__).parent / "system_chains_config.json", encoding='utf-8') as f:
        return json.load(f)

def check_chain(chain_config, missing_trackers):
    chain_name = chain_config['name']
    rpc_url = chain_config['rpc_url']
    print(f"\n{'='*50}")
    print(f"🔍 Checking {chain_name}")
    print(f"📡 RPC: {rpc_url}")
    print(f"{'='*50}")
    
    try:
        # Load collators for this chain
        with open(Path(__file__).parent / chain_config["collator_file"], encoding='utf-8') as f:
            collators = json.load(f)
        
        # Get current collators
        substrate = SubstrateInterface(url=rpc_url)
        invulnerables = substrate.query("CollatorSelection", "Invulnerables").value
        candidates = [c['who'] for c in substrate.query("CollatorSelection", "CandidateList").value]
        
        # Print results
        print(f"\n🔷 Invulnerable Collators ({len(invulnerables)})")
        for addr in invulnerables:
            print(f"  {addr[:10]}...{addr[-6:]} ({collators.get(addr, 'UNKNOWN')})")
        
        print(f"\n🔶 Candidate Collators ({len(candidates)})")
        for addr in candidates:
            print(f"  {addr[:10]}...{addr[-6:]} ({collators.get(addr, 'UNKNOWN')})")
        
        # Check specific collators and track missing ones
        for target_name in ["PARANODES.IO"]:  # Add more names as needed
            found = check_collator(target_name, invulnerables, candidates, collators)
            if not found:
                missing_trackers[target_name].append({
                    'chain': chain_name,
                    'rpc': rpc_url
                })
        
        # Detect unknowns
        unknown = [addr for addr in invulnerables + candidates if addr not in collators]
        if unknown:
            print("\n⚠️ Unknown Collators Detected:")
            for addr in unknown:
                print(f"  {addr}")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Error checking {chain_name}: {str(e)}")
        missing_trackers['ERRORS'].append({
            'chain': chain_name,
            'rpc': rpc_url,
            'error': str(e)
        })
        return False

def check_collator(name, invulnerables, candidates, collators):
    target_address = None
    for address, collator_name in collators.items():
        if name.lower() in collator_name.lower():
            target_address = address
            break
    
    if not target_address:
        print(f"\n❌ {name} not found in collator registry")
        return False
    
    if target_address in invulnerables:
        print(f"\n✅ {name} found in Invulnerables")
        return True
    elif target_address in candidates:
        print(f"\n✅ {name} found in Candidates")
        return True
    else:
        print(f"\n❌ {name} not currently active")
        return False

def print_missing_report(missing_trackers):
    print("\n" + " MISSING COLLATOR REPORT ".center(80, "="))
    for collator_name, missing_list in missing_trackers.items():
        if collator_name == 'ERRORS':
            continue
            
        if missing_list:
            print(f"\n❌ {collator_name} MISSING FROM {len(missing_list)} CHAINS:")
            for entry in missing_list:
                print(f"  • {entry['chain']} ({entry['rpc']})")
    
    if missing_trackers['ERRORS']:
        print("\n" + " ERRORS ".center(80, "="))
        for error in missing_trackers['ERRORS']:
            print(f"\n❌ {error['chain']} ({error['rpc']})")
            print(f"  Error: {error['error']}")

print(f"🚀 Starting Collator Checks for Paranodes System Chains - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
config = load_config()

# Initialize tracker for missing collators
missing_trackers = defaultdict(list)
missing_trackers['ERRORS'] = []

print("\n" + "POLKADOT CHAINS".center(50, "="))
for chain in config["polkadot_chains"]:
    check_chain(chain, missing_trackers)

print("\n" + "KUSAMA CHAINS".center(50, "="))
for chain in config["kusama_chains"]:
    check_chain(chain, missing_trackers)

print_missing_report(missing_trackers)
print("\n" + "✅ ALL CHECKS COMPLETE".center(50, "="))