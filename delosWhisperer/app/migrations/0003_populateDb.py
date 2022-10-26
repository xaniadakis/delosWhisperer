from django.db import migrations, models
import requests
from app.models import Courses


def find_between(string, first, last):
    try:
        start = string.index(first) + len(first)
        end = string.index(last, start)
        return string[start:end]
    except ValueError:
        return ""


def getValidCookie():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    }
    params = {
        'dp': 'di'
    }
    response = requests.get('https://delos.uoa.gr/opendelos/search', params=params, headers=headers)
    cookie = find_between(response.headers.get('Set-Cookie'), "JSESSIONID=", ";")
    return cookie


def persistCourses():
    cookies = {
        'JSESSIONID': getValidCookie(),
    }
    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        'Referer': 'https://delos.uoa.gr/opendelos/search?dp=di',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    r = requests.get('https://delos.uoa.gr/opendelos/report.html', cookies=cookies, headers=headers)
    # print(r.status_code)
    response = r.content.decode("utf-8")
    filtered = response.split("<div class=\"Search-Filters-Title\">Υπεύθυνος</div>")[0]
    refiltered = filtered.split("<a")
    i = 0
    courseIds = dict()
    courses = dict()
    for line in refiltered:
        if i > 0:
            subline = line.replace("\n", "").replace("\t", "")
            courseName = find_between(subline, "\"> ", "<small>")
            courseRid = find_between(subline, "&crs=", "\">")
            courseIds[str(i)] = courseName
            courses[courseName] = courseRid
        i += 1
    for courseId, courseName in courseIds.items():
        course = Courses.objects.create(fid=courseId, name=courseName, code=courses[courseName])
        course.save()
        # print("courseId: " + courseId + "  Course: " + courseName + " RID: " + courses[courseName])


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0001_initial'),
        ('app', '0002_courses_delete_course'),
    ]

    Courses.objects.all().delete()
    persistCourses()
    Courses.objects.all()
