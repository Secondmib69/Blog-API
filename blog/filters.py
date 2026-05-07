from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class RoleFilter(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset = None):
        if view.request.user.is_staff :
            return view.StaffFilterSet
        
        

class RoleSearchFilter(SearchFilter):
    def get_search_fields(self, view, request):
        fields = ['username', 'first_name', 'last_name', 'job_title']
        if request.user.is_staff:
            fields.extend(['email', 'phone'])
        return fields
