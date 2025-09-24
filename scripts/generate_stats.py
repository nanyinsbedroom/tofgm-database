import json
import os
import requests
import random
from datetime import datetime
from typing import Dict, Any, List
from collections import defaultdict

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
SERVERS_PATH = "servers/servers.json"
BOT_NAME = "Tower of Fantasy | Game Manager Database"

class StatisticsGenerator:
    def __init__(self):
        self.data = self._load_data()
        self.servers = self._load_servers()
        self.last_update = datetime.fromtimestamp(self.data["last_update"])
        self.total_accounts = self.data.get("total_accounts", 0)
        self.regions = self.data.get("regions", {})
        self.region_accounts = self._get_region_accounts()
        self.crew_stats = self._get_crew_stats()

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open("index.json", "r", encoding='utf-8') as f:
                return json.load(f)
        except UnicodeDecodeError:
            try:
                with open("index.json", "r", encoding='latin-1') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading index.json: {e}")
                return {
                    "last_update": 0,
                    "total_accounts": 0,
                    "regions": {}
                }
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading index.json: {e}")
            return {
                "last_update": 0,
                "total_accounts": 0,
                "regions": {}
            }

    def _load_servers(self) -> Dict[str, Any]:
        try:
            with open(SERVERS_PATH, "r", encoding='utf-8') as f:
                return json.load(f)
        except UnicodeDecodeError:
            try:
                with open(SERVERS_PATH, "r", encoding='latin-1') as f:
                    return json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading {SERVERS_PATH}: {e}")
                return {"os": {}, "cn": {}}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {SERVERS_PATH}: {e}")
            return {"os": {}, "cn": {}}

    def _get_actual_region_folders(self) -> List[str]:
        """Get the actual folder names that exist in the accounts directory"""
        accounts_dir = "accounts"
        if not os.path.exists(accounts_dir):
            print(f"Accounts directory '{accounts_dir}' not found")
            return []
        
        try:
            folders = [f for f in os.listdir(accounts_dir) 
                      if os.path.isdir(os.path.join(accounts_dir, f))]
            print(f"Found region folders: {folders}")
            return folders
        except Exception as e:
            print(f"Error reading accounts directory: {e}")
            return []

    def _map_region_keys_to_folders(self) -> Dict[str, str]:
        """Map region keys from index.json to actual folder names"""
        actual_folders = self._get_actual_region_folders()
        region_mapping = {}
        
        # Common region mappings
        common_mappings = {
            # English regions
            "asia_pacific": "asia_pacific",
            "europe": "europe", 
            "north_america": "north_america",
            "south_america": "south_america",
            "southeast_asia": "southeast_asia",
            
            # Try to match corrupted names
            "å»žæº”": "asia_pacific",  # Likely Asia Pacific
            "çūåū%«æ–”": "europe",     # Likely Europe
            "i—ūršníž´ei¬i»": "north_america"  # Likely North America
        }
        
        for region_key in self.regions.keys():
            # Try exact match first
            if region_key in actual_folders:
                region_mapping[region_key] = region_key
                continue
                
            # Try common mappings
            if region_key in common_mappings and common_mappings[region_key] in actual_folders:
                region_mapping[region_key] = common_mappings[region_key]
                continue
                
            # Try case-insensitive match
            for folder in actual_folders:
                if region_key.lower() == folder.lower():
                    region_mapping[region_key] = folder
                    break
            else:
                print(f"Warning: No folder found for region key '{region_key}'")
                
        print(f"Region mapping: {region_mapping}")
        return region_mapping

    def _get_region_accounts(self) -> Dict[str, List[Dict]]:
        region_accounts = defaultdict(list)
        region_mapping = self._map_region_keys_to_folders()
        
        for region_key, folder_name in region_mapping.items():
            region_file = f"accounts/{folder_name}/accounts.json"
            try:
                # Try UTF-8 first, then fallback to latin-1
                try:
                    with open(region_file, "r", encoding='utf-8') as f:
                        region_data = json.load(f)
                except UnicodeDecodeError:
                    with open(region_file, "r", encoding='latin-1') as f:
                        region_data = json.load(f)
                
                accounts = list(region_data.get("accounts", {}).values())
                region_accounts[region_key] = accounts
                print(f"Loaded {len(accounts)} accounts from {region_file}")
                
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading {region_file}: {e}")
                
        return region_accounts

    def _get_crew_stats(self) -> Dict[str, Dict[str, int]]:
        crew_stats = {}
        for region, accounts in self.region_accounts.items():
            crew_counts = defaultdict(int)
            for account in accounts:
                crew_name = account.get("crew", "No Crew")
                if crew_name and crew_name != "No Crew":
                    # Clean up crew name
                    crew_name = str(crew_name).strip()
                else:
                    crew_name = "No Crew"
                crew_counts[crew_name] += 1
            
            # Sort crews by member count (descending)
            sorted_crews = dict(sorted(crew_counts.items(), key=lambda x: x[1], reverse=True))
            crew_stats[region] = sorted_crews
            print(f"Region {region}: {len(crew_counts)} crews found")
            
        return crew_stats

    def _get_region_display_name(self, region_key: str) -> str:
        """Convert region key to display name"""
        display_names = {
            "asia_pacific": "Asia Pacific",
            "europe": "Europe",
            "north_america": "North America", 
            "south_america": "South America",
            "southeast_asia": "Southeast Asia",
            "å›žæº¯": "回溯",
            "ç­å‰æ–¯": "班吉斯",
            "ì—ìŠ¤íŽ˜ë¦¬ì•„": "에스페리아"
        }
        return display_names.get(region_key, region_key)

    def _generate_discord_embeds(self) -> Dict[str, Any]:
        embed = {
            "title": "Tower of Fantasy | Game Manager Database",
            "description": "📊 Regional Account Statistics",
            "color": random.randint(0, 0xFFFFFF),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": f"Last update: {self.last_update.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            },
            "fields": []
        }

        # Add total accounts field
        embed["fields"].append({
            "name": "📈 Total Accounts Tracked",
            "value": f"```{self.total_accounts:,}```",
            "inline": True
        })

        embed["fields"].append({
            "name": "🌍 Regions Tracked",
            "value": f"```{len(self.region_accounts)}```",
            "inline": True
        })

        # Add region-specific fields
        os_servers = self.servers.get("os", {})
        
        # Get regions that have actual data
        valid_regions = [region for region in self.regions.keys() 
                        if region in self.region_accounts and self.region_accounts[region]]
        
        for region_key in valid_regions:
            info = self.regions.get(region_key, {"total_accounts": 0})
            crew_info = self.crew_stats.get(region_key, {})
            
            # Get display name for region
            display_name = self._get_region_display_name(region_key)
            
            # Get top 3 crews by member count
            top_crews = list(crew_info.items())[:3]
            crew_display = []
            for crew_name, count in top_crews:
                if crew_name == "No Crew":
                    crew_display.append(f"• No Crew: `{count}`")
                else:
                    # Clean and truncate crew name
                    clean_name = str(crew_name).encode('ascii', 'ignore').decode('ascii', 'ignore')
                    if not clean_name or clean_name.isspace():
                        clean_name = "Unnamed Crew"
                    if len(clean_name) > 20:
                        clean_name = clean_name[:17] + "..."
                    crew_display.append(f"• {clean_name}: `{count}`")
            
            # Add "and X more..." if there are more crews
            if len(crew_info) > 3:
                crew_display.append(f"• ... and {len(crew_info) - 3} more crews")
            
            crew_text = "\n".join(crew_display) if crew_display else "• No crew data available"
            
            field_value = f"**Total Accounts**: `{info['total_accounts']:,}`\n**Top Crews**:\n{crew_text}"
            
            embed["fields"].append({
                "name": f"🏴‍☠️ {display_name}",
                "value": field_value,
                "inline": True
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
            print("Sending to Discord...")
            
            response = requests.post(
                DISCORD_WEBHOOK_URL,
                json=embed_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code != 204:
                print(f"Discord API Error: {response.status_code} - {response.text}")
                return False
                
            print("Successfully sent Discord notification")
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"Discord notification failed: {str(e)}")
            return False

    def update_stats(self):
        if self._send_to_discord():
            print("Sent Discord notification successfully")
        else:
            print("Failed to send Discord notification")

if __name__ == "__main__":
    generate = StatisticsGenerator()
    generate.update_stats()