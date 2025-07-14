from rest_framework import serializers


class AllFieldsNotRequiredSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):  # noqa
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, serializers.CharField):
                field.allow_blank = True
            field.required = False
