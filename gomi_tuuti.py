import requests  # Webサイトにデータを送るようリクエストする
import datetime  # 日付を取得するためのライブラリ
import os  # OSに関連する機能を提供する。ここでは環境変数にアクセスするための機能。
from dataclasses import dataclass
from dotenv import load_dotenv  # .envファイルの内容を環境変数として読み込む
from bs4 import BeautifulSoup
from typing import Optional  # Optional は None を含む可能性がある型を表す


@dataclass
class ProcessingResult:
    success: bool
    soup: Optional[BeautifulSoup] = None
    date: Optional[datetime.date] = None
    trash_kind: Optional[str] = None
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
    return ProcessingResult(success=True, trash_kind=td_class)

def get_trash_kind_name(soup: BeautifulSoup, td_class: str) -> ProcessingResult:
    td_element = soup.find("td", class_=td_class)
    if td_element is None:
        none_td_class = "指定された日付の要素が見つかりませんでした。"
        return ProcessingResult(success=False, error_msg=none_td_class)
    
    trash_kind = td_element.find("span", class_="trash_kind_name")
    if trash_kind is None:
        none_trash_kind = "ゴミ収集内容が見つかりませんでした。"
        return ProcessingResult(success=False, error_msg=none_trash_kind)
    
    return ProcessingResult(success=True, trash_kind=trash_kind.text)

def handle_result(result: ProcessingResult) -> bool:
    if not result.success:
        print(result.error_msg)
        exit()  # エラーが発生した場合はプログラムを終了
    return True


# メイン処理
html_requests = web_analysis()
handle_result(html_requests)

date_result = get_date()
handle_result(date_result)

td_class_result = generate_class_name(date_result.date)
handle_result(td_class_result)

trash_kind_result = get_trash_kind_name(html_requests.soup, td_class_result.trash_kind)
if handle_result(trash_kind_result):
    print(f"本日は、「{trash_kind_result.trash_kind}」の日です！")
    