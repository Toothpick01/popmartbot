import requests
import json
import re
import pyperclip
import os
from requests.auth import HTTPBasicAuth
from getpass import getpass

# Prompt for search term
search_term = input("Enter your search term: ").strip()
formatted_search_term = search_term.replace(' ', '+')

# EasyNews search URL
url = f"https://members-beta.easynews.com/3.0/search?basic=&gps={formatted_search_term}&fty%5B%5D=VIDEO"

# Radarr/Sonarr Configurations
radarr_api_url = "http://localhost:7878/api/v3/movie"
sonarr_api_url = "http://localhost:8989/api/v3/series"
radarr_api_key = "09f2e0f2122c4512b1440c2784d301fe"
sonarr_api_key = "8a582e93a4e945e19782b7ec01b686ba"
download_folder = r"C:\Users\Admin\Downloads"
jdownloader_folderwatch = r"C:\Users\Admin\AppData\Local\JDownloader 2.0\folderwatch"

# Session management
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# Login to EasyNews
username = input("Enter your EasyNews username: ").strip()
password = getpass("Enter your EasyNews password (hidden): ")

try:
    response = session.get(url, auth=HTTPBasicAuth(username, password))
    response.raise_for_status()
    print("Logged in successfully.")
except requests.exceptions.RequestException as e:
    print(f"Login failed: {e}")
    exit()

# Fetch root folders from Radarr or Sonarr
def get_root_folders(api_url, api_key):
    try:
        response = requests.get(f"{api_url}/rootfolder", headers={"X-Api-Key": api_key})
        response.raise_for_status()
        root_folders = response.json()
        return {folder["path"]: folder for folder in root_folders}
    except Exception as e:
        print(f"Failed to fetch root folders: {e}")
        return {}

# Fetch root folders for Radarr and Sonarr
radarr_root_folders = get_root_folders("http://localhost:7878/api/v3", radarr_api_key)
sonarr_root_folders = get_root_folders("http://localhost:8989/api/v3", sonarr_api_key)

# Display root folders for Radarr and Sonarr
def select_root_folder(root_folders):
    if not root_folders:
        print("No root folders found. Please configure them in Radarr or Sonarr.")
        return None
    print("\nAvailable Root Folders:")
    for idx, folder in enumerate(root_folders, 1):
        print(f"{idx}. {folder}")
    selected = int(input("Select a root folder: ")) - 1
    return list(root_folders.keys())[selected] if 0 <= selected < len(root_folders) else None

# Scrape search results
def scrape_search_results():
    try:
        response = session.get(url)
        response.raise_for_status()
        data_match = re.search(r'var INIT_RES = ({.*?});', response.text)
        if data_match:
            data = json.loads(data_match.group(1))
            return data.get('data', [])
        else:
            print("No search results found.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

# Function to format and display JSON response in a structured format
def display_response(response_json):
    print("\nResponse Details:")
    for key, value in response_json.items():
        if isinstance(value, dict) or isinstance(value, list):
            print(f"- {key.capitalize()}:")
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    print(f"  * {sub_key.capitalize()}: {sub_value}")
            elif isinstance(value, list):
                for idx, item in enumerate(value, start=1):
                    print(f"  * Item {idx}: {item}")
        else:
            print(f"- {key.capitalize()}: {value}")

# Fetch and display search results
search_results = scrape_search_results()
if not search_results:
    print("No results to display. Exiting.")
    exit()

download_links = {}
for i, result in enumerate(search_results, start=1):
    print(f"\nOption {i}:")
    print(f"File Name: {result.get('prettyFn', 'Unknown')}")
    print(f"File Size: {result.get('prettySize', 'Unknown')}")
    print(f"File Extension: {result.get('extension', 'Unknown')}")
    print(f"Audio Languages: {', '.join(result.get('alang', [])) or 'Not available'}")
    print("-" * 30)
    download_links[i] = {
        "link": f"https://members-beta.easynews.com/dl/3.0/auto/443/{result['hash']}{result['extension']}/{result['prettyFn']}{result['extension']}",
        "metadata": result
    }

# User selects an option
option = int(input("\nSelect an option to copy its download link to your clipboard: "))
if option in download_links:
    selected = download_links[option]
    download_link = selected["link"]
    metadata = selected["metadata"]
    pyperclip.copy(download_link)
    print("Download link copied to clipboard.")

    # Construct the .crawljob file
    crawljob_content = f"""enabled=TRUE
text={download_link}
packageName={metadata['prettyFn']}
filename={metadata['prettyFn']}{metadata['extension']}
autoConfirm=TRUE
autoStart=TRUE
extractAfterDownload=FALSE
downloadFolder={download_folder}
overwritePackagizerEnabled=false"""

    os.makedirs(jdownloader_folderwatch, exist_ok=True)

    crawljob_file_path = os.path.join(jdownloader_folderwatch, f"{metadata['prettyFn']}.crawljob")
    try:
        with open(crawljob_file_path, 'w') as f:
            f.write(crawljob_content)
        print(f".crawljob file created at {crawljob_file_path}")
    except Exception as e:
        print(f"Failed to create .crawljob file: {e}")

    choice = input("Add this media to Radarr or Sonarr? (r/s/skip): ").strip().lower()
    if choice == 'r':
        selected_folder = select_root_folder(radarr_root_folders)
        if selected_folder:
            payload = {
                "title": metadata['prettyFn'],
                "year": 2023,
                "qualityProfileId": 1,
                "titleSlug": metadata['prettyFn'].replace(" ", "-"),
                "images": [],
                "rootFolderPath": selected_folder,
                "monitored": True
            }
            headers = {"X-Api-Key": radarr_api_key}
            response = requests.post(radarr_api_url, json=payload, headers=headers)
            print("\nRadarr Response:")
            if response.status_code == 201:
                display_response(response.json())
            else:
                print(f"Error: {response.status_code} - {response.text}")

    elif choice == 's':
        selected_folder = select_root_folder(sonarr_root_folders)
        if selected_folder:
            search_title = metadata['prettyFn']
            search_url = f"http://localhost:8989/api/v3/series/lookup?term={search_title}"
            headers = {"X-Api-Key": sonarr_api_key}
            try:
                search_response = requests.get(search_url, headers=headers)
                search_response.raise_for_status()
                search_results = search_response.json()

                if search_results:
                    tvdb_id = search_results[0]['tvdbId']
                    payload = {
                        "title": search_results[0]['title'],
                        "qualityProfileId": 1,
                        "rootFolderPath": selected_folder,
                        "monitored": True,
                        "seasonFolder": True,
                        "seriesType": "standard",
                        "tvdbId": tvdb_id
                    }
                    response = requests.post(sonarr_api_url, json=payload, headers=headers)
                    print("\nSonarr Response:")
                    if response.status_code == 201:
                        display_response(response.json())
                    else:
                        print(f"Error: {response.status_code} - {response.text}")
                else:
                    print("No matching series found in Sonarr's database. Skipping.")
            except Exception as e:
                print(f"Error searching or adding series to Sonarr: {e}")
