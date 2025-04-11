from substrateinterface import SubstrateInterface

# 1. Define your known collators (address -> name mapping)
COLLATORS = {
    "16WWmr2Xqgy5fna35GsNHXMU7vDBM12gzHCFGibQjSmKpAN": "PARANODES.IO",
    "12ixt2xmCJKuLXjM3gh1SY7C3aj4gBoBUqExTBTGhLCSATFw": "12ixt2xmCJKuLXjM3gh1SY7C3aj4gBoBUqExTBTGhLCSATFw",
    "14wQoaBqk718MgNxp3qdpqHnEgmTTmTkcVnYuxMWWvYr3DXb": "STALKER SPACE/STATEMINT",
    "14xSXydBVvuMMaNduDXwWcckt3BziSB8Sa7o34Jt9z2aMGxX": "DPSTK",
    "15MV2nX6BEoiBz8Ua2xNta19sVBKT7kiw2MEHdu2Jd9a4VaC": "LUCKYFRIDAY.IO",
    "15X2eHehrexKqz6Bs6fQTjptP2ndn39eYdQTeREVeRk32p54": "15X2eHehrexKqz6Bs6fQTjptP2ndn39eYdQTeREVeRk32p54",
    "167xwLzY4z3uNBMQSdDJmPnLgPKBY1SRsvQXbyaeHcnwd4um": "TURBOFLAKES.IO/MINT",
    "14EQvBy9h8xGbh2R3ustnkfkF514E7wpmHtg27gDaTLM2str": "COINSTUDIO/SYSTEM",
    "14icei1ZMoG9QtKBFDk4y1eMR756q2TREuRAi2BanJ9MJVPL": "🧊 ICEBERG NODES 🧊",
    "12owmS8Sobqxfx6KK9vk9e67FqnGpZdmxCFCRFptzZdsoujC": "POLKADOTTERS/⛓CORE",
    "13Jpq4n3PXXaSAbJTMmFD78mXAzs8PzgUUQd5ve8saw7HQS5": "STAKEWORLD.IO",
    "13TUNfEBCi6xw5ZQgxYAwbCsALSuDfqDWMfbHigZNgncuV6v": "🐟YELLOWFIN TUNA🐟/🥗",
    "13xAUHVDyG1v9LLHYtMm7XZFyKNVxoj47oWV431XQ9kjXN38": "MILE🌍/SYS",
    "15wepZh1jWNqxBjsgErm8HmYiE21n79c5krQJeTsYAjHddeM": "SIK | CRIFFERENT.DE",
}

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
        substrate = SubstrateInterface(url="wss://rpc-asset-hub-polkadot.luckyfriday.io")
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

if __name__ == "__main__":
    print("Starting checks for Paranodes.io in collators list ...")
    print("Polkadot AssetHub")
    invulnerables, candidates = get_collators()
    
    print_collators("Invulnerable Collators", invulnerables)
    print_collators("Other Collators", candidates)
    
    # Specific collator check (add more as needed)
    check_collators("PARANODES.IO", invulnerables, candidates)
    
    detect_unknown_collators(invulnerables + candidates)
    print("\n✅ CHECKS COMPLETE!")