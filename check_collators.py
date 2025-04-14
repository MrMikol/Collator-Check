import json
import requests
from pathlib import Path
from substrateinterface import SubstrateInterface
from datetime import datetime
from collections import defaultdict
import logging
from typing import Dict, List
import sys


def load_config():
    """Load configuration from JSON file"""
    config_path = Path(__file__).parent / "system_chains_config.json"
    with open(config_path, encoding='utf-8') as f:
        return json.load(f)

def send_discord_alert(missing_report, webhook_url):
    """Send formatted alert to Discord webhook"""
    try:
        # Create embed message
        embed = {
            "title": "Collator Status Alert",
            "color": 16711680,  # Red color
            "timestamp": datetime.utcnow().isoformat(),
            "fields": []
        }

        # Add missing collators to embed
        for collator_name, missing_list in missing_report.items():
            if collator_name == 'ERRORS':
                continue
                
            if missing_list:
                value = "\n".join([f"• {entry['chain']} ({entry['rpc']})" for entry in missing_list])
                embed["fields"].append({
                    "name": f"❌ {collator_name} missing from {len(missing_list)} chains",
                    "value": value,
                    "inline": False
                })

        # Add errors if any
        if missing_report['ERRORS']:
            error_value = "\n".join([f"• {error['chain']}: {error['error']}" for error in missing_report['ERRORS']])
            embed["fields"].append({
                "name": "⚠️ Errors Encountered",
                "value": error_value,
                "inline": False
            })

        payload = {
            "embeds": [embed],
            "username": "Collator Monitor",
            "avatar_url": "https://i.imgur.com/4M34hi2.png"  # Optional: Replace with your icon
        }

        # Send to Discord
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print("\n📢 Discord alert sent successfully")
    
    except Exception as e:
        print(f"\n❌ Failed to send Discord alert: {str(e)}")

def check_chain(chain_config, missing_trackers):
    chain_name = chain_config['name']
    rpc_url = chain_config['rpc_url']
    print(f"\n{'='*50}")
    print(f"🔍 Checking {chain_name}")
    print(f"📡 RPC: {rpc_url}")
    print(f"{'='*50}")
    
    try:
        with open(Path(__file__).parent / chain_config["collator_file"], encoding='utf-8') as f:
            collators = json.load(f)
        
        substrate = SubstrateInterface(url=rpc_url)
        invulnerables = substrate.query("CollatorSelection", "Invulnerables").value
        candidates = [c['who'] for c in substrate.query("CollatorSelection", "CandidateList").value]
        
        print(f"\n🔷 Invulnerable Collators ({len(invulnerables)})")
        for addr in invulnerables:
            print(f"  {addr[:10]}...{addr[-6:]} ({collators.get(addr, 'UNKNOWN')})")
        
        print(f"\n🔶 Candidate Collators ({len(candidates)})")
        for addr in candidates:
            print(f"  {addr[:10]}...{addr[-6:]} ({collators.get(addr, 'UNKNOWN')})")
        
        for target_name in ["PARANODES.IO"]:
            found = check_collator(target_name, invulnerables, candidates, collators)
            if not found:
                missing_trackers[target_name].append({
                    'chain': chain_name,
                    'rpc': rpc_url
                })
        
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

def setup_logging():
    """Configure logging to file"""
    logging.basicConfig(
        filename='logs/monitor_debug.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main(test_mode=False):
    """Main execution function with comprehensive error handling"""
    setup_logging()
    logging.info("Starting collator monitoring session")
    
    try:
        config = None  # Initialize for exception handling scope
        config = load_config()
        
        # Validate config structure
        if not all(k in config for k in ["polkadot_chains", "kusama_chains"]):
            raise ValueError("Invalid config structure - missing required chains")

        missing_trackers = defaultdict(list)
        missing_trackers['ERRORS'] = []

        # Chain processing with individual error handling
        for chain_type in ["polkadot_chains", "kusama_chains"]:
            logging.info(f"Processing {chain_type}")
            print(f"\n{chain_type.replace('_', ' ').upper()}".center(50, "="))
            
            for chain in config.get(chain_type, []):
                try:
                    check_chain(chain, missing_trackers)
                except Exception as e:
                    error_msg = f"Chain {chain['name']} failed: {str(e)}"
                    logging.error(error_msg, exc_info=True)
                    missing_trackers['ERRORS'].append({
                        'chain': chain['name'],
                        'rpc': chain['rpc_url'],
                        'error': error_msg
                    })

        print_missing_report(missing_trackers)
        logging.info("Completed chain checks")

        # Alert logic
        needs_alert = any(
            missing_list for collator_name, missing_list in missing_trackers.items()
            if collator_name != 'ERRORS' and missing_list
        ) or missing_trackers['ERRORS']

        if test_mode:
            logging.info("Running in test mode")
            test_payload = {
                "PARANODES.IO": [{
                    "chain": "TEST-CHAIN", 
                    "rpc": "wss://test.rpc.url"
                }],
                "ERRORS": [{
                    "chain": "TEST-CHAIN",
                    "rpc": "wss://test.rpc.url",
                    "error": "This is a test error"
                }]
            }
            send_discord_alert(test_payload, config["discord_webhook_url"])
        elif needs_alert and "discord_webhook_url" in config:
            logging.info("Sending alert to Discord")
            send_discord_alert(missing_trackers, config["discord_webhook_url"])

        logging.info("Monitoring completed successfully")
        print("\n" + "✅ ALL CHECKS COMPLETE".center(50, "="))

    except json.JSONDecodeError as e:
        error_msg = f"Config JSON error: {str(e)}"
        logging.critical(error_msg)
        if config and "discord_webhook_url" in config:
            send_discord_alert({"ERRORS": [{"error": error_msg}]}, config["discord_webhook_url"])
        
    except Exception as e:
        error_msg = f"Critical failure: {str(e)}"
        logging.critical(error_msg, exc_info=True)
        if config and "discord_webhook_url" in config:
            send_discord_alert(
                {"ERRORS": [{"error": error_msg}]},
                config["discord_webhook_url"]
            )
        raise  # Re-raise for batch file error detection

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Unhandled top-level exception: {str(e)}")
        sys.exit(1)