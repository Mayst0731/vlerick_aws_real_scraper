"""Scrape course details: takes in course list information. returns all details of each course"""
from detail.overview_details import get_overview_info
from detail.faculty_rules import get_faculty_info, get_faculty_info_way2
from detail.testimonial_rules import get_testimonial_info
from detail.version_rules import get_version_info, get_version_info_way2

from download_parse import download_page


def extract_details(course_list, session, special_version_url):
    """Scrape detail list

            Parameters:
                course_list(list): course list contains each course's url
                session(object): A reusable TCP connection
            Returns:
                lst (list): A list contains a course's all the information needed to be formatted at the end
    """
    comprehensive_detail = []
    for course in course_list:
        info = {}
        course_page_obj = download_page(course['url'], session)
        if course["url"] in special_version_url:
            faculty_info = get_faculty_info_way2(course, course_page_obj, session)
        else:
            faculty_info = get_faculty_info(course, course_page_obj, session)
        info['course_faculties'] = faculty_info
        testimonial_info = get_testimonial_info(course, course_page_obj, session)
        info["testimonials"] = testimonial_info
        if course["url"] in special_version_url:
            version_info = get_version_info_way2(course_page_obj)
        else:
            version_info = get_version_info(course, course_page_obj, session)
        info["version_info"] = version_info
        overview_info = get_overview_info(course, course_page_obj, session)
        info["overview_info"] = overview_info
        new_course = {**course, **info}
        comprehensive_detail.append(new_course)
    return comprehensive_detail
