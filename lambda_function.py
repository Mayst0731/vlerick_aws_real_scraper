"""Lambda handler to start scraping"""
import json
import time
from botocore.vendored import requests
import boto3
import botocore
from category import extract_categories
from course import extract_courses
from detail import extract_details
from final_arrangement import final_run
import os


def start_crawl(base_url, special_version_url):
    """Assign crawling job for getting category,course,detail information."""
    session = requests.Session()
    category_list = extract_categories(base_url, session)
    # category_list = category_list[:1]
    course_list = extract_courses(category_list, session)
    # course_list = course_list[:1]
    detail_list = extract_details(course_list, session, special_version_url)
    session.close()
    return {"category": category_list,
            "course": course_list,
            "detail": detail_list}


def write_to_s3(lst_to_write, bucket_type, folder_path, file_name):
    """Write scraped information to aws s3 bucket"""
    s3_obj = boto3.resource('s3')
    bucket_name = os.environ[bucket_type]
    file_object = s3_obj.Object(bucket_name, folder_path+file_name)
    file_object.put(Body=json.dumps(lst_to_write))


def get_base_url(event):
    """Get base url from sqs message to start scraping"""
    messages = event["Records"]
    for msg in messages:
        body = msg["body"]
        dic = json.loads(body)
        if "3399_EUR" in dic:
            base_url = dic["3399_EUR"]
        else:
            return None
    return base_url


def lambda_handler(event, context):
    """Start crawling job triggered by sqs"""
    # region = os.environ['AWS_REGION']
    # print(region)

    start_time = time.time()
    # base_url = get_base_url(event)
    # if not base_url:
    #     return
    base_url = "https://www.vlerick.com/en/programmes/management-programmes"
    special_version_url = [
        "https://www.vlerick.com/en/programmes/management-programmes/accounting-finance/essentials-in-finance",
        "https://www.vlerick.com/en/programmes/management-programmes/digital-transformation/digital-leadership",
        "https://www.vlerick.com/en/programmes/management-programmes/general-management/learn-to-speak-business",
        "https://www.vlerick.com/en/programmes/management-programmes/marketing-sales/essentials-in-marketing",
        "https://www.vlerick.com/en/programmes/management-programmes/operations-supply-chain-management/essentials-in-operations",
        "https://www.vlerick.com/en/programmes/management-programmes/people-management-leadership/essentials-in-people-skills",
        "https://www.vlerick.com/en/programmes/management-programmes/strategy/essentials-in-strategy",
        "https://www.vlerick.com/en/programmes/management-programmes/people-management-leadership/negotiate-for-success"]

    lst = start_crawl(base_url, special_version_url)
    final_lst = final_run(lst["category"], lst["detail"])
    duration = time.time() - start_time
    minutes = duration // 60
    print(f"Crawled {duration} seconds, {minutes} mins")
    categories = final_lst["categories"]
    details = final_lst["details"]
    faculties = final_lst["faculties"]

    # write_to_s3(categories,"s3_category_bucket_name","category/","category_3399_EUR_XW_0226.json")
    # write_to_s3(details, "s3_detail_bucket_name", "detail/", "detail_3399_EUR_XW_0226.json")
    # write_to_s3(faculties, "s3_faculty_bucket_name", "faculty/", "faculty_3399_EUR_XW_0226.json")
    return "Finish running vlerick scraper"


lambda_handler("","")
