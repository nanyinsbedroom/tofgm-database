import json
import os
import requests
import random
from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
README_PATH = "README.md"
INDEX_PATH = "index.json"
SERVERS_PATH = "servers/servers.json"
BOT_NAME = "Tower of Fantasy | Game Manager"

class StatisticsGenerator:
    def __init__(self):
        self.data = self._load_data()
        self.servers = self._load_servers()
        self.last_update = datetime.fromtimestamp(self.data["last_update"])
        self.total_accounts = self.data.get("total_accounts", 0)
        self.regions = self.data.get("regions", {})
        self.region_accounts = self._get_region_accounts()
        self.region_extremes = self._find_region_extremes()

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(INDEX_PATH, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {INDEX_PATH}: {e}")
            return {
                "last_update": 0,
                "total_accounts": 0,
                "regions": {}
            }

    def _load_servers(self) -> Dict[str, Any]:
        try:
            with open(SERVERS_PATH, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {SERVERS_PATH}: {e}")
            return {"os": {}, "cn": {}}

    def _parse_registered_date(self, date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, "%b %d, %Y, %I:%M:%S %p")
        except ValueError:
            if date_str.startswith("Jan 1, 1"):
                return datetime.max
            try:
                return datetime.strptime(date_str, "%b %d, %Y, %H:%M:%S")
            except ValueError:
                print(f"Warning: Could not parse date '{date_str}' - using current time")
                return datetime.now()

    def _get_region_accounts(self) -> Dict[str, List[Dict]]:
        region_accounts = defaultdict(list)
        for region in self.regions.keys():
            region_file = f"accounts/{region}/accounts.json"
            try:
                with open(region_file, "r") as f:
                    region_data = json.load(f)
                    for account in region_data.get("accounts", {}).values():
                        account["parsed_date"] = self._parse_registered_date(account["registered"])
                        region_accounts[region].append(account)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading {region_file}: {e}")
        return region_accounts

    def _find_region_extremes(self) -> Dict[str, Dict[str, Dict]]:
        extremes = {}
        for region, accounts in self.region_accounts.items():
            if not accounts:
                continue
                
            valid_accounts = [a for a in accounts if a["parsed_date"] != datetime.max]
            default_accounts = [a for a in accounts if a["parsed_date"] == datetime.max]
            
            accounts_to_sort = valid_accounts if valid_accounts else default_accounts
            
            sorted_accounts = sorted(accounts_to_sort, key=lambda x: x["parsed_date"])
            extremes[region] = {
                "oldest": sorted_accounts[0],
                "newest": sorted_accounts[-1] if len(sorted_accounts) > 1 else sorted_accounts[0]
            }
        return extremes

    def _generate_readme(self) -> str:
        return (
            "<h1 align='center'>Tower of Fantasy | Game Manager Database</h1>\n\n"
            f"**Last Updated**: `{self.last_update.strftime('%Y-%m-%d %H:%M:%S UTC')}`  \n"
            f"**Total Accounts Tracked**: `{self.total_accounts:,}`  \n\n"
            
            "## About This Database\n\n"
            "> **Important Notice**: This semi-automated tracking system requires the third-party program to collect player data and manual login and map traversal across all server regions is necessary for complete data collection.\n\n"
            
            "### Data Structure\n"
            "- **Player names** and role identifiers  \n"
            "- **Server region** classifications  \n"
            "- **Crew** affiliations  \n"
            "- **Account creation** timestamps  \n"
            "- **Last-seen** activity dates  \n\n"
            
            "## Data Collection System\n\n"
            "> **Data Collection Warning**:  \n"
            "- Requires running third-party program  \n"
            "- Involves logging into each server region  \n"
            "- Needs manual map traversal for full coverage  \n\n"
            
            "### Technical Implementation\n"
            "- `Memory scanner` (third-party program)  \n"
            "- `Multi-threaded C++` data processor  \n"
            "- `JSON output` generator  \n\n"
            
            "### Collection Workflow\n"
            "1. **Manual Setup**:  \n"
            "   - Log into target server region  \n"
            "   - Launch third-party program  \n"
            "   - Start map traversal  \n"
            "   - Ensure all players are loaded in memory  \n"
            "2. **Automated Scanning**:  \n"
            "   - Process memory reading  \n"
            "   - Player structure detection  \n"
            "   - Data extraction (UIDs, positions, timestamps)  \n"
            "3. **Manual Verification**:  \n"
            "   - Walk through key map areas  \n"
            "   - Spot-check player concentrations  \n"
            "   - Validate scanner accuracy  \n\n"
            
            "## Key Features\n"
            "- **Regional Data Files**: `accounts/[region]/accounts.json`  \n"
            "- **Centralized Index**: `index.json` for global stats  \n"
            "- **Version Control**: Automated Git synchronization  \n"
            "- **Data Safety**: Failed scans preserved for retry  \n\n"
            
            "> **Usage Disclaimer**:  \n"
            "This system is not affiliated with Hotta Studio or Tower of Fantasy official services.  \n"
            "Data collection depends on third-party programs and manual verification.\n\n"
            
            "## Current Statistics\n\n"
            f"{self._format_region_stats()}\n\n"
            "*Auto-updated hourly* | [View Raw Data](https://github.com/soevielofficial/tofgm-database)"
        )
    
    def _format_region_name(self, region: str) -> str:
        return region.replace('_', ' ').title()

    def _format_region_stats(self) -> str:
        sections = []
        os_servers = self.servers.get("os", {})
        sorted_regions = sorted(os_servers.keys(), key=lambda x: x.lower())
        
        for region_name in sorted_regions:
            server_info = os_servers[region_name]
            region_key = region_name.lower().replace(' ', '_')
            info = self.regions.get(region_key, {"total_accounts": 0})
            extremes = self.region_extremes.get(region_key, {})
            
            formatted_region = self._format_region_name(region_key)
            
            section = f"### {formatted_region}\n\n"
            
            section += f"- **Location**: `{server_info.get('City', 'unknown')}, {server_info.get('Country', 'unknown')}`  \n"
            section += f"- **Network**: `{server_info.get('IP Address', 'unknown')}` (`{server_info.get('Hostname', 'unknown')}`)  \n"
            section += f"- **Provider**: `{server_info.get('ISP', 'unknown')}` (ASN{server_info.get('ASN', 'unknown')})  \n\n"
            
            section += f"- **Total Accounts**: `{info['total_accounts']:,}`  \n"
            
            if extremes:
                section += f"- **Tracked Latest Registered Account**: `{extremes['newest']['name']}`  \n"
                section += f"  - Date: `{extremes['newest']['registered']}`  \n"
                section += f"- **Tracked Earliest Registered Account**: `{extremes['oldest']['name']}`  \n"
                section += f"  - Date: `{extremes['oldest']['registered']}`  \n"
            
            sections.append(section)
        
        return "\n".join(sections)

    def _generate_discord_embeds(self) -> Dict[str, Any]:
        embed = {
            "title": "Game Manager Report",
            "description": "⚠️ This semi-automated tracking system requires the third-party program to collect player data and manual login and map traversal across all server regions is necessary for complete data collection.",
            "color": random.randint(0, 0xFFFFFF),
            "timestamp": datetime.utcnow().isoformat(),
            "image": {
                "url": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2064650/4f85fcd20b06b23e471198ed937521c251688172/library_hero.jpg"
            },
            "footer": {
                "text": f"Last update: {self.last_update.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            },
            "fields": []
        }

        embed["fields"].extend([
            {
                "name": "Total Tracked Accounts:",
                "value": f"```{self.total_accounts:,}```",
                "inline": True
            },
            {
                "name": "Server Regions Tracked:",
                "value": f"```{len(self.regions)}```",
                "inline": True
            },
            {
                "name": "Server Details:",
                "value": "",
                "inline": False
            }
        ])

        os_servers = self.servers.get("os", {})
        sorted_regions = sorted(os_servers.keys(), key=lambda x: x.lower())
        
        for region_name in sorted_regions:
            server_info = os_servers[region_name]
            region_key = region_name.lower().replace(' ', '_')
            info = self.regions.get(region_key, {"total_accounts": 0})
            extremes = self.region_extremes.get(region_key, {})
            
            server_value = [
                f"• **IP**: `{server_info.get('IP Address', 'Unknown')}`",
                f"• **Location**: `{server_info.get('City', '?')}, {server_info.get('Country', '?')}`",
                f"• **ISP**: `{server_info.get('ISP', 'Unknown')}`",
                f"• **Total Tracked Accounts**: `{info['total_accounts']:,}`"
            ]
            
            if extremes:
                oldest = extremes.get('oldest', {})
                newest = extremes.get('newest', {})
                
                if oldest.get('name'):
                    try:
                        registered_date = datetime.strptime(oldest.get('registered', ''), '%b %d, %Y, %I:%M:%S %p')
                        formatted_date = registered_date.strftime('%b %d, %Y, %I:%M:%S %p')
                    except (ValueError, TypeError):
                        formatted_date = oldest.get('registered', '?')
                
                server_value.append(f"• **Tracked Earliest Registered Account**: `{oldest['name']} on {formatted_date}`")
            
                if newest.get('name') and newest.get('name') != oldest.get('name'):
                    try:
                        registered_date = datetime.strptime(newest.get('registered', ''), '%b %d, %Y, %I:%M:%S %p')
                        formatted_date = registered_date.strftime('%b %d, %Y, %I:%M:%S %p')
                    except (ValueError, TypeError):
                        formatted_date = newest.get('registered', '?')
                    
                    server_value.append(f"• **Tracked Latest Registered Account**: `{newest['name']} on {formatted_date}`")

            embed["fields"].append({
                "name": f"{region_name}",
                "value": "\n".join(server_value),
                "inline": False
            })

        embed["fields"].append({
            "name": "\u200b",
            "value": "[View Raw Data on GitHub](https://github.com/soevielofficial/tofgm-database)",
            "inline": False
        })

        return {
            "username": BOT_NAME,
            "embeds": [embed]
        }

    def _send_to_discord(self) -> bool:
        if not DISCORD_WEBHOOK_URL:
            print("No Discord webhook configured - skipping notification")
            return False

        try:
            embed_data = self._generate_discord_embeds()
            print("Sending to Discord:", json.dumps(embed_data, indent=2))
            
            total_chars = sum(len(field.get('value', '')) for field in embed_data['embeds'][0].get('fields', []))
            if total_chars > 6000:
                print("Embed too large - trimming fields")
                embed_data['embeds'][0]['fields'] = embed_data['embeds'][0]['fields'][:5]
                
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=embed_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 204:
                print(f"Discord API Error: {response.status_code} - {response.text}")
                return False
                
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"Discord notification failed: {str(e)}")
            if hasattr(e, 'response') and e.response:
                print(f"Response content: {e.response.text}")
            return False

    def update_stats(self):
        readme_content = self._generate_readme()
        with open(README_PATH, "w") as f:
            f.write(readme_content)
        print(f"Updated {README_PATH}")

        if self._send_to_discord():
            print("Sent Discord notification")

if __name__ == "__main__":
    generate = StatisticsGenerator()
    generate.update_stats()