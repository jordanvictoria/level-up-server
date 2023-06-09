"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Gamer, Game
from rest_framework.decorators import action


class EventView(ViewSet):
    """Level up game types view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single game type

        Returns:
            Response -- JSON serialized game type
        """

        event = Event.objects.get(pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)


    def list(self, request):
        """Handle GET requests to get all game types

        Returns:
            Response -- JSON serialized list of game types
        """

        events = Event.objects.all()
        

        if "game" in request.query_params:
            game_id = request.query_params['game']
            events = events.filter(game=game_id)

        # Set the `joined` property on every event
        for event in events:
            # Check to see if the gamer is in the attendees list on the event
            gamer = Gamer.objects.get(user=request.auth.user)
            event.joined = gamer in event.attendees.all()

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Handle POST operations

        Returns
            Response -- JSON serialized game instance
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        game = Game.objects.get(pk=request.data["game"])

        event = Event.objects.create(
            description=request.data["description"],
            date=request.data["date"],
            time=request.data["time"],
            game=game,
            organizer=gamer
        )
        serializer = EventSerializer(event)
        return Response(serializer.data)

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
    organizer = EventOrganizerSerializer(many=False)
    attendees = EventAttendeeSerializer(many=True)
    game = EventGameSerializer(many=False)

    class Meta:
        model = Event
        fields = ('id', 'description', 'date', 'time', 'game', 'organizer', 'attendees', 'joined')
        depth = 1