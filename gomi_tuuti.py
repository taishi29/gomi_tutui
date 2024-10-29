import requests
import os # OSに関連する機能を提供する。ここでは環境変数にアクセスするための機能。
from dotenv import load_dotenv # .envファイルの内容を環境変数として読み込む
from bs4 import BeautifulSoup

# .envファイルの内容を環境変数として読み込む
load_dotenv()

# Webページを取得して解析する
load_url = os.getenv("LOAD_URL")
html = requests.get(load_url)
soup = BeautifulSoup(html.content, "html.parser")

print(soup)