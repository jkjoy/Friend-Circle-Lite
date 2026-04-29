"""Legacy-compatible crawl entrypoints.

The internal implementation is now delegated to `crawler_service`, but these
functions keep the existing public API stable for `run.py` and external users.
"""

import logging

import requests

from friend_circle_lite import HEADERS_JSON, timeout
from friend_circle_lite.crawler_service import (
    FriendCircleCrawler,
    limit_large_dataset as _limit_large_dataset,
    sort_articles_by_time as _sort_articles_by_time,
)

def fetch_and_process_data(json_url: str, specific_RSS: list = None, count: int = 5, cache_file: str = None):
    """Legacy wrapper around the new crawler orchestration service."""
    return FriendCircleCrawler(
        json_url=json_url,
        count=count,
        specific_rss=specific_RSS,
        cache_file=cache_file,
    ).run()

def sort_articles_by_time(data, future_tolerance_days=2):
    """Legacy wrapper around the refactored sort helper."""
    return _sort_articles_by_time(data, future_tolerance_days=future_tolerance_days)

def marge_data_from_json_url(data, marge_json_url):
    """
    从另一个 JSON 文件中获取数据并合并到原数据中。

    参数：
    data (dict): 包含文章信息的字典
    marge_json_url (str): 包含另一个文章信息的 JSON 文件的 URL。

    返回：
    dict: 合并后的文章信息字典，已去重处理
    """
    try:
        response = requests.get(marge_json_url, headers=HEADERS_JSON, timeout=timeout)
        marge_data = response.json()
    except Exception as e:
        logging.error(f"无法获取链接：{marge_json_url}，出现的问题为：{e}", exc_info=True)
        return data
    
    if 'article_data' in marge_data:
        logging.info(f"开始合并数据，原数据共有 {len(data['article_data'])} 篇文章，第三方数据共有 {len(marge_data['article_data'])} 篇文章")
        data['article_data'].extend(marge_data['article_data'])
        data['article_data'] = list({v['link']:v for v in data['article_data']}.values())
        logging.info(f"合并数据完成，现在共有 {len(data['article_data'])} 篇文章")
    return data

def marge_errors_from_json_url(errors, marge_json_url):
    """
    从另一个网络 JSON 文件中获取错误信息并遍历，删除在errors中，
    不存在于marge_errors中的友链信息。

    参数：
    errors (list): 包含错误信息的列表
    marge_json_url (str): 包含另一个错误信息的 JSON 文件的 URL。

    返回：
    list: 合并后的错误信息列表
    """
    try:
        response = requests.get(marge_json_url, timeout=10)  # 设置请求超时时间
        marge_errors = response.json()
    except Exception as e:
        logging.error(f"无法获取链接：{marge_json_url}，出现的问题为：{e}", exc_info=True)
        return errors

    # 提取 marge_errors 中的 URL
    marge_urls = {item[1] for item in marge_errors}

    # 使用过滤器保留 errors 中在 marge_errors 中出现的 URL
    filtered_errors = [error for error in errors if error[1] in marge_urls]

    logging.info(f"合并错误信息完成，合并后共有 {len(filtered_errors)} 位朋友")
    return filtered_errors

def deal_with_large_data(result, future_tolerance_days=2):
    """Legacy wrapper around the refactored dataset trimming helper."""
    return _limit_large_dataset(result, future_tolerance_days=future_tolerance_days)
