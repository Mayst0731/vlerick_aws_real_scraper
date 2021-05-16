"""Scrape course list. Takes in the whole category list. Returns course list for all categories"""
from urllib import parse
from download_parse import download_page


def extract_courses(category_list, session):
    """Scrape course list

        Parameters:
            category_list(list): Category list contains each category's url
            session(object): A reusable TCP connection
        Returns:
            lst (list): A list contains each course's url
    """
    lst = []
    course_dict = dict()
    for cate in category_list:
        category_page_obj = download_page(cate['url'], session)
        course_elements = category_page_obj.find_all('div', attrs={'class': 'programItem clearfix grid_12 alpha'})
        course_elements += category_page_obj.find_all('div', attrs={'class': 'programItem clearfix grid_12 omega'})
        length = len(course_elements)
        print(f'length of courses {length}')
        for course_element in course_elements:
            course_name = course_element.find('h2').text
            if course_name not in course_dict:
                course_url_post = course_element.find('h2').a.get('href')
                course_url = parse.urljoin(cate['url'], course_url_post)
                course = {}
                course["name"] = course_name
                course['url'] = course_url
                course['category'] = [cate['category']]
                course['category_url'] = [cate['url']]
                course_dict[course_name] = course
            else:
                if cate['category'] not in course_dict[course_name]['category']:
                    course_dict[course_name]['category'].append(cate['category'])
                    course_dict[course_name]['category_url'].append(cate['url'])
                else:
                    continue
    for course in course_dict.values():
        lst.append(course)
    print(f'********length of courses: {len(lst)}')
    return lst
