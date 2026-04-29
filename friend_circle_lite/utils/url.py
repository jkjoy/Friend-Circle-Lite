import logging
from urllib.parse import urlparse, urljoin
import re

def replace_non_domain(link: str, blog_url: str) -> str:
    """
    检测并处理相对地址、非正常域名（如 IP 地址或 localhost）。
    - 如果是相对地址（无协议和域名），自动拼接 blog_url
    - 如果是 localhost 或 IP 地址，替换为 blog_url
    - 如果是正常的绝对地址，直接返回

    :param link: 原始地址字符串
    :param blog_url: 博客的基础地址
    :return: 处理后的完整地址字符串
    """
    if not link:
        return link
    
    try:
        parsed = urlparse(link)
        
        # 情况1: 相对地址（没有 scheme 和 netloc）
        # 例如: "/post/article.html" 或 "post/article.html"
        if not parsed.scheme and not parsed.netloc:
            # 使用 urljoin 来正确处理相对路径
            return urljoin(blog_url, link)
        
        # 情况2: localhost 或 IP 地址
        if 'localhost' in parsed.netloc or re.match(r'^\d{1,3}(\.\d{1,3}){3}$', parsed.netloc):
            # 提取 path + query + fragment
            path = parsed.path or '/'
            if parsed.query:
                path += '?' + parsed.query
            if parsed.fragment:
                path += '#' + parsed.fragment
            return urljoin(blog_url.rstrip('/') + '/', path.lstrip('/'))
        
        # 情况3: 正常的绝对地址，直接返回
        return link
        
    except Exception as e:
        logging.warning(f"替换链接时出错：{link}, error: {e}")
        return link
