from django.http import HttpResponse
from django.template import loader
from app.models import Courses
from rest_framework.views import APIView
from rest_framework.response import Response
from .downloader import DelosDownloader
from rest_framework import status
import logging

logger = logging.getLogger('django')


def index(request):
    mycourses = Courses.objects.all().values()
    template = loader.get_template('index.html')
    context = {
        'mycourses': mycourses,
    }
    return HttpResponse(template.render(context, request))


class ApiView(APIView):

    def get(self, request, *args, **kwargs):
        logger.info("Endpoint for course downloading was hit")
        rid = request.GET.get('rid')
        name = request.GET.get('name')
        dd = DelosDownloader(rid, name)
        return Response(dd.response, status=dd.statusCode)
