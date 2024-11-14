from rest_framework.throttling import AnonRateThrottle

from lms.djangoapps.course_api.views import CourseListView as BaseCourseListView

from .serializers import CourseSerializer


class CourseListAnonThrottle(AnonRateThrottle):
    """
    Limit the number of requests users can make to the course list id API.
    """

    rate = "60/m"


class CourseListView(BaseCourseListView):
    """
    **Use Cases**

        Request information on all active courses.

    **Example Requests**

        GET /tox-core/api/v1/courses/

    **Response Values**

        Body comprises a list of objects as returned by `CourseDetailView`.

    **Parameters**

        active_only (optional):
            If this boolean is specified, only the courses that have not ended or do not have any end
            date are returned. This is different from search_term because this filtering is done on
            CourseOverview and not ElasticSearch.

    **Returns**

        * 200 on success, with a list of course discovery objects as returned
          by `CourseDetailView`.

        Example response:

            [
              {
                "id": "edX/example/2012_Fall",
                "name": "Example Course",
                "short_description": "An example course.",
              }
            ]
    """

    pagination_class = None
    serializer_class = CourseSerializer
    throttle_classes = (CourseListAnonThrottle,)
