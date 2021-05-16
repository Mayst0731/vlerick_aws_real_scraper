"""Downloads and parses web pages. Takes in reusable TCP session and url. Returns parsed tree form web page object"""
import bs4


def download_page(url, session):
    """ Downloads and parse web page using its url and reusable TCP session"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&r=http%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt='}

    source = session.get(url, headers=headers).text
    page = bs4.BeautifulSoup(source, 'html.parser')
    return page
