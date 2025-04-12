from substrateinterface import SubstrateInterface
import json
from pathlib import Path

with open(Path(__file__).parent / "kusama_collators.json", encoding='utf-8') as f:
    COLLATORS = json.load(f)

def check_collators(collator_name, invulnerables, candidates):
    target_address = None
    for address, name in COLLATORS.items():
        if collator_name.lower() in name.lower():
            target_address = address
            break
    
    if not target_address:
        print(f"\n❌ {collator_name} not found in COLLATORS dictionary")
        return
    
    if target_address in invulnerables:
        print(f"\n✅ {collator_name} found in Invulnerables (address: {target_address})")
    
    elif target_address in candidates:
        print(f"\n✅ {collator_name} found in Candidates (address: {target_address})")
    
    else:
        print(f"\n❌ {collator_name} not currently in Collator list (address: {target_address})")

def get_collators():
    try:
        substrate = SubstrateInterface(url="wss://rpc-bridge-hub-kusama.luckyfriday.io")
        invulnerables = substrate.query("CollatorSelection", "Invulnerables").value
        candidates = [c['who'] for c in substrate.query("CollatorSelection", "CandidateList").value]
        return invulnerables, candidates
    except Exception as e:
        print(f"Error fetching collators: {e}")
        return [], []

def print_collators(title, addresses):
    print(f"\n🔷 {title} ({len(addresses)})")
    for addr in addresses:
        print(f"  {addr[:10]}...{addr[-6:]} ({COLLATORS.get(addr, 'UNKNOWN')})")

def detect_unknown_collators(all_collators):
    unknown = [addr for addr in all_collators if addr not in COLLATORS]
    if unknown:
        print("\n⚠️ Unknown Collators Detected:")
        for addr in unknown:
            print(f"  {addr}")
        print("\nTip: Add these to KNOWN_COLLATORS dictionary")

print("Starting checks for Paranodes.io in collators list ...")
print("Kusama BridgeHub")
invulnerables, candidates = get_collators()
    
print_collators("Invulnerable Collators", invulnerables)
print_collators("Other Collators", candidates)
    
check_collators("PARANODES.IO", invulnerables, candidates)
    
detect_unknown_collators(invulnerables + candidates)
print("\n✅ CHECKS COMPLETE!")