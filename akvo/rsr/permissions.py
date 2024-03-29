# -*- coding: utf-8 -*-

# Akvo RSR is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module.
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

import rules

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from akvo.cache import cache_with_key
from .models import Employment, IatiExport, Organisation, PartnerSite, Project, ProjectUpdate

GROUP_NAME_ADMINS = 'Admins'
GROUP_NAME_ME_MANAGERS = 'M&E Managers'
GROUP_NAME_PROJECT_EDITORS = 'Project Editors'
GROUP_NAME_USERS = 'Users'
GROUP_NAME_ENUMERATORS = 'Enumerators'
GROUP_NAME_USER_MANAGERS = 'User Managers'

PERM_NAME_GROUP_MAP = {
    'is_org_admin': [GROUP_NAME_ADMINS],
    'is_org_user_manager': [GROUP_NAME_USER_MANAGERS],
    'is_org_me_manager_or_project_editor': [GROUP_NAME_PROJECT_EDITORS, GROUP_NAME_ME_MANAGERS],
    'is_org_me_manager': [GROUP_NAME_ME_MANAGERS],
    'is_org_user': [GROUP_NAME_USERS],
    'is_org_enumerator': [GROUP_NAME_ENUMERATORS],
}

NO_EDIT_ROLES = [GROUP_NAME_USERS, GROUP_NAME_USER_MANAGERS, GROUP_NAME_ENUMERATORS]
EDIT_ROLES = [GROUP_NAME_ADMINS, GROUP_NAME_ME_MANAGERS, GROUP_NAME_PROJECT_EDITORS]
CREATE_PROJECT_ROLES = [GROUP_NAME_ADMINS]


@rules.predicate
def is_rsr_admin(user):
    if user.is_authenticated and user.is_admin:
        return True
    return False


def _user_has_group_permissions(user, obj, group_names):
    User = get_user_model()
    if not user.is_authenticated:
        return False

    employments = user.approved_employments(group_names=group_names)
    has_employments = employments.exists()
    if not has_employments:
        return False

    if obj is None:
        return True

    if isinstance(obj, ProjectUpdate):
        if group_names == [GROUP_NAME_ADMINS]:
            # Check if user can admin the user making the update

            # NOTE: We could set `obj = user` and just see if the admin has the
            # right permissions on the user, but admins cannot modify content
            # owned users, only their employments. This seems to be reasonable,
            # though, it may be harmless to change. We therefor use an ugly
            # Employment QuerySet here to check further.
            obj = obj.user.employers.all()
            id_ = None
        else:
            return False

    elif hasattr(obj, 'project_id'):
        id_ = obj.project_id

    elif isinstance(obj, Project):
        id_ = obj.id

    elif hasattr(obj, 'project_relation'):
        query = {obj.project_relation: [obj.id]}
        id_ = Project.objects.values_list('id', flat=True).get(**query)

    else:
        id_ = None

    if id_:
        return user_has_perm(user, employments, id_)

    # FIXME: Admins can only edit directly employed users, not content owned
    # users. Admins can change employments of content_owned_users, though
    all_users = employments.organisations().users().values_list('id', flat=True)
    if isinstance(obj, User):
        return obj.id in all_users

    # NOTE: This is a "caching" hack. The query for content_owned_organisations
    # is pretty slow, and doing it multiple times per request is a disaster.
    # Per request, though, the user object should ideally be created once and
    # only once. So, we are caching the ids of the content owned organisations
    # on the user object, and avoiding multiple slow queries.
    if not hasattr(user, '_content_owned_organisations'):
        content_owned_organisations = employments.organisations()\
                                                 .content_owned_organisations()\
                                                 .values_list('id', flat=True)
        user._content_owned_organisations = content_owned_organisations
    else:
        content_owned_organisations = user._content_owned_organisations

    if isinstance(obj, Organisation):
        return obj.id in content_owned_organisations

    if isinstance(obj, Employment):
        return obj.organisation_id in content_owned_organisations

    if isinstance(obj, QuerySet) and obj.model == Employment:
        # NOTE: We reach here from the ProjectUpdate check above
        return bool(
            set(obj.values_list('organisation_id', flat=True)) & set(content_owned_organisations)
        )

    if isinstance(obj, PartnerSite):
        return obj.organisation_id in content_owned_organisations

    if isinstance(obj, IatiExport):
        return obj.reporting_organisation_id in content_owned_organisations

    if hasattr(obj, 'location_target') and isinstance(obj.location_target, Organisation):
        return obj.location_target_id in content_owned_organisations

    return False


@rules.predicate
def is_org_admin(user, obj):
    group_names = PERM_NAME_GROUP_MAP['is_org_admin']
    return _user_has_group_permissions(user, obj, group_names)


@rules.predicate
def is_org_user_manager(user, obj):
    group_names = PERM_NAME_GROUP_MAP['is_org_user_manager']
    return _user_has_group_permissions(user, obj, group_names)


@rules.predicate
def is_org_me_manager_or_project_editor(user, obj):
    group_names = PERM_NAME_GROUP_MAP['is_org_me_manager_or_project_editor']
    return _user_has_group_permissions(user, obj, group_names)


@rules.predicate
def is_org_me_manager(user, obj):
    group_names = PERM_NAME_GROUP_MAP['is_org_me_manager']
    return _user_has_group_permissions(user, obj, group_names)


@rules.predicate
def is_org_user(user, obj):
    group_names = PERM_NAME_GROUP_MAP['is_org_user']
    return _user_has_group_permissions(user, obj, group_names)


@rules.predicate
def is_org_enumerator(user, obj):
    group_names = PERM_NAME_GROUP_MAP['is_org_enumerator']
    return _user_has_group_permissions(user, obj, group_names)


@rules.predicate
def is_self(user, obj):
    if not obj:
        return True
    if isinstance(obj, get_user_model()) and obj == user:
        return True
    if isinstance(obj, Employment) and obj.user == user:
        return True
    return False


@rules.predicate
def is_own(user, obj):
    if obj is None:
        return True
    if not hasattr(obj, 'user_id'):
        return False
    return obj.user_id == user.id


def user_filtered_projects_cache_key(user, hierarchy_org, organisations):
    hierarchy_org_id = hierarchy_org.pk if hierarchy_org is not None else 0
    org_ids = ','.join(sorted({str(org.pk) for org in organisations.only('pk')}))
    key = 'user_filtered_projects:{}:{}:{}'.format(user.id, hierarchy_org_id, org_ids)
    return key


def user_has_perm(user, employments, project_id):
    """Check if a user has access to a project based on their employments."""

    from akvo.rsr.models import Project

    project = Project.objects.get(id=project_id)
    hierarchy_org = project.get_hierarchy_organisation()
    organisations = employments.organisations()
    filtered_projects = user_filtered_project_ids(user, hierarchy_org, organisations)
    return project_id in filtered_projects


@cache_with_key(user_filtered_projects_cache_key, timeout=15)
def user_filtered_project_ids(user, hierarchy_org, organisations):

    from akvo.rsr.models import ProjectHierarchy

    # Projects that is a program's root_project where user does not have access directly, will be excluded from the list
    indirect_programs = ProjectHierarchy.objects.exclude(
        id__in=ProjectHierarchy.objects.filter(root_project__partners__in=organisations).values_list('id', flat=True)
    ).values_list('root_project__id', flat=True)
    all_projects = organisations.content_owned_organisations().all_projects().exclude(id__in=indirect_programs).distinct()
    filtered_projects = set(all_projects.values_list('id', flat=True))
    return filtered_projects
