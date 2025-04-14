import json
import requests
import logging
import sys
from pathlib import Path
from substrateinterface import SubstrateInterface
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    filename='logs/monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

def log(message: str, console: bool = False, level: str = "info"):
    """Unified logging function"""
    if level.lower() == "error":
        logging.error(message)
        if console:
            print(f"❌ {message}")
    elif level.lower() == "warning":
        logging.warning(message)
        if console:
            print(f"⚠️ {message}")
    else:
        logging.info(message)
        if console:
            print(f"ℹ️ {message}")

def load_config() -> Dict:
    """Load configuration from JSON file"""
    try:
        config_path = Path(__file__).parent / "system_chains_config.json"
        with open(config_path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        log(f"Config load failed: {str(e)}", console=True, level="error")
        raise

def send_discord_alert(missing_report: Dict, webhook_url: str) -> None:
    """Send formatted alert to Discord webhook"""
    try:
        embed = {
            "title": "Collator Status Alert",
            "color": 16711680,  # Red
            "timestamp": datetime.utcnow().isoformat(),
            "fields": []
        }

        for collator_name, missing_list in missing_report.items():
            if collator_name == 'ERRORS':
                continue
            if missing_list:
                embed["fields"].append({
                    "name": f"❌ {collator_name} missing from {len(missing_list)} chains",
                    "value": "\n".join([f"• {entry['chain']} ({entry['rpc']})" for entry in missing_list]),
                    "inline": False
                })

        if missing_report['ERRORS']:
            embed["fields"].append({
                "name": "⚠️ Errors",
                "value": "\n".join([f"• {error['chain']}: {error['error']}" for error in missing_report['ERRORS']]),
                "inline": False
            })

        response = requests.post(
            webhook_url,
            json={"embeds": [embed]},
            timeout=10
        )
        response.raise_for_status()
        log("Discord alert sent", console=True)
    except Exception as e:
        log(f"Discord send failed: {str(e)}", console=True, level="error")

def check_chain(chain_config: Dict, missing_trackers: Dict) -> bool:
    """Check a single chain's collators"""
    try:
        with open(Path(__file__).parent / chain_config["collator_file"], encoding='utf-8') as f:
            collators = json.load(f)

        substrate = SubstrateInterface(url=chain_config["rpc_url"])
        invulnerables = substrate.query("CollatorSelection", "Invulnerables").value
        candidates = [c['who'] for c in substrate.query("CollatorSelection", "CandidateList").value]

        log(f"Checking {chain_config['name']}...", console=True)
        log(f"Invulnerables: {len(invulnerables)}, Candidates: {len(candidates)}")

        for target_name in ["PARANODES.IO"]:
            if not check_collator(target_name, invulnerables, candidates, collators):
                missing_trackers[target_name].append({
                    'chain': chain_config['name'],
                    'rpc': chain_config['rpc_url']
                })

        unknown = [addr for addr in invulnerables + candidates if addr not in collators]
        if unknown:
            log(f"Unknown collators detected: {len(unknown)}", level="warning")

        return True
    except Exception as e:
        error_msg = f"Chain {chain_config['name']} failed: {str(e)}"
        log(error_msg, level="error")
        missing_trackers['ERRORS'].append({
            'chain': chain_config['name'],
            'rpc': chain_config['rpc_url'],
            'error': error_msg
        })
        return False

def check_collator(name: str, invulnerables: List, candidates: List, collators: Dict) -> bool:
    """Check if a specific collator is active"""
    target_address = next(
        (addr for addr, collator_name in collators.items() 
         if name.lower() in collator_name.lower()),
        None
    )

    if not target_address:
        log(f"{name} not in registry", level="warning")
        return False

    if target_address in invulnerables:
        log(f"{name} is invulnerable")
        return True
    elif target_address in candidates:
        log(f"{name} is candidate")
        return True
    
    log(f"{name} not active", level="warning")
    return False

def main(test_mode: bool = False) -> None:
    """Main execution function"""
    try:
        log("🚀 Starting collator checks", console=True)
        config = load_config()

        missing_trackers = defaultdict(list)
        missing_trackers['ERRORS'] = []

        for chain_type in ["polkadot_chains", "kusama_chains"]:
            log(f"Processing {chain_type.replace('_', ' ')}", console=True)
            for chain in config.get(chain_type, []):
                check_chain(chain, missing_trackers)

        if test_mode:
            log("Running in test mode", console=True)
            test_payload = {
                "PARANODES.IO": [{"chain": "TEST", "rpc": "wss://test"}],
                "ERRORS": [{"chain": "TEST", "rpc": "wss://test", "error": "Test error"}]
            }
            send_discord_alert(test_payload, config["discord_webhook_url"])
        elif any(missing_trackers.values()):
            send_discord_alert(missing_trackers, config["discord_webhook_url"])

        log("✅ All checks complete", console=True)
    except Exception as e:
        log(f"Critical failure: {str(e)}", console=True, level="error")
        raise

if __name__ == "__main__":
    try:
        main(test_mode="--test" in sys.argv)
    except Exception as e:
        log("Fatal error - script terminated", console=True, level="error")
        sys.exit(1)