import requests # Webサイトにデータを送るようリクエストする
import datetime # 日付を取得するためのライブラリ
import os # OSに関連する機能を提供する。ここでは環境変数にアクセスするための機能。
from dotenv import load_dotenv # .envファイルの内容を環境変数として読み込む
from bs4 import BeautifulSoup

# .envファイルの内容を環境変数として読み込む
load_dotenv()

# Webページを取得して解析する
load_url = os.getenv("LOAD_URL")
html = requests.get(load_url)
soup = BeautifulSoup(html.content, "html.parser")

# 今日の日付を取得
today = datetime.date.today()

# 今日の日付のタグを取り出す
td_class = "td" + str(today.day)
date = soup.find("td", class_=td_class)

# その日のごみ収集内容を取り出す
trash_kind = date.find("span", class_="trash_kind_name")

print(trash_kind.text)