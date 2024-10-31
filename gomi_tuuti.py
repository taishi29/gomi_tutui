import requests  # Webサイトにデータを送るようリクエストする機能
import datetime  # 日付を取得するための機能
import os  # OSに関連する機能を提供する。ここでは環境変数にアクセスするための機能
from dataclasses import dataclass # データ型を明確にしたデータ構造を作成するための機能
from dotenv import load_dotenv  # .envファイルの内容を環境変数として読み込むための機能
from bs4 import BeautifulSoup # HTMLデータを解析する機能
from typing import List, Optional  # Optional は None を含む可能性がある型を表す


load_dotenv() # .envファイルの内容を環境変数として読み込む


# 関数の処理結果を格納するデータクラス
@dataclass
class ProcessingResult:
    success: bool
    soup: Optional[BeautifulSoup] = None
    date: Optional[datetime.date] = None
    td_class: Optional[str] = None
    trash_kinds: Optional[List[str]] = None
    error_msg: Optional[str] = None


# URLを環境変数として読み込み、htmlリクエストを送信、解析する関数
def web_analysis() -> ProcessingResult:
    load_url = os.getenv("LOAD_URL")

    try:
        html = requests.get(load_url)
        html.raise_for_status()
        soup = BeautifulSoup(html.content, "html.parser")
        return ProcessingResult(success=True, soup=soup)
        
    except requests.RequestException as e:
        return ProcessingResult(success=False, error_msg=str(e))


# 引数の日付を datetime型にする。また、引数が無かったら今日の日付を取得する関数
def get_date(date: Optional[str] = None) -> ProcessingResult:
    if date is None:
        date = datetime.date.today()
  
    elif isinstance(date, str):
        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            value_error = "日付のフォーマットが正しくありません。YYYY-MM-DD形式で指定してください。"
            return ProcessingResult(success=False, error_msg=value_error)
    
    return ProcessingResult(success=True, date=date)


# "指定された日or今日(td_class)"の情報を取得するために、HTMLクラス属性を設定する関数(例：<td class="td5"> ※5は日付)
def generate_class_name(date: datetime.date) -> ProcessingResult:
    if not isinstance(date, datetime.date):
        return ProcessingResult(success=False, error_msg="無効な日付オブジェクトです。")
   
    td_class = "td" + str(date.day) 
    return ProcessingResult(success=True, td_class=td_class)


# "指定された日or今日(td_element)"の"ごみ収集内容(trash_kinds_elements)"を取得するための関数(例：<td class="td5">の<p class="trash_kind_name">)
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


# 各処理のエラーハンドリングをまとめた関数
def handle_result(result: ProcessingResult) -> bool:
    if not result.success:
        print(result.error_msg)
        exit()  # エラーが発生した場合はプログラムを終了
    return True


# Line notifyを用いて、引数で受け取った処理結果のメッセージをLINEで通知する関数
def line_notify(msg: str):
    token = os.getenv("LINE_NOTIFY_TOKEN")
    # サーバーに送るパラメータを用意
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': 'Bearer ' + token}
    payload = {'message': msg}
    # requestsモジュールのpost関数を利用してメッセージを送信する
    # ヘッダにトークン情報，パラメータにメッセージを指定する
    requests.post(url, headers=headers, params=payload)


# メイン処理
'''
～メイン処理の簡単な流れ～
1. HTMLデータを解析
2. 取得したいごみ収集日を設定
3. 2を基に、HTMLのclass属性を設定
4. 3のHTMLのclass属性で取得したいごみ収集日の情報をスクレイピングし、そこからごみ収集内容を取得
5. LINEで通知するメッセージを作成し、実際に送信する
'''
html_requests = web_analysis()
handle_result(html_requests)

date_result = get_date()
handle_result(date_result)

td_class_result = generate_class_name(date_result.date)
handle_result(td_class_result)

trash_kinds_result = get_trash_kinds_name(html_requests.soup, td_class_result.td_class)
if handle_result(trash_kinds_result):
    msg = "\n本日は、\n"
    for trash_kind in trash_kinds_result.trash_kinds:
        msg += f"「{trash_kind}」" + "\n"
    msg += "の日です！"
    print(msg)
    line_notify(msg)
    