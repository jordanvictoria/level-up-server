"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Gamer, Game
from rest_framework.decorators import action
from django.db.models import Count
from django.db.models import Q
from django.core.exceptions import ValidationError


class EventView(ViewSet):
    """Level up game types view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single game type

        Returns:
            Response -- JSON serialized game type
        """

        #   tried to annotate onto one resource, failed
        #  events = Event.objects.annotate(attendees_count=Count('attendees'))

        event = Event.objects.get(pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)


    def list(self, request):
        """Handle GET requests to get all game types

        Returns:
            Response -- JSON serialized list of game types
        """

        events = Event.objects.all()

        # events = Event.objects.annotate(attendees_count=Count('attendees'))

        if "game" in request.query_params:
            game_id = request.query_params['game']
            events = events.filter(game=game_id)

        # Find a particular gamer
        # gamer = Gamer.objects.get(id=1)

        # Event.objects.filter(
        #     Q(organizer=gamer) &
        #     Q(game__gamer=gamer)
        # )

        gamer = Gamer.objects.get(user=request.auth.user)

        events = Event.objects.annotate(
            attendees_count=Count('attendees'),
            joined=Count(
                'attendees',
                filter=Q(attendees=gamer)
            )
        )

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Handle POST operations

        Returns
            Response -- JSON serialized game instance
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        # game = Game.objects.get(pk=request.data["game"])
        # serializer.save(game=game)

        serializer = CreateEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(gamer=gamer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        """Handle PUT requests for an event

        Returns:
            Response -- Empty body with 204 status code
        """

        event = Event.objects.get(pk=pk)
        event.description = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]

        event_game = Game.objects.get(pk=request.data["game"])
        event.game = event_game
        event.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk):
        """Handle PUT requests for an event"""
        event = Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""
    
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
        event.attendees.add(gamer)
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)

    @action(methods=['delete'], detail=True)
    def leave(self, request, pk):
        """Delete request for a user to sign up for an event"""
    
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
        event.attendees.remove(gamer)
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    

        


class EventOrganizerSerializer(serializers.ModelSerializer):
    """JSON serializer for organizer"""
    class Meta:
        model = Gamer
        fields = ('id', 'bio', 'full_name')

class EventAttendeeSerializer(serializers.ModelSerializer):
    """JSON serializer for attendees"""
    class Meta:
        model = Gamer
        fields = ('id', 'bio', 'full_name')

class EventGameSerializer(serializers.ModelSerializer):
    """JSON serializer for games"""
    class Meta:
        model = Game
        fields = ('id', 'title', 'maker', 'number_of_players', 'skill_level', 'type', 'creator')


class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for game types
    """
    attendees_count = serializers.IntegerField(default=None)
    organizer = EventOrganizerSerializer(many=False)
    attendees = EventAttendeeSerializer(many=True)
    game = EventGameSerializer(many=False)

    class Meta:
        model = Event
        fields = ('id', 'description', 'date', 'time', 'game', 'organizer', 'attendees', 'joined', 'attendees_count')
        depth = 2

class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'description', 'date', 'time', 'game']
