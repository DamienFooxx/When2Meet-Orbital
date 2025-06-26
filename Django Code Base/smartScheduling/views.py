from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from smartScheduling.scheduling_engine import schedule_best_timeslots
from accounts.models import Profile
from smartScheduling.serializers import SchedulingInputSerializer, SchedulingOutputSerializer
from decimal import Decimal, InvalidOperation
from datetime import date, time

class SchedulingViewSet(viewsets.ViewSet):
    """
    Viewset for finding available timeslots for smart scheduling.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail = False, methods = ['post'], url_path = 'find-available-slots')
    def find_available_slots(self, request):
        input_serializer = SchedulingInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        profiles = list(Profile.objects.filter(
            unique_id__in=data['users']
        ))

        # Check if all requested users were found
        if len(profiles) != len(data['users']):
            found_user_ids = {p.unique_id for p in profiles}
            missing_user_ids = set(data['users']) - found_user_ids
            return Response(
                {'error': f'Users not found: {", ".join(missing_user_ids)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        slots = schedule_best_timeslots(
            users=profiles,
            start_date=data['start_date'],
            start_time=data['start_time'],
            end_date=data['end_date'],
            end_time=data['end_time'],
            duration=data['duration'],
            buffer=data['buffer'],
            min_attendance=data['minimum_attendance']
        )

        slots_list = [
            {
                'start_date': key[0].date(),
                'start_time': key[0].time(),
                'end_date': key[1].date(),
                'end_time': key[1].time(),
                **info,
            }
            for key, info in slots.items()
        ]

        output_serializer = SchedulingOutputSerializer(data=slots_list, many=True)
        output_serializer.is_valid(raise_exception=True)

        return Response({'available_slots': output_serializer.data}, status=status.HTTP_200_OK)
