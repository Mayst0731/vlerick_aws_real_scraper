"""Scrape category list. Takes in base_url. Returns all categories needed"""
from urllib import parse
from download_parse import download_page


def extract_categories(base_url, session):
    """Scrape category list
        Parameters:
            base_url(str): url for scraping categories
            session(object): A reusable TCP connection
        Returns:
            cate_list (list): A list contains each category's url
    """
    cate_list = []
    category_page_obj = download_page(base_url, session)
    category_divs = category_page_obj.find_all('div', attrs={'class': 'grid_8'})
    category_divs += category_page_obj.find_all('div', attrs={'class': 'grid_8 omega'})
    category_divs += category_page_obj.find_all('div', attrs={'class': 'grid_8 alpha'})

    check_repeat = set()

    for category_info in category_divs:
        category_name = category_info.find('h2').text
        prefix = category_info.parent.previous_sibling.previous_sibling.previous_sibling.h3.text.strip()
        if category_name not in check_repeat:
            cate = dict()
            category_name = prefix + ' - ' + category_name
            check_repeat.add(category_name)
            category_url_post = category_info.find('ul').find('a').get('href')
            category_url = parse.urljoin(base_url, category_url_post)
            cate['category'] = category_name
            cate['url'] = category_url
            cate['parent_url'] = base_url
            cate_list.append(cate)
    return cate_list
