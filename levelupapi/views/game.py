"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Game, Gamer, GameType
from django.db.models import Count
from django.db.models import Q
from django.core.exceptions import ValidationError



class GameView(ViewSet):
    """Level up game types view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single games

        Returns:
            Response -- JSON serialized games
        """

        try:
            game = Game.objects.get(pk=pk)
            serializer = GameSerializer(game)
            return Response(serializer.data)

        except Game.DoesNotExist as ex:
            return Response(status=status.HTTP_404_NOT_FOUND)


    def list(self, request):
        """Handle GET requests to get all games

        Returns:
            Response -- JSON serialized list of games
        """

        games = Game.objects.all()
        # games = Game.objects.annotate(event_count=Count('events'))

        gamer = Gamer.objects.get(user=request.auth.user)

        games = Game.objects.annotate(
            event_count=Count('events'),
            user_event_count=Count(
                'events',
                filter=Q(creator=gamer)
            )
        )




        # Q examples
        # game_type = request.query_params.get('type', None)
        # if game_type is not None:
        #     games = games.filter(type=game_type)


        # search = self.request.query_params.get('search', None)
        # Game.objects.filter(
        #     Q(title__startswith=search) |
        #     Q(maker__startswith=search)
        # )





        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    def create(self, request):
        """Handle POST operations

        Returns
            Response -- JSON serialized game instance
        """
        # game_type = GameType.objects.get(pk=request.data["type"])
        # serializer.save(type=game_type)
        gamer = Gamer.objects.get(user=request.auth.user)
        serializer = CreateGameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(creator=gamer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        """Handle PUT requests for a game

        Returns:
            Response -- Empty body with 204 status code
        """

        game = Game.objects.get(pk=pk)
        game.title = request.data["title"]
        game.maker = request.data["maker"]
        game.number_of_players = request.data["number_of_players"]
        game.skill_level = request.data["skill_level"]

        game_type = GameType.objects.get(pk=request.data["type"])
        game.type = game_type
        game.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk):
        """Handle PUT requests for an event"""
        
        game = Game.objects.get(pk=pk)
        game.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)



class GameSerializer(serializers.ModelSerializer):
    event_count = serializers.IntegerField(default=None)
    user_event_count = serializers.IntegerField(default=None)
    """JSON serializer for games
    """


    class Meta:
        model = Game
        fields = ('id', 'title', 'maker', 'number_of_players', 'skill_level', 'type', 'creator', 'event_count', 'user_event_count')
        depth = 1

class CreateGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'maker', 'number_of_players', 'skill_level', 'type']