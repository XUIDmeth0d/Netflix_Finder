import os
import re
import threading
import logging
import colorama
import time
import requests
from bs4 import BeautifulSoup
import urllib3

colorama.init()

def find_netflix_accounts(soup):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = set(re.findall(email_pattern, soup.text))
    
    for email in emails:
        account_info = f"Potential Netflix account: Email - {email}"
        if not is_email_in_file(email):
            save_to_file(account_info)
            logging.info(f"Saved potential account: {account_info}")

def save_to_file(info):
    try:
        with open("finds.txt", "a") as f:
            f.write(info + '\n')
    except Exception as e:
        logging.error(f"Error in save_to_file: {e}")

def get_soup():
    try:
        with open("netflix_page.html", "rb") as f:
            content = f.read()
        return BeautifulSoup(content, "html.parser")
    except FileNotFoundError:
        logging.error("Error: netflix_page.html file not found.")
        return None

def is_email_in_file(email):
    with open("finds.txt", "r") as f:
        return any(email == line.strip() for line in f)

def animate_banner():
    animation = "|/-\\"
    idx = 0
    while True:
        if os.path.exists("finds.txt"):
            current_size = os.path.getsize("finds.txt")
            print(f"\rLooking for potential Netflix accounts... {animation[idx % len(animation)]}", end="")
            idx += 1
            time.sleep(0.1)
        else:
            time.sleep(1)  # Wait for 1 second if the file doesn't exist

def make_proxy_request(url, proxy_file):
    session = requests.session()
    proxies = get_proxies_from_file(proxy_file)
    try:
        for proxy in proxies:
            session.proxies = {'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'}
            response = session.get(url, verify=False)  # Suppress SSL certificate verification warnings
            if response.status_code == 200:
                return response
    except Exception as e:
        logging.error("Error making request: %s", e)
        return None

def get_proxies_from_file(proxy_file):
    proxies = []
    try:
        with open(proxy_file, 'r') as file:
            proxies = file.read().splitlines()
    except FileNotFoundError:
        logging.error("Error: Proxy file not found.")
    return proxies

def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print(colorama.Fore.BLUE + "Welcome to XUID - Netflix Account Finder!")
    print(colorama.Fore.BLUE + "Looking for potential Netflix accounts...")
    
    banner_thread = threading.Thread(target=animate_banner)
    banner_thread.start()
    
    try:
        logging.basicConfig(filename="netflix_account_finder.log", level=logging.ERROR)
        
        # URL to scrape
        url = "https://ytricks.co/free-netflix-account-trick/"  # replace with the URL you want to scrape
        proxy_file = "socks5_proxies.txt"  # Specify the path to your SOCKS5 proxy file
        
        response = make_proxy_request(url, proxy_file)
        if response:
            soup = BeautifulSoup(response.text, "html.parser")
            find_netflix_accounts(soup)
        
    except Exception as e:
        logging.error(f"Error in main: {e}")

    banner_thread.join()

if __name__ == "__main__":
    main()
