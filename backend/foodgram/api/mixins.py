from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.viewsets import GenericViewSet


class ListRetrieveMixin(GenericViewSet, RetrieveModelMixin, ListModelMixin):
    """Миксин для получения отдельного обьекта"""
    # search_fields = ('name',)
    pass


class ListCreateRetrieveUpdateDeleteMixin(GenericViewSet, CreateModelMixin,
                                          ListModelMixin, UpdateModelMixin,
                                          DestroyModelMixin,
                                          RetrieveModelMixin):
    """Миксин для получения объекта, списка, создания, обновления и удаления"""
    pass
