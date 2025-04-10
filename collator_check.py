from substrateinterface import SubstrateInterface

def connect_to_chain():
    try:
        substrate = SubstrateInterface(
            url="wss://rpc-asset-hub-kusama.luckyfriday.io",
            type_registry_preset='kusama'
        )
        print("✅ Connected to the chain.")
        return substrate
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None
    
connect_to_chain()