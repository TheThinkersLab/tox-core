import pytz
from datetime import datetime

from django.db.models import Q

from rest_framework.generics import ListAPIView
from rest_framework.throttling import AnonRateThrottle

from lms.djangoapps.course_api.serializers import CourseKeySerializer
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class CourseIdListAnonThrottle(AnonRateThrottle):
    """
    Limit the number of requests users can make to the course list id API.
    """
    rate = "60/m"


class CourseIdListView(ListAPIView):
    """
    **Use Cases**

        Request a list of course IDs for all active courses.

    **Example Requests**

        GET /tox-core/api/v1/course-ids/

    **Response Values**

        Body comprises a list of course ids for all active courses.

    **Returns**

        * 200 on success, with a list of course ids for all active courses.

        Example response:

        [
            "course-v1:edX+DemoX+Demo_Course"
        ]
    """
    serializer_class = CourseKeySerializer
    throttle_classes = (CourseIdListAnonThrottle,)
    pagination_class = None

    def get_queryset(self):
        """
        The below code is a combination of code snippets abstracted from the below links:

        https://github.com/openedx/edx-platform/blob/master/openedx/core/djangoapps/content/course_overviews/models.py#L743
        https://github.com/openedx/edx-platform/blob/open-release/redwood.3/openedx/core/djangoapps/content/course_overviews/models.py#L697
        """
        return (
            CourseOverview.objects
            .filter(Q(end__isnull=True) | Q(end__gte=datetime.now().replace(tzinfo=pytz.UTC)))
            .values_list('id', flat=True)
        )
