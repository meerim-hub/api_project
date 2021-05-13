from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import  action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets, status, filters
from rest_framework.viewsets import ModelViewSet

from .models import *
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, CommentSerializer
from .permissions import *


class CommentPermissionMixin:
    def get_permissions(self):
        if self.action == 'create':
            permissions = [IsAuthenticated,]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsCommentAuthor, IsAuthenticated]
        else:
            permissions = []
        return [permission() for permission in permissions]


class PermissionMixin:
    def get_permissions(self):
        if self.action == 'create':
            permissions = [IsAuthenticated,]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsProductAuthor, IsAuthenticated]
        else:
            permissions = []
        return [permission() for permission in permissions]


class CommentViewSet(CommentPermissionMixin, ModelViewSet, ):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer




class ProductImageView(generics.ListCreateAPIView, PermissionMixin):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'request': self.request}


class LikeView(APIView):
    def get(self, request, format=None, pk=None):
        post = Product.objects.get(pk=pk)
        user = self.request.user
        if user.is_authenticated:
            if user in post.likes.all():
                like = False
                post.likes.remove(user)
            else:
                like = True
                post.likes.add(user)
        data = {
            'like': like
        }
        return Response(data)


class ProductsViewSet(viewsets.ModelViewSet, PermissionMixin):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



    def get_serializer_context(self):
        return {'request': self.request}

    def get_permissions(self):
        print(self.action)
        if self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsProductAuthor, ]
        else:
            permissions = []
        return [permission() for permission in permissions]

    @action(detail=False, methods=['get'])
    def search(self, request, pk=None):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(description__icontains=q))

        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def sort(self, request):
        filter = request.query_params.get('filter')
        if filter == 'A-Z':
            queryset = self.get_queryset().order_by('title')
        elif filter == 'Z-A':
            queryset = self.get_queryset().order_by('-title')
        elif filter == 'replies':
            maximum = 0
            for problem in self.get_queryset():

                if maximum < problem.replies.count():
                    maximum = problem.replies.count()
                    queryset = self.get_queryset().filter(id=problem.id)
        else:
            queryset = self.get_queryset()

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny, ]
