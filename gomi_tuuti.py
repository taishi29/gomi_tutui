import requests # Webサイトにデータを送るようリクエストする
import datetime # 日付を取得するためのライブラリ
import os # OSに関連する機能を提供する。ここでは環境変数にアクセスするための機能。
from dotenv import load_dotenv # .envファイルの内容を環境変数として読み込む
from bs4 import BeautifulSoup

def web_analysis():
    # .envファイルの内容を環境変数として読み込む
    load_dotenv()
    load_url = os.getenv("LOAD_URL")

    try:
        html = requests.get(load_url)
        html.raise_for_status()
    except requests.RequestException as e:
        print(f"Webページの取得に失敗しました：{e}")
        return None
 
    soup = BeautifulSoup(html.content, "html.parser")
    return soup
    
def generate_class_name():
    # 今日の日付を取得
    today = datetime.date.today()

    # 今日の日付のクラスを設定
    td_class = "td" + str(today.day)
    return td_class
    
def get_trash_kind_name(soup, td_class):
    date = soup.find("td", class_=td_class)
    if date is None:
        print("指定された日付の要素が見つかりませんでした。")
        return None
    
    # その日のごみ収集内容を取り出す
    trash_kind = date.find("span", class_="trash_kind_name")
    if trash_kind is None:
        print("ゴミ収集内容が見つかりませんでした。")
        return None
    
    return trash_kind




