from urllib import parse
import re

from download_parse import download_page


def get_overview_info(course, course_obj, session):
    """Get information in overview page of each course"""
    video_info = get_video_info(course_obj)
    overview = get_course_desc(course_obj)
    who_should_attend = get_who_should_attend_info(course, course_obj, session)
    takeaways = get_takeaways(course, course_obj, session)
    return {"video_title": video_info['video_title'],
            "video_url": video_info['video_url'],
            "overview": overview,
            "who_should_attend": who_should_attend,
            "course_takeaways": takeaways}


def get_video_info(course_obj):
    """Get course video introduction"""
    video_url = ''
    video_title = ''
    try:
        video_session = course_obj.find('div', attrs={"class": "ytp-title-text"})
        video_title = video_session.find('a').text
        video_url = video_session.find('a').get('href')
    except Exception as err:
        print(f'get_video_info has problem of {err}')
    return {'video_title': video_title,
            'video_url': video_url}


def get_course_desc(course_obj):
    """Get course text introduction"""
    para = ''
    try:
        desc_session_div = course_obj.find('div', attrs={'class': 'rte'})
        children_objs = desc_session_div.findChildren()
        for child in children_objs:
            if child.name == 'h1' or child.name == 'h2':
                continue
            if child.name == 'hr':
                break
            if child.name == 'p':
                para += child.text
            elif child.name == 'h3':
                para += child.text
            else:
                continue
        para = para.replace('\xa0', ' ').strip()
    except Exception as err:
        print(f'get_course_desc has problem of {err}')
    return para


def get_who_should_attend_url(course_url, course_obj):
    """Get who should attend page url"""
    who_should_attend_url = ''
    a_link = course_obj.find('a', text='For whom?')
    if not a_link:
        a_link = course_obj.find('a', text='For Whom?')
    if a_link:
        who_should_attend_url_post = a_link.get('href')
        who_should_attend_url = parse.urljoin(course_url, who_should_attend_url_post)
    return who_should_attend_url


def get_takeaways(course, course_obj, session):
    """Get takeaways description"""
    takeaways = ''
    try:
        takeaways_link = course_obj.find("a", text="Why this programme?").get('href')
        takeaways_url = parse.urljoin(course['url'], takeaways_link)
        page_obj = download_page(takeaways_url, session)
        if page_obj.find('div', attrs={"class": "rte"}).find('p') and page_obj.find('div', attrs={"class": "rte"}).find(
                'li'):
            takeaways_sessions = page_obj.find('div', attrs={"class": "rte"}).find_all('p')
            takeaways_sessions += page_obj.find('div', attrs={"class": "rte"}).find_all('li')
        elif page_obj.find('div', attrs={"class": "rte"}).find('p'):
            takeaways_sessions = page_obj.find('div', attrs={"class": "rte"}).find_all('p')
        elif page_obj.find('div', attrs={"class": "rte"}).find('li'):
            takeaways_sessions = page_obj.find('div', attrs={"class": "rte"}).find_all('li')
        for takeaways_session in takeaways_sessions:
            takeaways += takeaways_session.text
    except Exception as err:
        print(f'get_takeaways encounters problem of {err}')
    return takeaways


def get_who_should_attend_info(course, course_obj, session):
    """Get who should attend description"""
    who_should_attend = ''
    try:
        who_should_attend_url = get_who_should_attend_url(course['url'], course_obj)
        who_should_attend_obj = download_page(who_should_attend_url, session)
        who_should_attend_div = who_should_attend_obj.find('div', attrs={'class': 'rte'})
        children_objs = who_should_attend_div.findChildren()
        who_should_attend = ''
        for child in children_objs:
            if child.name == 'p':
                who_should_attend += '\n' + child.text
            if child.name == 'ul':
                who_should_attend_lis = child.find_all('li')
                for who_should_attend_li in who_should_attend_lis:
                    who_should_attend += who_should_attend_li.text
        who_should_attend = who_should_attend.replace('\xa0', ' ').strip()
    except Exception as err:
        print(f'get_who_should_attend_info encounters problem of {err}')
    return who_should_attend


