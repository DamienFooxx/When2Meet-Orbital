from rest_framework import serializers
from decimal import Decimal

# Custom validator for multiples of 15
def multiple_of_15(value):
    if value % 15 != 0:
        raise serializers.ValidationError('This value must be a multiple of 15.')

class SchedulingInputSerializer(serializers.Serializer):
    group_id = serializers.CharField(required=False)
    users = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        allow_empty=False
    )
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)
    duration = serializers.IntegerField(required=True, validators=[multiple_of_15])
    type_of_meetup = serializers.ChoiceField(choices=['virtual', 'physical'], default='virtual')
    buffer = serializers.IntegerField(required=False, validators=[multiple_of_15])
    minimum_attendance = serializers.DecimalField(
        max_digits=5, decimal_places=2, min_value=Decimal('0.00'), max_value=Decimal('100.00'), default=Decimal('50.00')
    )

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be a positive integer.")
        return value

    def validate_buffer(self, value):
        if value < 0:
            raise serializers.ValidationError("Buffer must be a non-negative integer.")
        return value

    def validate(self, data):
        """
        Set default buffer based on type_of_meetup if not provided.
        """
        if 'buffer' not in data:
            if data.get('type_of_meetup') == 'virtual':
                data['buffer'] = 15
            else:
                data['buffer'] = 30
        return data


class SchedulingOutputSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    start_time = serializers.TimeField()
    end_date = serializers.DateField()
    end_time = serializers.TimeField()
    free_count = serializers.IntegerField()
    group_size = serializers.IntegerField()
    attendance = serializers.FloatField()