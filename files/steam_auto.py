from steampy.client import SteamClient
from files.dannie import api_steam, login_steam, password_steam, path_guard
import time
steam_client = SteamClient(api_steam)
time.sleep(3)
steam_client.login(login_steam, password_steam, path_guard)
session = steam_client.is_session_alive()