# **********************************************************************************
def get_overview_info_way2(course_obj):
    """Get overview information in another way for some special courses"""
    video_info = get_video_info(course_obj)
    who_should_attend = get_overview_info_way2(course_obj)
    takeaways = get_takeaways_way2(course_obj)
    overview = get_course_desc_way2(course_obj)
    return {"video_title": video_info['video_title'],
            "video_url": video_info['video_url'],
            "overview": overview,
            "who_should_attend": who_should_attend,
            "course_takeaways": takeaways}


def get_who_should_attend_way2(course_obj):
    """Get who should attend information in another way for some special courses"""
    who_should_attend = ''
    try:
        who_should_attend_related_session = course_obj.find("a", attrs={"id": "forwhom"})
        who_should_attend_sessions = who_should_attend_related_session.parent.parent.parent.find_all('p')
        for who_should_attend_session in who_should_attend_sessions:
            who_should_attend += who_should_attend_session.text
    except Exception as err:
        print(f"who should attend way2 has problem of {err}")
    if not who_should_attend_related_session:
        try:
            who_should_attend_relate_session = course_obj.find("strong", text="who would benefit?")
            who_should_attend_session = who_should_attend_relate_session.parent.parent.find('div',
                                                                                            attrs={
                                                                                                "class": "text-wrap"})
            who_should_attend += who_should_attend_session.text
        except Exception as err:
            print(f"who should attend way2 has problem of {err}")
    if not who_should_attend_related_session:
        try:
            who_should_attend_relate_session = course_obj.find("strong", text="For whom")
            who_should_attend_sessions = who_should_attend_relate_session.parent.parent.find_all('p')
            for who_should_attend_session in who_should_attend_sessions:
                who_should_attend += who_should_attend_session.text
        except Exception as err:
            print(f"who should attend way2 has problem of {err}")
    return who_should_attend


def get_takeaways_way2(course_obj):
    """Get takeaways information in another way for some special courses"""
    takeaways = ''
    try:
        takeaways_related_session = course_obj.find('a', attrs={"id": "why"})
        takeaways_session = takeaways_related_session.parent.parent.parent.find('div', attrs={"class": "text-wrap"})
        if takeaways_session:
            if takeaways_session.find('p'):
                takeaways_session.p.extract()
            takeaways += takeaways_session.text.strip()
        if not takeaways_session:
            takeaways_sessions = takeaways_related_session.parent.parent.find_all('li')
            for takeaways_session in takeaways_sessions:
                takeaways += takeaways_session.text.strip()
        takeaways = takeaways.strip()
        return takeaways
    except Exception as err:
        print(f'get_takeaways_way2 has problem of {err}')
    if not takeaways_related_session:
        try:
            takeaways_related_session = course_obj.find('strong', text="WHY THIS PROGRAMME?")
            takeaways_sessions = takeaways_related_session.parent.parent.find_all('li')
            for takeaways_session in takeaways_sessions:
                takeaways += takeaways_session.text.strip()
        except Exception as err:
            print(f'get_takeaways_way2 has problem of {err}')
    takeaways = takeaways.strip()
    return takeaways


def get_course_desc_way2(course_obj):
    """Get course text introduction in another way for some special courses"""
    desc = ''
    try:
        desc_related_session = course_obj.find('a', attrs={"id": "design"})
        desc_session = desc_related_session.parent.parent.parent.find('div', attrs={"class": "text-wrap"})
        desc = desc_session.text
    except Exception as err:
        print(f'get_course_desc_way2 has problem of {err}')
    if not desc_related_session:
        try:
            desc_session = course_obj.find('div', attrs={"class": "white-block"})
            desc = desc_session.text
        except Exception as err:
            print(f'get_course_desc_way2 has problem of {err}')
    if not desc:
        try:
            desc_sessions = course_obj.find('div', attrs={"class": "grey-block sue-content-block"}).find_all('div',
                                                                                                             attrs={
                                                                                                                 "class": "text-wrap"})
            for desc_session in desc_sessions:
                desc += desc_session.text
        except Exception as err:
            print(f'get_course_desc_way2 has problem of {err}')
    desc = re.sub(r'[\s{2,3}]', ' ', desc)
    return desc
