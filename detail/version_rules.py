"""Get version detail for courses"""
from urllib.parse import urljoin
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

from detail.format_details import get_currency, format_date, get_symbol_currency, find_directly_start_date1, \
    filter_locations
from download_parse import download_page


def get_version_info(course, course_obj, session):
    '''
    :param course_obj
    :return: practical info page link
    '''
    no_version_url = [
        "https://www.vlerick.com/en/programmes/management-programmes/human-resource-management/vlerick-hr-day",
        "https://www.vlerick.com/en/programmes/management-programmes/entrepreneurship/marketing-leadership-masterclass",
        "https://www.vlerick.com/en/programmes/management-programmes/entrepreneurship/scale-up-masterclass"]
    directly_version_url = [
        "https://www.vlerick.com/en/programmes/management-programmes/accounting-finance/excellence-in-corporate-finance",
        "https://www.vlerick.com/en/programmes/management-programmes/general-management/executive-development-programme-middle-managers"]

    if course["url"] in no_version_url:
        version_info = no_version_info()
        return version_info

    if course["url"] in directly_version_url:
        version_info = directly_version_info(course, session)
        return version_info
    version_info = {}
    practical_a_tag = course_obj.find('a', text=re.compile("Practical"))
    if not practical_a_tag:
        practical_a_tag = course_obj.find('a', text=re.compile("Practicalities"))
    if practical_a_tag:
        practical_info_link = urljoin(course["url"], practical_a_tag.get('href'))
        practical_page = download_page(practical_info_link, session)
        version_info = course_version_info_way1(course, course_obj, practical_page)
    return version_info


def location_for_one_version_course(practical_info_page_obj):
    '''
    :param practical_info_page_obj: -> Object
    :return: location: -> String
    '''
    location = []
    try:
        loc_session = practical_info_page_obj.find('p', attrs={'id': 'corporatebody_0_phLocations'})
        loc_session.strong.extract()
        location = loc_session.text.strip()
        if '\n' in location:
            location = location.replace('\n', '').strip()
    except Exception as err:
        print(f'location has some problem of: {err}')
    return [location]


def fee_in_pratical_page(practical_info_page_obj):
    '''
    :param practical_info_page_obj: -> Object
    :return: tuition related information -> Object
    '''
    obj = {'tuition': '',
           'currency': '',
           'tuition_note': ''}
    try:
        fee_session = practical_info_page_obj.find('p', attrs={'id': 'corporatebody_0_phFees'})
        fee_session_text_list = fee_session.text.split()
        tuition = fee_session_text_list[1]
        currency = fee_session_text_list[2]
        tuition_desc = ' '.join(fee_session_text_list[3:])
        obj['tuition'] = tuition
        obj['currency'] = get_currency(currency)
        obj['tuition_note'] = tuition_desc
    except Exception as err:
        print(err)
    return obj


def course_version_info_way1(course, course_obj, practical_info_page_obj):
    '''
    :param course_obj
    :return:
    '''
    versions = 1
    locations = set()
    versions_info_lst = list()
    try:
        fee_related_info = fee_in_pratical_page(practical_info_page_obj)
        ver_outside_obj = course_obj.find('div', attrs={"class": "editionsWrapper"})
        if ver_outside_obj:
            ver_objs = ver_outside_obj.find_all('div')
            length = length_for_multiple_version_course(practical_info_page_obj)
            for obj in ver_objs:
                version_obj = {}
                location_link = obj.find('a')
                location = location_link.text
                if '...' in location:
                    versions = 10
                    break
                if location not in locations:
                    if '\n' in location:
                        location = location.replace('\n', '').strip()
                    locations.add(location)
                    effective_start_date_session = obj.find_all('p')[0]
                    effective_start_date_session.strong.extract()
                    effective_start_date = effective_start_date_session.text.strip('\n')
                    effective_start_date = format_date(effective_start_date)
                    language_session = obj.find_all('p')[2]
                    language_session.strong.extract()
                    language = language_session.text.strip('\n')
                    version_obj['location'] = [location]
                    version_obj['effective_date_start'] = effective_start_date
                    version_obj['languages'] = language
                    version_obj.update(fee_related_info)
                    duration_type = get_duration_type(length)
                    duration_num = get_duration_num(length)
                    effective_end_date = calculate_end_date(effective_start_date, duration_type, duration_num)
                    version_obj['effective_date_end'] = effective_end_date
                    duration_type = "duration_" + duration_type
                    version_obj[duration_type] = duration_num
                    versions_info_lst.append(version_obj)
        else:
            pass
    except Exception as err:
        print(f'{course["url"]} first find_all has problems {err}')
    if len(locations) != 0:
        versions = len(locations)
    try:
        for version_obj in versions_info_lst:
            version_obj['versions'] = versions
    except Exception as err:
        print(f'course_version_info_way1 has problem of {err}')
    if versions == 1:
        version_obj = {}
        info_session = course_obj.find('div', attrs={'class': 'programDetails'})
        if info_session:
            length_session = info_session.find_all('p')[1]
            length_session.strong.extract()
            length = length_session.text.strip('\n')
            effective_start_date_session = info_session.find_all('p')[2]
            effective_start_date_session.strong.extract()
            effective_start_date = effective_start_date_session.text
            effective_start_date = format_date(effective_start_date)
            duration_type = get_duration_type(length)
            duration_num = get_duration_num(length)
            effective_end_date = calculate_end_date(effective_start_date, duration_type, duration_num)
            language_session = info_session.find_all('p')[3]
            language_session.strong.extract()
            language = language_session.text
            version_obj['effective_date_start'] = effective_start_date.strip('\n')
            version_obj['effective_date_end'] = effective_end_date
            duration_type = "duration_" + duration_type
            version_obj[duration_type] = duration_num
            version_obj['languages'] = language.strip('\n')
            version_obj['versions'] = versions
            version_obj['location'] = location_for_one_version_course(practical_info_page_obj)

            fee_related_info = fee_in_pratical_page(practical_info_page_obj)
            version_obj.update(fee_related_info)

            versions_info_lst.append(version_obj)
    return versions_info_lst


