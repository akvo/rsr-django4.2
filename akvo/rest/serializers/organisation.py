# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module.
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

import logging

from rest_framework import serializers

from akvo.rsr.models import Organisation

from ..fields import Base64ImageField

from .organisation_budget import (OrganisationCountryBudgetSerializer,
                                  OrganisationTotalBudgetSerializer,
                                  OrganisationRecipientOrgBudgetSerializer,
                                  OrganisationRegionBudgetSerializer,
                                  OrganisationTotalExpenditureSerializer)
from .organisation_document import OrganisationDocumentSerializer
from .organisation_location import (OrganisationLocationSerializer,
                                    OrganisationLocationExtraSerializer)
from .rsr_serializer import BaseRSRSerializer

logger = logging.getLogger(__name__)


class OrganisationSerializer(BaseRSRSerializer):

    total_budgets = OrganisationTotalBudgetSerializer(read_only=True, many=True, required=False)
    recipient_org_budgets = OrganisationRecipientOrgBudgetSerializer(
        read_only=True, many=True, required=False
    )
    region_budgets = OrganisationRegionBudgetSerializer(
        source='recipient_region_budgets', read_only=True, many=True, required=False
    )
    country_budgets = OrganisationCountryBudgetSerializer(
        source='recipient_country_budgets', read_only=True, many=True, required=False
    )
    total_expenditures = OrganisationTotalExpenditureSerializer(
        read_only=True, many=True, required=False
    )
    documents = OrganisationDocumentSerializer(read_only=True, many=True, required=False)
    locations = OrganisationLocationSerializer(read_only=True, many=True, required=False)
    logo = Base64ImageField(required=False, allow_empty_file=True, allow_null=True)

    latitude = serializers.CharField(source='primary_location.latitude', required=False)
    longitude = serializers.CharField(source='primary_location.longitude', required=False)
    city = serializers.CharField(source='primary_location.city', required=False)
    current_user_permissions = serializers.SerializerMethodField()

    class Meta:
        model = Organisation
        fields = '__all__'

    def create(self, validated_data):
        if 'primary_location' in validated_data and isinstance(validated_data['primary_location'], dict):
            location = validated_data.pop('primary_location', {})
        else:
            location = None

        instance = super(OrganisationSerializer, self).create(validated_data)

        if location is not None:
            location['location_target'] = instance.pk
            serializer = OrganisationLocationSerializer(data=location)
            try:
                serializer.is_valid(raise_exception=True)
            except Exception:
                # Delete organisation if location could not be created
                instance.delete()
                raise
            else:
                serializer.save()
                instance.refresh_from_db()

        return instance

    def get_current_user_permissions(self, organisation):
        user = self.context['request'].user
        permissions = dict(
            can_create_iati_export=user.has_perm('rsr.add_iatiexport', organisation),
            can_edit_iati_export=user.has_perm('rsr.change_iatiexport', organisation),
        )
        return permissions


class OrganisationExtraSerializer(OrganisationSerializer):

    primary_location = OrganisationLocationExtraSerializer()
    can_edit_users = serializers.SerializerMethodField()
    can_create_projects = serializers.SerializerMethodField()
    can_create_iati_exports = serializers.SerializerMethodField()

    class Meta(OrganisationSerializer.Meta):
        fields = (
            'id',
            'logo',
            'long_name',
            'name',
            'primary_location',
            'can_edit_users',
            'can_create_projects',
            'can_create_iati_exports',
            'enforce_program_projects',
            'content_owner',
        )

    def get_can_edit_users(self, organisation):
        user = self.context['request'].user
        return user.has_perm('rsr.change_employment', organisation)

    def get_can_create_projects(self, organisation):
        user = self.context['request'].user
        return user.has_perm('rsr.add_project', organisation)

    def get_can_create_iati_exports(self, organisation):
        user = self.context['request'].user
        return user.has_perm('rsr.add_iatiexport', organisation)


class OrganisationBasicSerializer(BaseRSRSerializer):

    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
            'long_name',
            'logo'
        )


# NOTE: Use this serializer only with organisations that are already known to be
# orgs where a user can edit them.
class UserManagementOrgSerializer(BaseRSRSerializer):

    can_edit_users = serializers.SerializerMethodField()

    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
            'long_name',
            'logo',
            'can_edit_users',
        )

    def get_can_edit_users(self, organisation):
        # NOTE: We always return True since the serializer is expected to be
        # used only for organisations which already known to be from a list of
        # organisations the user can edit.
        return True
