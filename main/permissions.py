from rest_framework.permissions import BasePermission


class IsProductAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool (request.user.is_authenticated and str(obj.user).lower() == str(request.user.email).lower())



class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool (request.user.is_authenticated)
