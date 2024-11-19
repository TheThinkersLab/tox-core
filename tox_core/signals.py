import requests

from django.conf import settings
from django.dispatch import receiver

from openedx_events.learning.signals import CERTIFICATE_CREATED


@receiver(CERTIFICATE_CREATED)
def handle_certificate_created_event(sender, **kwargs):
    event_type = kwargs['metadata'].event_type
    user_id = kwargs['certificate'].user.id
    course_id = str(kwargs['certificate'].course.course_key)

    if event_type != "org.openedx.learning.certificate.created.v1":
        return

    url = f"{settings.TOX_CORE_API_BASE_URL}/api/hrms/bamboo/v1/training/record-completion"
    payload = {
        "user_id": user_id,
        "course_id": course_id
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    requests.post(url, json=payload, headers=headers)

    return
