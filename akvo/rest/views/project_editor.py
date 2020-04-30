# -*- coding: utf-8 -*-
"""Akvo RSR is covered by the GNU Affero General Public License.

See more details in the license.txt file located at the root folder of the Akvo RSR module.
For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.
"""

from django.contrib.admin.models import LogEntry, CHANGE
from akvo.rsr.models.result.indicator_dimension import IndicatorDimensionName
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from rest_framework import status as http_status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import ValidationError as RestValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from akvo.rest.models import TastyTokenAuthentication
from akvo.rsr.models import (
    Indicator, Keyword, Organisation, Project, ProjectEditorValidationSet, Result
)
from .project_editor_utils import (
    convert_related_objects, create_or_update_objects_from_data, log_changes, update_object
)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def project_editor(request, pk=None):
    """The main API call for saving any data entered in the project editor."""

    # Retrieve project and user information, and check user permissions to edit the project
    project = Project.objects.get(pk=pk)
    user = request.user

    if not user.has_perm('rsr.change_project', project):
        return HttpResponseForbidden()

    # Retrieve form data and set default values
    data = request.POST.copy()
    errors, changes, rel_objects = create_or_update_objects_from_data(project, data)
    # Update the IATI checks for every save in the editor.
    updated_project = Project.objects.get(pk=pk)
    updated_project.update_iati_checks()

    # Ensure errors are properly encoded
    for error in errors:
        if 'location' in error['name'] and 'Invalid literal' in error['error']:
            error['error'] = 'Only decimal values are accepted.'
        else:
            error['error'] = str(error['error'], errors='ignore')

    return Response(
        {
            'changes': log_changes(changes, user, project),
            'errors': errors,
            'rel_objects': convert_related_objects(rel_objects),
            'need_saving': [data],
        }
    )


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@transaction.atomic
def project_editor_reorder_items(request, project_pk=None):
    """API call to reorder results or indicators"""

    errors, item_list, item_selected, swap_id = [], [], None, -1

    item_type = request.POST.get('item_type', False)
    item_id = request.POST.get('item_id', False)
    item_direction = request.POST.get('item_direction', False)

    if item_type == 'result':
        item_selected = Result.objects.get(id=item_id)
        item_list = Result.objects.filter(project_id=project_pk)
    elif item_type == 'indicator':
        item_selected = Indicator.objects.get(id=item_id)
        item_list = Indicator.objects.filter(result_id=item_selected.result_id)
    else:
        errors += ['Invalid item type']

    if not errors:
        # assign order if it doesn't already exist or is messed up
        n_items = item_list.count()
        if n_items > 0 and set(item_list.values_list('order', flat=True)) != set(range(n_items)):
            for i, item in enumerate(item_list):
                item.order = i
                item.save()

        if item_type == 'result':
            item_original_order = Result.objects.get(id=item_id).order
        else:
            item_original_order = Indicator.objects.get(id=item_id).order

        if item_direction == 'up' and not item_original_order < 1:
            item_swap = item_list.get(order=item_original_order - 1)
            item_swap.order = item_original_order
            item_swap.save()

            swap_id = item_swap.id

            if item_selected:
                item_selected.order = item_original_order - 1
                item_selected.save()

        elif item_direction == 'down' and not item_original_order >= len(item_list) - 1:
            item_swap = item_list.get(order=item_original_order + 1)
            item_swap.order = item_original_order
            item_swap.save()

            swap_id = item_swap.id

            if item_selected:
                item_selected.order = item_original_order + 1
                item_selected.save()

        else:
            errors += ['Unable to reorder the selected item, it may already be at top/bottom of '
                       'list.']

    return Response(
        {
            'errors': errors,
            'swap_id': swap_id,
        }
    )


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def project_editor_import_results(request, project_pk=None):
    project = Project.objects.get(pk=project_pk)
    user = request.user

    if not user.can_import_results(project):
        return HttpResponseForbidden()

    status_code, message = project.import_results()

    if status_code == 1:
        data = {'project_id': project_pk, 'import_success': True}
        status = http_status.HTTP_201_CREATED
    else:
        data = {'project_id': project_pk, 'import_success': False, 'message': message}
        status = http_status.HTTP_400_BAD_REQUEST

    return Response(data=data, status=status)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def project_editor_copy_results(request, project_pk=None, source_pk=None):
    project = Project.objects.get(pk=project_pk)
    source_project = Project.objects.get(pk=source_pk)
    user = request.user

    if not user.can_import_results(project):
        return HttpResponseForbidden()

    if not user.has_perm('rsr.change_project', source_project):
        return HttpResponseForbidden()

    data = {'project_id': project_pk, 'copy_success': True}
    try:
        project.copy_results(source_project)
        status = http_status.HTTP_201_CREATED
    except RuntimeError as e:
        data['copy_success'] = False
        data['message'] = str(e)
        status = http_status.HTTP_400_BAD_REQUEST

    return Response(data=data, status=status)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((SessionAuthentication, TastyTokenAuthentication))
