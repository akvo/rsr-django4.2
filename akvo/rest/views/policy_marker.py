# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module.
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.


from akvo.rsr.models import PolicyMarker

from ..serializers import PolicyMarkerSerializer
from ..viewsets import PublicProjectViewSet


class PolicyMarkerViewSet(PublicProjectViewSet):
    """
    """
    queryset = PolicyMarker.objects.all()
    serializer_class = PolicyMarkerSerializer
    filter_fields = ('project', 'policy_marker', )

    def get_queryset(self, related_to='project__'):
        return super(PolicyMarkerViewSet, self).get_queryset(related_to)
