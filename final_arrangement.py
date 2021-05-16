"""The final process of formatting details for meeting import requirements"""


def arrange_detail(details):
    """Make up details"""
    new_details = []
    for detail in details:
        detail["category"] = modify_category(detail["category"])
        for version_info in detail["version_info"]:
            overview_info = detail["overview_info"]
            new_detail = {**detail, **version_info, **overview_info}
            del new_detail["version_info"]
            del new_detail["overview_info"]
            new_detail["desc"] = new_detail.pop("overview")
            overview = {'desc': new_detail["desc"],
                        'video_title': new_detail["video_title"],
                        'video_url': new_detail["video_url"]}
            new_detail["overview"] = overview
            schedule = [["", "", "", "formal"]]
            schedule[0][0] = new_detail["effective_date_start"]
            schedule[0][1] = new_detail["effective_date_end"]
            schedule[0][2] = get_duration_number(detail)
            new_detail["schedule"] = schedule
            new_detail["active"] = True
            new_detail["category_tags"] = []
            new_detail["priority"] = 0
            new_detail["publish"] = 100
            new_detail["Repeatable"] = "Y"
            new_detail["duration_consecutive"] = True
            if "tuition" in new_detail:
                new_detail["tuition_number"] = new_detail.pop("tuition")
            else:
                new_detail["tuition_number"] = 0
            new_details.append(new_detail)
    for detail in new_details:
        detail["university_school"] = '3399_EUR'
        detail["version"] = detail.pop('versions')
    check_attrs(new_details)
    return new_details


def modify_category(category_list):
    """modify category prefix"""
    modified_categories = []
    for cate in category_list:
        if "Management Domains" in cate:
            new_cate = cate.replace("Management Domains", "Management Programmes")
            modified_categories.append(new_cate)
    return modified_categories


def check_attrs(details):
    """Test missing attrs and patch up below"""
    detail_attrs = {'name': '',
                    'url': '',
                    'university_school': '',
                    'category': '',
                    'desc': '',
                    'active': '',
                    'type': '',
                    'category_tags': '',
                    'priority': 0,
                    'publish': 100,
                    'version': '',
                    'location': '',
                    'currency': '',
                    'tuition_number': '',
                    'tuition_note': '',
                    'Repeatable': 'Y',
                    'effective_date_start': '',
                    'effective_date_end': '',
                    'duration_consecutive': '',
                    'languages': '',
                    'credential': '',
                    'course_takeaways': '',
                    'course_faculties': [],
                    'who_attend_desc': '',
                    'overview': '',
                    'testimonials': [],
                    'exec_ed_inquiry_cc_emails': '',
                    'schedule': [],
                    'is_advanced_management_program': '',
                    'who_attend_params': '{"working experience": "","background knowledge":""}'
                    }

    for detail in details:
        if "location" not in detail:
            detail["type"] = 'Onsite'
        else:
            detail["type"] = define_course_type(detail)
        if "location" not in detail:
            detail["location"] = "Brussels, ----, Belgium"
        else:
            detail["location"] = location_map(detail["location"])
        if 'credential' not in detail:
            detail['credential'] = ''
        if 'who_attend_desc' not in detail:
            detail['who_attend_desc'] = ''
        if 'is_advanced_management_program' not in detail:
            detail['is_advanced_management_program'] = False
        if 'who_attend_params' not in detail:
            detail['who_attend_params'] = detail_attrs['who_attend_params']
        if 'exec_ed_inquiry_cc_emails' not in detail:
            detail['exec_ed_inquiry_cc_emails'] = ''

        for k in detail_attrs:
            if k not in detail:
                print(f"{detail['url']} do not have {k}")
    return details


def get_duration_number(detail):
    """Map the duration number"""
    num = ''
    if 'duration_days' in detail:
        num = str(detail['duration_days'])
    elif 'duration_weeks' in detail:
        num = str(detail['duration_weeks'])
    elif 'duration_months' in detail:
        num = str(detail['duration_months'])
    return num


def define_course_type(detail):
    """Define course type"""
    c_type = ''
    onsite_locations = ["Brussels", "Ghent", "Leuven", "Btech Deinze"]
    if detail["version"] == 1:
        locations = ' '.join(map(str,detail['location']))
        for loc in onsite_locations:
            if 'Hybrid' in locations:
                c_type = 'Blended-Onsite&Virtual'
            elif loc in locations and "Online" in locations:
                c_type = 'Blended-Onsite&Virtual'
            elif loc in locations:
                c_type = 'Onsite'
            elif "Online" in locations:
                c_type = 'Online-Virtual'
    elif detail["version"] == 2:
        locations = ' '.join(map(str,detail['location']))
        for loc in onsite_locations:
            if loc in locations:
                c_type = 'Onsite'
            elif "Online" in locations:
                c_type = 'Online-Virtual'
    return c_type


def location_map(original_loc):
    """map the scraped location string to importable location string"""
    if len(original_loc) == 0:
        main_campus = "Brussels, ----, Belgium"
        return [main_campus]
    location_dict = {"Brussels": "Brussels, ----, Belgium",
                     "Ghent": "Ghen, ----, Belgium",
                     "Leuven": "Leuven, ----, Belgium",
                     'Online': "Brussels, ----, Belgium",
                     "Deinze": "Deinze, ----, Belgium",
                     'Hybrid': "Brussels, ----, Belgium",
                     "Gent": "Gent, ----, Belgium",
                     "Brussel": "Brussel, ----, Belgium"}
    locations = ' '.join(map(str,original_loc))
    new_loc_set = set()
    for loc in location_dict:
        if loc in locations:
            new_loc_set.add(location_dict[loc])
    new_loc = list(new_loc_set)
    return new_loc


def filter_out_faculties(details):
    """filter out faculty list for the final faculty.json file"""
    name_set = set()
    fac_list = []
    for detail in details:
        new_fac_for_single_detail = []
        faculties = detail["course_faculties"]
        if len(faculties) > 0:
            for fac in faculties:
                name_set.add(fac["name"])
                fac_list.append(fac)
                new_fac_for_single_detail.append(fac["name"])
            detail["course_faculties"] = new_fac_for_single_detail
    return fac_list


def delete_repeating_cates(cates):
    """Delete redundant categories"""
    cate_set = set()
    cate_list = list()
    for cate in cates:
        if "Management Domains" in cate["category"]:
            cate["category"] = cate["category"].replace("Management Domains", 'Management Programmes')
        if cate["category"] not in cate_set:
            cate_set.add(cate["category"])
            cate_list.append(cate)
        else:
            print(cate["category"])
    return cate_list


def final_run(categories, details):
    """The function to run all the final modifications and get the valid lists for the sake storing to s3"""
    final_details = arrange_detail(details)

    final_faculties = filter_out_faculties(final_details)

    final_details = check_attrs(final_details)

    final_categories = delete_repeating_cates(categories)
    return {"categories": final_categories,
            "details": final_details,
            "faculties": final_faculties}
