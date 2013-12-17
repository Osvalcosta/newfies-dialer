# -*- coding: utf-8 -*-
#
# Newfies-Dialer License
# http://www.newfies-dialer.org
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2011-2013 Star2Billing S.L.
#
# The Initial Developer of the Original Code is
# Arezqui Belaid <info@star2billing.com>
#

from rest_framework import viewsets
from apirest.event_serializers import EventSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from appointment.models.events import Event
from appointment.function_def import get_calendar_user_id_list
import ast


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows event to be viewed or edited.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    authentication = (BasicAuthentication, SessionAuthentication)
    permissions = (IsAuthenticatedOrReadOnly, )

    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Event.objects.all()
        else:
            calendar_user_list = get_calendar_user_id_list(self.request.user)
            queryset = Event.objects.filter(creator_id__in=calendar_user_list)
        return queryset

    @action(methods=['PATCH'])
    def updat_event_status(self, request, pk=None):
        """it will update last child event status"""        
        event = self.get_object()

        if self.request.user.is_superuser:
            queryset = Event.objects.filter(parent_event=event)
        else:
            calendar_user_list = get_calendar_user_id_list(self.request.user)
            queryset = Event.objects.filter(parent_event=event, creator_id__in=calendar_user_list)

        
        event.status = request.DATA['status']
        event.save()        
        #return Response(serializer.errors,
        #                status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': 'event status has been updated'})

    @action(methods=['GET'])
    def get_list_child(self, request, pk=None):
        """it will get all child events"""        
        event = self.get_object()        
        if self.request.user.is_superuser:
            queryset = Event.objects.filter(parent_event=event)
        else:
            calendar_user_list = get_calendar_user_id_list(self.request.user)
            queryset = Event.objects.filter(parent_event=event, creator_id__in=calendar_user_list)        

        list_data = []        
        for child_event in queryset:            
            event_url =  'http://%s/rest-api/event/%s/' % (self.request.META['HTTP_HOST'], str(child_event.id))            
            data = {
                'url': event_url,
                'title': child_event.title, 
                'description': child_event.description,
                'start': str(child_event.start),
                'end': str(child_event.end),                                        
            }
            list_data.append(data)

        temp_data = ", ".join(str(e) for e in list_data)
        
        final_data = ast.literal_eval(temp_data)        
        return Response(final_data)
                