def length_for_multiple_version_course(practical_info_page_obj):
    """Get course duration for multiple version courses"""
    length = ''
    try:

        length_session = practical_info_page_obj.find('p', attrs={'id': 'corporatebody_0_phLength'})
        length_session.strong.extract()
        length = length_session.text.strip()
    except Exception as err:
        print(f'length_for_multiple_version_course encounters problem of {err}')
    return length


def get_duration_type(length):
    """Get duration type"""
    length = str(length)
    if 'days' in length or 'Days' in length:
        l_type = 'days'
    if 'weeks' in length or 'Weeks' in length:
        l_type = 'weeks'
    if 'months' in length:
        l_type = 'months'
    return l_type


def get_duration_num(length):
    """Get duration number"""
    num = ''
    num = re.findall(r'\d+', length)[0]
    return num


def calculate_end_date(start_date, duration_type, duration_num):
    """Calculate end date by start date and duration"""
    if duration_type == "months":
        date = datetime.strptime(start_date, "%Y-%m-%d")
        m_m = int(duration_num)
        end_date = date + relativedelta(months=+m_m)
        end_date = end_date.strftime("%Y-%m-%d")
        return end_date
    if duration_type == "weeks":
        date = datetime.strptime(start_date, "%Y-%m-%d")
        week_num = int(duration_num)
        end_date = date + relativedelta(weeks=+week_num)
        end_date = end_date.strftime("%Y-%m-%d")
        return end_date
    if duration_type == "days":
        date = datetime.strptime(start_date, "%Y-%m-%d")
        day_num = int(duration_num)
        end_date = date + relativedelta(days=+day_num)
        end_date = end_date.strftime("%Y-%m-%d")
        return end_date
    return ""


def get_version_info_way2(course_obj):
    """get version information in another way for some special courses"""
    version_info = []
    table_session = course_obj.find('div', attrs={"id": "corporateright_0_TextBlock"})
    if table_session:
        lis = table_session.find_all('li')
        if lis:
            first_li = lis[0]
            version = {"effective_date_start": "",
                       "effective_date_end": "",
                       "duration_months": 3,
                       "languages": 'English',
                       "credential": "Certificate",
                       "versions": 1}
            price = lis[-1]
            tuition_info = get_price_info2(price)
            new_version = {**version, **tuition_info}
            version_info.append(new_version)
        else:
            txt = table_session.find_all('td')[-1].text
            txt_list = txt.split()
            if 'euros' in txt:
                duration_num, duration_type, start_date, language, location, tuition, currency, tuition_note1, \
                tuition_note2, tuition_note3 = txt_list
                tuition_note = tuition_note1 + tuition_note2 + tuition_note3
            else:
                duration_num, duration_type, start_date, language, location, tuition, currency, tuition_note1, \
                tuition_note2 = \
                    txt_list[0], txt_list[1], txt_list[2], txt_list[-6], txt_list[-5], txt_list[-3], txt_list[-4], \
                    txt_list[-2], txt_list[-1]
                tuition_note = tuition_note1 + tuition_note2
            duration_num = int(duration_num)
            currency = get_symbol_currency(currency)
            start_date = get_txt_start_date(start_date)
            end_date = calculate_end_date(start_date, duration_type, duration_num)
            duration_type = 'duration_' + duration_type
            location = [location]
            tuition = get_tuition2(tuition)
            version = {"location": location,
                       "effective_date_start": start_date,
                       "effective_date_end": end_date,
                       duration_type: duration_num,
                       "languages": language,
                       "currency": currency,
                       "tuition": tuition,
                       "tuition_note": tuition_note,
                       "versions": 1}
            version_info.append(version)
    return version_info


