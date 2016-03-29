# -*- coding: utf-8 -*-
"""Akvo RSR is covered by the GNU Affero General Public License.

See more details in the license.txt file located at the root folder of the Akvo RSR module.
For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.
"""

from akvo.rsr.models import Transaction, TransactionSector
from ..serializers import TransactionSerializer, TransactionSectorSerializer
from ..viewsets import PublicProjectViewSet


class TransactionViewSet(PublicProjectViewSet):
    """Transaction resource."""

    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_fields = (
        'project', 'reference', 'transaction_type', 'currency', 'provider_organisation',
        'receiver_organisation')


class TransactionSectorViewSet(PublicProjectViewSet):
    """Transaction sector resource."""

    queryset = TransactionSector.objects.all()
    serializer_class = TransactionSectorSerializer
    filter_fields = ('transaction__project', 'transaction', 'code')
    project_relation = 'transaction__project__'
