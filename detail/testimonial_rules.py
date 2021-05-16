"""Get testimonial detail for each course"""
from urllib import parse
from urllib.parse import urljoin

from download_parse import download_page


def get_testimonial_info(course,course_obj,session):
    """Extract testimonial details"""
    testimonial_list = []
    try:
        if course['url'] == "https://www.vlerick.com/en/programmes/management-programmes/digital-transformation/digital-leadership":
            testimonial_list = get_digital_leadership_testis(course_obj)
        elif course['url'] == "https://www.vlerick.com/en/programmes/management-programmes/people-management-leadership/negotiate-for-success":
            testimonial_list = get_negotiate_for_success_testis(course['url'],course_obj)
        else:
            testimonial_page = get_testi_page_url(course_obj,session)
            testimonial_list = get_testimonials(testimonial_page)
    except Exception as err:
        print(f'get_testimonial_info encounters problem of {err}')
    return testimonial_list


def get_digital_leadership_testis(course_obj):
    """"""
    testis = []
    return testis


def get_negotiate_for_success_testis(course_url,course_obj):
    """Get testimonials information for special course of get negotiate for success"""
    testis = []
    testis_related_session = course_obj.find('strong',text="testimonial")
    first_name_com_title = testis_related_session.find_next('p')
    first_name = first_name_com_title.strong.text
    first_title = first_name_com_title.find('span').text
    first_com = first_name_com_title.text.replace(first_title,'').replace(first_name,'').strip()
    first_pic_link = first_name_com_title.find_next('table').find('img').get('src')
    first_pic_url = parse.urljoin(course_url,first_pic_link)
    first_desc = first_name_com_title.find_next('table').find('em').text
    if '-' in first_name:
        first_name = first_name.replace('-','').strip()
    first_testi = {"name":first_name,
                   "title":first_title,
                   "company":first_com,
                   "desc":first_desc,
                   "pic_url":first_pic_url,
                   "visual_url":"",
                   "publish":"public"}
    sec_name_title_com = testis_related_session.find_next('p').find_next('p').find_next('p')
    sec_name = sec_name_title_com.strong.text.replace('-','').strip()
    sec_title = sec_name_title_com.span.text
    sec_name_title_com.strong.extract()
    sec_com = sec_name_title_com.text.replace(sec_title,'').strip()
    sec_pic_link = sec_name_title_com.find_next_sibling().img.get('src')
    sec_pic_url = parse.urljoin(course_url,sec_pic_link)
    sec_desc = sec_name_title_com.find_next_sibling().find_next_sibling().text.strip()
    sec_testi = {"name": sec_name,
                   "title": sec_title,
                   "company": sec_com,
                   "desc": sec_desc,
                   "pic_url": sec_pic_url,
                   "visual_url": "",
                   "publish": "public"}
    testis.append(first_testi)
    testis.append(sec_testi)
    return testis


def get_testimonials(testimonial_page_obj):
    """Get one testimonial's information"""
    testi_trs = testimonial_page_obj.find_all('tr')
    testi_list = []
    for testi_tr in testi_trs:
        name = ''
        title = ''
        company = ''
        testi_desc = ''
        pic_url = ''
        visual_url = ''
        testi_dict = {}
        try:
            all_td = testi_tr.find_all('td')
            all_text = ''
            for one_td in all_td:
                if one_td.strong:
                    name = one_td.strong.text
                all_desc = ''
                if one_td.em:
                    all_em = one_td.find_all('em')
                    for one_em in all_em:
                        all_desc += one_em.text
                if one_td.text:
                    all_text += one_td.text
                if one_td.img:
                    pic_url = one_td.img.get('src')
                if one_td.iframe:
                    visual_url = one_td.iframe.get('src')
                if one_td.find('span',attrs={"class":"legend"}):
                    title = one_td.find('span',attrs={"class":"legend"}).text
            company = all_text.replace(name,'').replace(all_desc,'').replace(title,'')
            if '“' in company:
                idx = company.index('“')
                company = company[:idx]
            if '\"' in company:
                idx = company.index('\"')
                company = company[:idx]
            company = company.replace(',','').replace('\n',' ').strip()
            title = title.strip()
            if '\xa0' in title:
                title = title.replace('\xa0',' ')
            if '\xa0' in all_desc:
                all_desc = all_desc.replace('\xa0',' ')
            if '\xa0' in company:
                company = company.replace('\xa0',' ')
            if '\xa0' in name:
                name = name.replace('\xa0',' ')
        except Exception as err:
            print(err)
        if len(pic_url)>0 and not pic_url.startswith("https"):
            pic_url = urljoin("https://www.vlerick.com/", pic_url)
        integrate_testi = {"name":name,
                           "title":title,
                           "company":company,
                           "desc":all_desc,
                           "pic_url":pic_url,
                           "visual_url":visual_url,
                           "publish":"public"}
        testi_list.append(integrate_testi)
    return testi_list


def get_testi_page_url(course_obj,session):
    """Get testimonial page link"""
    url = ''
    link = course_obj.find('a',text="Testimonials").get('href')
    url = urljoin("https://www.vlerick.com/",link)
    page = download_page(url, session)
    return page
