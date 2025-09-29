<h1 align='center'>Tower of Fantasy | Game Manager Database</h1>

![Image](https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/2064650/7fc8d15627e3d780287f1132b3f7eaa06e371897/library_hero_2x.jpg)

<div align="center"> <a href="https://nanyinsbedroom.github.io" target="_blank"> <img src="https://img.shields.io/badge/Database-Webview-blue?style=for-the-badge&logo=github" alt="Database Webview" /> </a> <a href="https://discord.gg/Bs5cPKumFX" target="_blank"> <img src="https://img.shields.io/badge/Discord-Community-7289DA?style=for-the-badge&logo=discord" alt="Discord Community" /> </a> </div>

> **Important Notice: Player Data Tracking System**
>
> This system is a semi-automated tool for tracking player population data and is **not affiliated with, endorsed by, or supported by Hotta Studio or the official Tower of Fantasy service.**
>
> **Critical Prerequisites:**
> - Data collection requires a **third-party program** not provided here.
> - You must **manually log in** to each target server region.
> - Complete data requires **manual exploration** of the entire game map to ensure all players are loaded into the local game client.

### Data Structure
The system collects and stores the following anonymized player data:
- **Player Identifier:** In-game Name and Role ID
- **Server Information:** Region and Name
- **Social Data:** Crew (Guild) Affiliation
- **Timestamps:** Account Creation Date and Last-Seen Activity Date

### Collection Workflow

1.  **Manual Setup & Data Acquisition:**
    - Log into the target server region using the official game client.
    - Launch the required third-party data collection program.
    - Manually traverse the entire game map to load all player characters into your client's view.

2.  **Automated Data Processing:**
    - The third-party program scans the game's memory.
    - It detects and extracts player data structures.
    - Relevant information (UIDs, positions, timestamps, etc.) is parsed and saved.

3.  **Manual Verification & Validation:**
    - Physically visit key social hubs and high-traffic areas on the map.
    - Perform spot-checks to verify that the scanner is accurately capturing all visible players.
    - This step confirms the completeness and accuracy of the automated scan.

### System Features
- **Organized Data Storage:** Player data is saved in regional files: `accounts/[server_region]/accounts.json`
- **Centralized Statistics:** An `index.json` file aggregates global population stats and trends.
- **Automated Version Control:** All data changes are automatically committed and synced using the libgit2 library.
- **Data Integrity:** Failed or interrupted scans are preserved, allowing for recovery and retry without data loss.
