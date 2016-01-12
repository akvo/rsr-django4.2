# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module.
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.


from akvo.rsr.models import ProjectDocument

from ..serializers import ProjectDocumentSerializer
from ..viewsets import PublicProjectViewSet


class ProjectDocumentViewSet(PublicProjectViewSet):
    """
    """
    queryset = ProjectDocument.objects.all()
    serializer_class = ProjectDocumentSerializer
    filter_fields = ('project', )

    def get_queryset(self, related_to='project__'):
        return super(ProjectDocumentViewSet, self).get_queryset(related_to)
