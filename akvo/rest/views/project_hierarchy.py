# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module.
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

from akvo.rsr.models import ProjectHierarchy, Project
from ..serializers import ProjectHierarchySerializer, ProjectUpdateSerializer
from ..viewsets import PublicProjectViewSet
from ..pagination import StandardSizePageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response


class RawProjectHierarchyViewSet(PublicProjectViewSet):
    queryset = ProjectHierarchy.objects.all()
    serializer_class = ProjectHierarchySerializer
    project_relation = 'root_project__'


@api_view(['GET'])
def program_countries(request, program_pk):
    program = get_object_or_404(ProjectHierarchy, root_project=program_pk)
    root = program.root_project
    descendant_ids = root.descendants().values_list('id', flat=True)
    queryset = Project.objects\
        .prefetch_related('primary_location__country')\
        .filter(id__in=descendant_ids)\
        .exclude(primary_location__country__isnull=True)\
        .values_list('primary_location__country__iso_code', flat=True)\
        .distinct()
    country_codes = set(queryset)
    return Response(sorted({code.upper() for code in country_codes if code}))


@api_view(['GET'])
def program_updates(request, program_pk):
    program = get_object_or_404(ProjectHierarchy, root_project=program_pk)
    queryset = program.descendants.published().all_updates()
    paginator = StandardSizePageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    if page is not None:
        serializer = ProjectUpdateSerializer(page, many=True, context=dict(request=request))
        return paginator.get_paginated_response(serializer.data)
    serializer = ProjectUpdateSerializer(queryset, many=True, context=dict(request=request))
    return Response(serializer.data)