def get_price_info2(price):
    """Get price detail in another way for some special courses"""
    price = price.text
    tuition = ''
    currency = ''
    tuition_note = ''
    try:
        tuition, currency, tuition_note = price.partition("EUR")
        currency = get_currency(currency)
        tuition = get_tuition2(tuition)
        tuition_note = tuition_note.strip().replace("\xa0", '')
    except:
        pass
    return {"tuition": tuition,
            "currency": currency,
            "tuition_note": tuition_note}


def get_tuition2(tuition_text):
    """Match tuition by regex"""
    num = re.findall(r'\d+', tuition_text)
    tuition = ''.join(num)
    return int(tuition)


def get_useful_txt_duration_type(txt):
    """Extract duration type"""
    d_type = ''
    if 'days' in txt:
        d_type = 'days'
    elif 'weeks' in txt:
        d_type = 'weeks'
    elif 'months' in txt:
        d_type = 'months'
    return d_type


def get_txt_start_date(txt):
    """format date"""
    date_list = txt.split('/')
    date = date_list[0]
    month = date_list[1]
    year = date_list[2]
    start_date = f'{year}-{month}-{date}'
    return start_date


def no_version_info():
    """Hard code course that does not have version detail"""
    version = {"location": [],
               "effective_date_start": "",
               "effective_date_end": "",
               "languages": "English",
               "currency": "",
               "tuition_note": "",
               "versions": 1}
    return [version]


def directly_version_info(course, session):
    """Get version information for two special courses"""
    version_list = []
    version_page_url = course['url'] + '/practical-info'
    page = download_page(version_page_url, session)
    if course['url'] == "https://www.vlerick.com/en/programmes/management-programmes/accounting-finance/excellence-in-corporate-finance":
        version_info = get_directly_version1(page)
    elif course['url'] == "https://www.vlerick.com/en/programmes/management-programmes/general-management/executive-development-programme-middle-managers":
        version_info = get_directly_version2(page)
    version_list.append(version_info)
    return version_list


def get_directly_version1(page):
    """The first way to extract specific details of version"""
    date_session = page.find("p", attrs={"id": "corporatebody_0_phDates"})
    length_session = page.find("p", attrs={"id": "corporatebody_0_phLength"})
    locations_session = page.find("p", attrs={"id": "corporatebody_0_phLocations"})
    language_session = page.find("p", attrs={"id": "corporatebody_0_phLanguage"})
    fee_session = page.find("p", attrs={"id": "corporatebody_0_phFees"})

    date_session = date_session.find_next("ul").find('li')
    length_session.strong.extract()
    locations_session.strong.extract()
    language_session.strong.extract()
    fee_session.strong.extract()

    date_text = date_session.text.strip()
    length_text = length_session.text.strip()
    location_text = locations_session.text.strip()
    language_text = language_session.text.strip()
    fee_text = fee_session.text.strip()

    start_date = find_directly_start_date1(date_text)
    duration_type = get_duration_type(length_text)
    duration_num = get_duration_num(length_text)
    location = location_text.split()
    location = filter_locations(location)
    tuition = get_tuition2(fee_text)
    currency = get_symbol_currency(fee_text)
    language = language_text
    end_date = calculate_end_date(start_date, duration_type, duration_num)
    duration_type = 'duration_' + duration_type
    version_info = {"location": location,
                    "effective_date_start": start_date,
                    "effective_date_end": end_date,
                    "languages": language,
                    "tuition": int(tuition),
                    "currency": currency,
                    duration_type: int(duration_num),
                    "tuition_note": "",
                    "versions": 1}
    return version_info


def get_directly_version2(page):
    """The second way to extract specific details of version"""
    date_session = page.find("p", attrs={"id": "corporatebody_0_phDates"})
    length_session = page.find("p", attrs={"id": "corporatebody_0_phLength"})
    locations_session = page.find("p", attrs={"id": "corporatebody_0_phLocations"})
    language_session = page.find("p", attrs={"id": "corporatebody_0_phLanguage"})
    fee_session = page.find("p", attrs={"id": "corporatebody_0_phFees"})

    date_session.strong.extract()
    length_session.strong.extract()
    locations_session.strong.extract()
    language_session.strong.extract()
    fee_session.strong.extract()

    date_text = date_session.text.split(',')[0].strip()
    length_text = length_session.text.strip()
    location_text = locations_session.text.strip()
    language_text = language_session.text.strip()
    fee_text = fee_session.text.strip()

    start_date = find_directly_start_date1(date_text)
    duration_type = get_duration_type(length_text)
    duration_num = get_duration_num(length_text)
    location = location_text.split()
    location = filter_locations(location)
    tuition = int(fee_text.split()[0])
    currency = get_symbol_currency(fee_text)
    language = language_text
    end_date = calculate_end_date(start_date, duration_type, duration_num)
    tuition_note = fee_text.split()[-1]
    version_info = {"location": location,
                    "effective_date_start": start_date,
                    "effective_date_end": end_date,
                    "languages": language,
                    "tuition": int(tuition),
                    "currency": currency,
                    duration_type: int(duration_num),
                    "versions": 1,
                    "tuition_note": tuition_note}
    return version_info
