import requests  # Webサイトにデータを送るようリクエストする
import datetime  # 日付を取得するためのライブラリ
import os  # OSに関連する機能を提供する。ここでは環境変数にアクセスするための機能。
from dataclasses import dataclass
from dotenv import load_dotenv  # .envファイルの内容を環境変数として読み込む
from bs4 import BeautifulSoup
from typing import List, Optional  # Optional は None を含む可能性がある型を表す


@dataclass
class ProcessingResult:
    success: bool
    soup: Optional[BeautifulSoup] = None
    date: Optional[datetime.date] = None
    trash_kinds: Optional[List[str]] = None
    error_msg: Optional[str] = None

def web_analysis() -> ProcessingResult:
    # .envファイルの内容を環境変数として読み込む
    load_dotenv()
    load_url = os.getenv("LOAD_URL")

    try:
        html = requests.get(load_url)
        html.raise_for_status()
        soup = BeautifulSoup(html.content, "html.parser")
        return ProcessingResult(success=True, soup=soup)
        
    except requests.RequestException as e:
        return ProcessingResult(success=False, error_msg=str(e))

def get_date(date=None) -> ProcessingResult:
    if date is None:
        date = datetime.date.today()
  
    elif isinstance(date, str):
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            value_error = "日付のフォーマットが正しくありません。YYYY-MM-DD形式で指定してください。"
            return ProcessingResult(success=False, error_msg=value_error)
    
    return ProcessingResult(success=True, date=date)

def generate_class_name(date: datetime.date) -> ProcessingResult:
    if not isinstance(date, datetime.date):
        return ProcessingResult(success=False, error_msg="無効な日付オブジェクトです。")
    td_class = "td" + str(date.day)
    return ProcessingResult(success=True, trash_kinds=td_class)

def get_trash_kinds_name(soup: BeautifulSoup, td_class: str) -> ProcessingResult:
    td_element = soup.find("td", class_=td_class)
    if td_element is None:
        none_td_class = "指定された日付の要素が見つかりませんでした。"
        return ProcessingResult(success=False, error_msg=none_td_class)
    
    trash_kinds_elements = td_element.find_all("span", class_="trash_kind_name")
    
    if not trash_kinds_elements:
        none_trash_kinds = "ゴミ収集内容が見つかりませんでした。"
        return ProcessingResult(success=False, error_msg=none_trash_kinds)
    else:
        trash_kinds = [item.get_text() for item in trash_kinds_elements]
        return ProcessingResult(success=True, trash_kinds=trash_kinds)

def handle_result(result: ProcessingResult) -> bool:
    if not result.success:
        print(result.error_msg)
        exit()  # エラーが発生した場合はプログラムを終了
    return True


def line_notify(msg):
    load_dotenv()
    token = os.getenv("LINE_NOTIFY_TOKEN")
    #サーバーに送るパラメータを用意
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + token}
    payload = {'message': msg}
    #requestsモジュールのpost関数を利用してメッセージを送信する
    #ヘッダにトークン情報，パラメータにメッセージを指定する
    requests.post(url, headers=headers, params=payload)


# メイン処理
html_requests = web_analysis()
handle_result(html_requests)

date_result = get_date("2024-10-09")
handle_result(date_result)

td_class_result = generate_class_name(date_result.date)
handle_result(td_class_result)

trash_kinds_result = get_trash_kinds_name(html_requests.soup, td_class_result.trash_kinds)
if handle_result(trash_kinds_result):
    msg = "\n本日は、\n"
    for trash_kind in trash_kinds_result.trash_kinds:
        msg += f"「{trash_kind}」" + "\n"
    msg += "の日です！"
    print(msg)
    line_notify(msg)
    