"""
Course API Serializers.  Representing course catalog data
"""


from rest_framework import serializers


class CourseSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """
    Serializer for Course objects providing minimal data about the course.
    Compare this with CourseDetailSerializer.
    """

    id = serializers.CharField()  # pylint: disable=invalid-name
    name = serializers.CharField(source='display_name_with_default_escaped')
    short_description = serializers.CharField()
