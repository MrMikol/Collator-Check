from substrateinterface import SubstrateInterface

COLLATORS = {
    "16WWmr2Xqgy5fna35GsNHXMU7vDBM12gzHCFGibQjSmKpAN": "PARANODES.IO",
    "15PUkSRWuefDSLbEYp39MJ1zxShrratU4SXaLZanL8Zkren3": "OPENBITLAB/BRIDGEHUB",
    "16X3CtQVwBvHGJCquvLw1ayG5SWk4qKUHudBDpQVGXBdvqdg": "STALKER SPACE/BRIDGEHUB",
    "13oz8fEwZ7TmpoAnozbHAfCG2L5uWdVmDq7cjY5Aw2CBW5Cj": "MEGATRON",
    "15MV2nX6BEoiBz8Ua2xNta19sVBKT7kiw2MEHdu2Jd9a4VaC": "LUCKYFRIDAY.IO",
    "15cu9qomrRvnqkvnSMhPPkBp9359QDbGBy1bVo3tseozxhxj": "HYPERSPEED",
    "14gL78nk3rVZamwGg33VuEa1koYC3rcoymFcPGXKbJ7JKyHZ": "COINSTUDIO/BRIDGEHUB",
    "14icei1ZMoG9QtKBFDk4y1eMR756q2TREuRAi2BanJ9MJVPL": "🧊 ICEBERG NODES 🧊",
    "12owmS8Sobqxfx6KK9vk9e67FqnGpZdmxCFCRFptzZdsoujC": "POLKADOTTERS/⛓CORE",
    "13Jpq4n3PXXaSAbJTMmFD78mXAzs8PzgUUQd5ve8saw7HQS5": "STAKEWORLD.IO",
    "13TUNfEBCi6xw5ZQgxYAwbCsALSuDfqDWMfbHigZNgncuV6v": "🐟YELLOWFIN TUNA🐟/🥗",
    "13xAUHVDyG1v9LLHYtMm7XZFyKNVxoj47oWV431XQ9kjXN38": "MILE🌍/SYS",
    "15wepZh1jWNqxBjsgErm8HmYiE21n79c5krQJeTsYAjHddeM": "SIK | CRIFFERENT.DE",
    "134AK3RiMA97Fx9dLj1CvuLJUa8Yo93EeLA1TkP6CCGnWMSd": "134AK3RiMA97Fx9dLj1CvuLJUa8Yo93EeLA1TkP6CCGnWMSd",
    "15dU8Tt7kde2diuHzijGbKGPU5K8BPzrFJfYFozvrS1DdE21": "15dU8Tt7kde2diuHzijGbKGPU5K8BPzrFJfYFozvrS1DdE21",
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
        substrate = SubstrateInterface(url="wss://rpc-bridge-hub-polkadot.luckyfriday.io")
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
print("Polkadot BridgeHub")
invulnerables, candidates = get_collators()
    
print_collators("Invulnerable Collators", invulnerables)
print_collators("Other Collators", candidates)
    
check_collators("PARANODES.IO", invulnerables, candidates)
    
detect_unknown_collators(invulnerables + candidates)
print("\n✅ CHECKS COMPLETE!")