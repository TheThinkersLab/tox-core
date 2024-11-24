import datetime
from pytz import UTC

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from rest_framework import status, exceptions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from common.djangoapps.student.models import UserProfile
from common.djangoapps.student.models.user import PendingEmailChange
from lms.djangoapps.course_api.views import CourseListView as BaseCourseListView
from openedx.core.djangoapps.user_api.accounts.api import update_account_settings
from openedx.core.djangoapps.user_api.accounts.views import UsernameReplacementView
from openedx.core.djangoapps.user_api.errors import (
    AccountValidationError,
    AccountUpdateError,
    UserNotAuthorized,
    UserNotFound,
)

from .serializers import CourseSerializer

User = get_user_model()


class CourseListAnonThrottle(AnonRateThrottle):
    """
    Limit the number of requests users can make to the course list API.
    """

    rate = "60/m"


class CourseListView(BaseCourseListView):
    """
    **Use Cases**

        Use this endpoint to get a list of all active courses.

        This endpoint will be called from the `hrms-integration` service during
            - initial connection to synchronize systems for the very first time
            - via a cron to keep up synchronization.

    **Example Requests**

        GET /tox-core/api/v1/courses/

    **Response Values**

        Body comprises a list of objects as returned by `CourseDetailView` from openedX.

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


class AccountView(UsernameReplacementView):
    """
    **Use Cases**

        Use this endpoint to update user information anonymously.

        This endpoint will be used in combination with the above endpoint for synchronizations,
        specifically, during cronjob. When the user data changes in HRMS systems, we plan to
        update the same in Open edX.

    **Example Requests**

        PUT /tox-core/api/v1/user/accounts/pk/

    **Request Values**

        * name: The fullname of the user.
        * email: The email address of the user.

        **Example Request**

            {
                "name": "Yennefer of Vengerberg",
                "email": "yennefer.vengerberg"@example.com",
            }

    **Response Values**

        {
            "message": "Account updated"
        }

    **Code Abstractions**

        - https://github.com/openedx/edx-platform/blob/73ba58ae11a9b1a896cdeeb515d1818c207f6b21/openedx/core/djangoapps/user_api/accounts/views.py#L412
        - https://github.com/openedx/edx-platform/blob/master/common/djangoapps/student/views/management.py#L867
        - https://github.com/openedx/edx-platform/blob/master/common/djangoapps/student/models/user.py#L904
        - https://github.com/openedx/edx-platform/blob/master/openedx/core/djangoapps/user_api/accounts/views.py#L1259
    """

    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get('pk', None)

        if not user_id:
            return Response({"error": "User ID not provided"}, status=status.HTTP_400_BAD_REQUEST)

        user = self.get_user_account(user_id=user_id)

        try:
            with transaction.atomic():
                update_account_settings(user, request.data)
        except UserNotAuthorized:
            return Response(status=status.HTTP_403_FORBIDDEN)
        except UserNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except AccountValidationError as err:
            return Response({"field_errors": err.field_errors}, status=status.HTTP_400_BAD_REQUEST)
        except AccountUpdateError as err:
            return Response(
                {"developer_message": err.developer_message, "user_message": err.user_message},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "email" in request.data:
            new_email = request.data["email"]
            self.confirm_email_change(user=user, new_email=new_email)
            self.replace_username(current_username=user.username, desired_username=new_email)

        return Response({"message": "Account updated"}, status=status.HTTP_200_OK)

    def get_user_account(self, user_id):  # noqa
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise exceptions.ValidationError(detail={"pk": f"{user_id} is not a valid user."})

    def confirm_email_change(self, user: User, new_email: str):  # noqa
        if User.objects.filter(email=new_email).exists():
            raise exceptions.ValidationError(detail={"error": "Email address already in use"})

        u_prof = UserProfile.objects.get(user=user)
        meta = u_prof.get_meta()
        if 'old_emails' not in meta:
            meta['old_emails'] = []
        meta['old_emails'].append([user.email, datetime.datetime.now(UTC).isoformat()])
        u_prof.set_meta(meta)
        u_prof.save()

        user.email = new_email
        user.save()

        try:
            pec = PendingEmailChange.objects.get(user=user)
        except PendingEmailChange.DoesNotExist:
            pec = None

        if pec:
            pec.delete()

    def replace_username(self, current_username, desired_username):  # noqa
        # (model_name, column_name)
        MODELS_WITH_USERNAME = (
            ("auth.user", "username"),
            ("consent.DataSharingConsent", "username"),
            ("consent.HistoricalDataSharingConsent", "username"),
            ("credit.CreditEligibility", "username"),
            ("credit.CreditRequest", "username"),
            ("credit.CreditRequirementStatus", "username"),
            ("user_api.UserRetirementPartnerReportingStatus", "original_username"),
            ("user_api.UserRetirementStatus", "original_username"),
        )
        UNIQUE_SUFFIX_LENGTH = getattr(settings, "SOCIAL_AUTH_UUID_LENGTH", 4)

        replacement_locations = self._load_models(MODELS_WITH_USERNAME)

        new_username = self._generate_unique_username(desired_username, suffix_length=UNIQUE_SUFFIX_LENGTH)
        successfully_replaced = self._replace_username_for_all_models(
            current_username, new_username, replacement_locations
        )

        if not successfully_replaced:
            raise exceptions.ValidationError(detail={"error": "Username already in use"})
