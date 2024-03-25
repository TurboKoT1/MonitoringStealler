import requests
import time
import json
import os
import random
from bs4 import BeautifulSoup

if not os.path.exists("config.json"):
    raise FileNotFoundError("Конфиг не найден!")

with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

ADS_TITLE = config["ads"]["title"]
ADS_DESCRIPTION = config["ads"]["description"]
ADS_VERSIONS = config["ads"]["versions"]

OTHER_DELAY = config["other"]["delay"]

cookies = config["cookies"]
checked_servers = []


def parse_servers():
    response = requests.get('https://monitoringminecraft.ru/novie-servera')
    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        return soup.find_all('tr', class_='server')

    return False


def steal_servers():
    servers = parse_servers()
    if servers:
        for server in servers:
            if server not in checked_servers:
                ip = server.find('td', class_='ip').text.strip()
                review_tag = server.find('td', class_='review')

                if not review_tag:
                    steal_server(ip, get_cookie())
                    time.sleep(OTHER_DELAY)

                checked_servers.append(server)


def steal_server(ip, cookie):
    try:
        print(ip)
        response = requests.post(
            url="https://monitoringminecraft.ru/add-server",
            headers={
                "Cookie": cookie,
                "user-agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'''
            },
            data={
                "address": ip,
                "right": 1
            },
        )

        json = response.json()

        if 'error' in json:
            if json['error'] == 'Вы слишком часто обращаетесь к мониторингу':
                print("[INFO/RATE-LIMIT] Словил рейт лимит, жду 5 секунд..")
                time.sleep(5)
        else:
            server_id = json['id']
            requests.post(
                url=f"https://monitoringminecraft.ru/acc/edit-server-{server_id}",
                headers={
                    "Cookie": cookie,
                    "user-agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'''
                },
                data={
                    "forced_title": f"{ADS_TITLE} - {random.randint(0000, 9999)}",
                    "lure": ADS_DESCRIPTION,
                    "forced_address": "",
                    "site_url": "",
                    "description": "",
                    "public_contacts": "",
                    "client_url": "",
                    "map_url": "",
                    "show_plugins": "on",
                    "banner": "(binary)",
                    "forced_version_tag": "ver" + random.choice(ADS_VERSIONS).replace(".", "a"),
                    "address": "",
                    "submit": "Обновить"
                }
            )
    except requests.JSONDecodeError:
        print("eshkere")


def remove_server(server_id: int, cookie: dict):
    requests.post(
        url=f"https://monitoringminecraft.ru/acc/remove-server-{server_id}",
        headers={
            "Cookie": cookie,
            "user-agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'''
        }
    )


def get_cookie() -> dict:
    for cookie in cookies:
        if len(get_servers(cookie)) < 2:
            return cookie

    clean_last_servers()
    return get_cookie()


def clean_last_servers():
    for cookie in cookies:
        servers = get_servers(cookie)
        if servers:
            first_server = servers[0]
            link_cell = first_server.find('td').find('a', href=True)
            if link_cell:
                server_link = link_cell['href']
                parts = server_link.split('/')
                server_id = parts[-1]
                remove_server(server_id, cookie)


def get_servers(cookie: dict) -> list:
    servers_list = []

    response = requests.post(
        url="https://monitoringminecraft.ru/acc/servers",
        headers={
            "Cookie": cookie,
            "user-agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'''
        }
    )
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='newservers')
    if table:
        servers = table.find_all('tr')
        for server in servers:
            servers_list.append(server)

    return servers_list


if __name__ == "__main__":
    while True:
        steal_servers()
        time.sleep(60)
