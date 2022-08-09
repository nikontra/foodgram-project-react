from api.serializers import FollowSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    http_method_names = ('get', 'post', 'delete',)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=self.request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = self.request.user
        follow = Follow.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Вы не можете подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif follow:
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(
                user=user, author=author
            )
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not follow:
            return Response(
                {'errors': 'Вы не подписаны на данного автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