def project_editor_import_result(request, project_pk, parent_result_id):
    try:
        project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        return HttpResponseNotFound()
    except Project.MultipleObjectsReturned:
        return HttpResponseBadRequest()

    user = request.user
    if not user.can_import_results(project):
        return HttpResponseForbidden()

    try:
        result = project.import_result(parent_result_id)
    except (Project.DoesNotExist, Project.MultipleObjectsReturned, Result.DoesNotExist,
            Result.MultipleObjectsReturned, ValidationError) as e:
        raise RestValidationError(str(e))

    data = {'result_id': result.pk, 'import_success': True}
    return Response(data=data, status=http_status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((SessionAuthentication, TastyTokenAuthentication))
def project_editor_import_indicator(request, project_pk, parent_indicator_id):
    try:
        project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        return HttpResponseNotFound()
    except Project.MultipleObjectsReturned:
        return HttpResponseBadRequest()

    user = request.user
    if not user.can_import_results(project):
        return HttpResponseForbidden()

    try:
        indicator = project.import_indicator(parent_indicator_id)
    except (Project.DoesNotExist, Project.MultipleObjectsReturned, Indicator.DoesNotExist,
            Indicator.MultipleObjectsReturned, ValidationError) as e:
        raise RestValidationError(str(e))

    data = {'indicator_id': indicator.pk, 'import_success': True}
    return Response(data=data, status=http_status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def project_editor_add_validation(request, project_pk=None, validation_pk=None):
    project = Project.objects.get(pk=project_pk)
    validation_set = ProjectEditorValidationSet.objects.get(pk=validation_pk)
    user = request.user

    if not user.has_perm('rsr.change_project', project):
        return HttpResponseForbidden()

    if validation_set not in project.validations.all():
        project.validations.add(validation_set)

        change_message = '%s %s.' % (_('Project editor, added: validation set'), validation_set)

        LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=ContentType.objects.get_for_model(project).pk,
            object_id=project.pk,
            object_repr=str(project),
            action_flag=CHANGE,
            change_message=change_message
        )

    return Response({})


@api_view(['DELETE'])
@permission_classes((IsAuthenticated, ))
def project_editor_remove_validation(request, project_pk=None, validation_pk=None):
    project = Project.objects.get(pk=project_pk)
    validation_set = ProjectEditorValidationSet.objects.get(pk=validation_pk)
    user = request.user

    if not user.has_perm('rsr.change_project', project):
        return HttpResponseForbidden()

    if validation_set in project.validations.all():
        project.validations.remove(validation_set)

        change_message = '%s %s.' % (_('Project editor, deleted: validation set'), validation_set)

        LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=ContentType.objects.get_for_model(project).pk,
            object_id=project.pk,
            object_repr=str(project),
            action_flag=CHANGE,
            change_message=change_message
        )

    return Response({})


@api_view(['DELETE'])
@permission_classes((IsAuthenticated, ))
def project_editor_remove_keyword(request, project_pk=None, keyword_pk=None):
    project = Project.objects.get(pk=project_pk)
    keyword = Keyword.objects.get(pk=keyword_pk)
    user = request.user

    if not user.has_perm('rsr.change_project', project):
        return HttpResponseForbidden()

    if keyword in project.keywords.all():
        project.keywords.remove(keyword)

        change_message = '%s %s.' % (_('Project editor, deleted: keyword'), keyword)

        LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=ContentType.objects.get_for_model(project).pk,
            object_id=project.pk,
            object_repr=str(project),
            action_flag=CHANGE,
            change_message=change_message
        )

    return Response({})


@api_view(['DELETE'])
@permission_classes((IsAuthenticated, ))
def project_editor_remove_indicator_dimension(request, indicator_pk=None, dimension_pk=None):

    indicator = Indicator.objects.get(pk=indicator_pk)
    dimension = IndicatorDimensionName.objects.get(pk=dimension_pk)
    user = request.user

    if not user.has_perm('rsr.change_project', indicator.result.project):
        return HttpResponseForbidden()

    if indicator.parent_indicator is not None:
        return HttpResponseForbidden()

    if dimension in indicator.dimension_names.all():
        indicator.dimension_names.remove(dimension)

        change_message = '%s %s.' % (_('Project editor, relation removed: indicator dimension'), dimension)

        LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=ContentType.objects.get_for_model(indicator).pk,
            object_id=indicator.pk,
            object_repr=str(indicator),
            action_flag=CHANGE,
            change_message=change_message
        )

    return Response({})


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def project_editor_organisation_logo(request, pk=None):
    org = Organisation.objects.get(pk=pk)
    user = request.user

    if not user.has_perm('rsr.change_organisation', org):
        return HttpResponseForbidden()

    data = request.data
    errors, changes, rel_objects = [], [], {}

    if 'logo' in data:
        changes, errors, rel_objects = update_object(
            Organisation, pk, ['logo'], [''], [data['logo']], changes, errors,
            rel_objects, 'rsr_organisation.' + str(pk)
        )

    return Response({'errors': errors})


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def log_project_addition(request, project_pk=None):
    project = Project.objects.get(pk=project_pk)
    user = request.user
    if not user.has_perm('rsr.change_project', project):
        return HttpResponseForbidden()

    Project.log_project_addition(project_pk, user)
    content = {'log_entry': 'added successfully'}
    return Response(content, status=http_status.HTTP_201_CREATED)
