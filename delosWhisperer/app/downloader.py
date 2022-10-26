import requests
import re
import urllib.request
import progressbar
import os
import logging
from rest_framework import status

logger = logging.getLogger('django')


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class DelosDownloaderProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar = progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


def find_between(string, first, last):
    try:
        start = string.index(first) + len(first)
        end = string.index(last, start)
        return string[start:end]
    except ValueError:
        return ""


class DelosDownloader():

    def __init__(self, courseRid, courseName):
        logger.info('Will download course: ' + courseName)
        self.dir = os.path.expanduser('~') + "/Videos/"
        self.errors = []
        self.courseIds = dict()
        self.courses = dict()
        self.inputIds = set()
        self.cookie = None
        self.getValidCookie()
        self.downloadCourseByRid(courseRid, courseName)
        self.nLectures = 0
        self.response = None
        self.statusCode = None
        if not self.errors:
            logger.info(Colors.GREEN + "No errors occured while downloading. Operation was successful." + Colors.RESET)
            self.response = "Successfuly downloaded " + str(self.nLectures) + " lectures of the: " + courseName + " courses."
            self.statusCode = status.HTTP_200_OK
        else:
            logger.info(Colors.FAIL + "Errors occured while downloading the following files: \n")
            self.response = "ERROR(s): "
            for error in self.errors:
                logger.info(error)
                self.response += error + ", "
            self.statusCode = status.HTTP_500_INTERNAL_SERVER_ERROR


    def getValidCookie(self):
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
        self.cookie = find_between(response.headers.get('Set-Cookie'), "JSESSIONID=", ";")
        logger.info(self.cookie)


    def chooseCoursesToDownload(self):
        cookies = {
            'JSESSIONID': self.cookie,
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
        logger.info(r.status_code)

        response = r.content.decode("utf-8")
        filtered = response.split("<div class=\"Search-Filters-Title\">Υπεύθυνος</div>")[0]
        refiltered = filtered.split("<a")

        i = 0
        for line in refiltered:
            if i > 0:
                subline = line.replace("\n", "").replace("\t", "")
                courseName = find_between(subline, "\"> ", "<small>")
                courseRid = find_between(subline, "&crs=", "\">")
                self.courseIds[str(i)] = courseName
                self.courses[courseName] = courseRid
            i += 1

        for courseId, courseName in self.courseIds.items():
            logger.info(
                Colors.BOLD + "courseId: " + Colors.RESET + courseId + Colors.BOLD + "  Course: " + Colors.RESET + courseName + Colors.BOLD + " RID: " + Colors.RESET +
                self.courses[courseName])

        logger.info("Please type the id(s) of the course(s) you are interested to download.")

        validInput = True
        while validInput:
            validInput = set(map(str, input().split()))
            self.inputIds.update(validInput)

        logger.info("The courses you chose are the following:")
        for inputId in self.inputIds:
            logger.info(inputId + " : " + self.courseIds[inputId])
        logger.info("\n")


    def downloadCourseByRid(self, courseRid, courseName):
        logger.info(
            Colors.BLUE + "Attempting to download lectures from " + Colors.BLUE + courseName + Colors.RESET + Colors.BLUE + " course. (" + courseRid + ")" + Colors.RESET)

        cookies = {
            'JSESSIONID': self.cookie,
        }
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://delos.uoa.gr/opendelos/search?dp=di',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Sec-GPC': '1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        }
        params = {
            'dp': 'di',
            'crs': courseRid,
        }
        r = requests.get('https://delos.uoa.gr/opendelos/search', params=params, cookies=cookies, headers=headers)

        response = r.content.decode("utf-8")
        filtered = response.split("<!-- RESULT LIST -->", 1)[1]
        refiltered = filtered.split("<div class=\"col-md-12\">")

        links = {}
        i = 0
        for line in refiltered:
            if i > 0:
                subline = line.replace("\n", "").replace("\t", "")
                lectureName = find_between(subline, "&nbsp;", ") </strong>")
                filename = re.sub('[^0-9a-zA-Zά-ώΑ-ΩΆ-Ώ]+', '_', lectureName) + ".mp4"
                parentDirectory = re.split('(\d+)', filename)[0][:-1] + "/"
                lectureRid = find_between(subline, "href=\"/opendelos/player?rid=", "\"><span")
                links[
                    filename] = "https://delos-media.uoa.gr:443/delosrc/resources/vl/" + lectureRid + "/" + lectureRid + ".mp4"
            i += 1

        lines = filtered.splitlines()

        logger.info("Will download the following lectures:")
        for x in links.keys():
            logger.info(x)

        path = self.dir + parentDirectory
        if not os.path.isdir(path):
            os.mkdir(path)
            logger.info(Colors.WARNING + "Directory " + path + " was created" + Colors.RESET)

        for filename, url in links.items():
            completeFilename = path + filename
            if not os.path.exists(completeFilename):
                try:
                    logger.info(
                        Colors.WARNING + "Attempting to download from: " + Colors.BLUE + url + Colors.WARNING + " into: " + Colors.BLUE + completeFilename + Colors.RESET)
                    local_filename, headers = urllib.request.urlretrieve(url, completeFilename,
                                                                         DelosDownloaderProgressBar())
                    logger.info(Colors.GREEN + "Successfully downloaded " + filename + Colors.RESET + "\n")
                    self.nLectures += 1
                except Exception as e:
                    logger.info(
                        Colors.FAIL + "Exception " + e.__class__ + " occured while downloading " + filename + ".\n" + Colors.RESET)
                    if os.path.exists(completeFilename):
                        os.remove(completeFilename)
                    self.errors.append(filename)
            else:
                logger.info(Colors.GREEN + completeFilename + " file already exists." + Colors.RESET + "\n")
