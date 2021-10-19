# -*- coding: utf-8 -*-

# Akvo Reporting is covered by the GNU Affero General Public License.
# See more details in the license.txt file located at the root folder of the Akvo RSR module.
# For additional details on the GNU license please see < http://www.gnu.org/licenses/agpl.html >.

from django.db.models import Q
from akvo.rsr.models import (
    Project, RelatedProject, Result, Indicator, IndicatorPeriod, IndicatorDimensionName, IndicatorDimensionValue, DefaultPeriod
)


def get_lineage(project):
    project_id = project.id
    family = [project_id]
    while True:
        parent_id = Project.objects.filter(
            Q(
                related_projects__related_project=project_id,
                related_projects__relation=RelatedProject.PROJECT_RELATION_CHILD
            ) | Q(
                related_to_projects__project=project_id,
                related_to_projects__relation=RelatedProject.PROJECT_RELATION_PARENT
            )
        ).values_list('id', flat=True).first()
        if parent_id is None:
            break
        family.append(parent_id)
        project_id = parent_id
    return family


def get_nearest_common_ancestor(first_lineage, second_lineage):
    for it in first_lineage:
        if it in second_lineage:
            return it


def make_tree_from_list(items, parent_attr):
    tree = []
    ids = [it['id'] for it in items]
    lookup = {item['id']: {'item': item, 'children': []} for item in items}
    for item in items:
        item_id = item['id']
        node = lookup[item_id]
        parent_id = item.get(parent_attr, None)
        # Root node, or any items with parents outside of the project ancestry are added to the tree
        if not parent_id or parent_id not in ids:
            tree.append(node)
        else:
            lookup[parent_id]['children'].append(node)
    return tree


def get_leaf(branch):
    return get_leaf(branch['children'][0]) if len(branch['children']) else branch['item']


def make_target_parent_map(tree, project_attr, project_id, new_parent_id):
    target_parent_map = {}
    for node in tree:
        if len(node['children']) < 2:
            # Node is either empty or it only have on side of the tree leaf.
            # This will happen when the child removes the imported parent's RF object
            # or it creates a new one that is not part of the parent's RF
            continue
        children = node['children']
        first, second = get_leaf(children[0]), get_leaf(children[1])
        if first[project_attr] == project_id and second[project_attr] == new_parent_id:
            target_parent_map[first['id']] = second['id']
        elif second[project_attr] == project_id and first[project_attr] == new_parent_id:
            target_parent_map[second['id']] = first['id']
        else:
            print('Ignoring ambiguous lineage tree node', node)
    return target_parent_map


RF_MODELS_CONFIG = {
    # key: (Model, parent_attribute, project_relation)
    'results': (Result, 'parent_result', 'project'),
    'indicators': (Indicator, 'parent_indicator', 'result__project'),
    'periods': (IndicatorPeriod, 'parent_period', 'indicator__result__project'),
    'dimension_names': (IndicatorDimensionName, 'parent_dimension_name', 'project'),
    'dimension_values': (IndicatorDimensionValue, 'parent_dimension_value', 'name__project'),
    'default_periods': (DefaultPeriod, 'parent_id', 'project'),
}


def get_rf_change_candidates(project, new_parent):
    project_lineage_ids = get_lineage(project)
    new_parent_lineage_ids = get_lineage(new_parent)
    # Only hierarchy up to the nearest common ancestor are needed to link between the project and the new parent.
    # Don't include project to find commond ancestor to prevent the possibility that new parent is child of project.
    common_ancestor_id = get_nearest_common_ancestor(project_lineage_ids[1:], new_parent_lineage_ids)
    if common_ancestor_id is None:
        print('No common ancestor found')
        return {}
    # Remove all projects that are ancestors of the nearest common ancestor and make the nearest common ancestor
    # as the root of the hierarchy.
    project_ids = set(project_lineage_ids).symmetric_difference(set(new_parent_lineage_ids)) | {common_ancestor_id}
    candidates = {}
    for key, config in RF_MODELS_CONFIG.items():
        model, parent_attr, project_relation = config
        filter_arg = {f"{project_relation}__in": project_ids}
        items = model.objects.filter(**filter_arg).values('id', parent_attr, project_relation)
        items_tree = make_tree_from_list(items, parent_attr)
        candidates[key] = make_target_parent_map(items_tree, project_relation, project.id, new_parent.id)
    return candidates


def change_parent(project, new_parent, verbosity=0):
    """Change the parent of a project to the specified new parent.

    This function changes a project's parent including its Result Framework
    objects by traversing up the hierarchy to find the nearest common ancestor
    then creates a binary lineage tree connecting the project and the new
    parent using the nearest common ancestor as root. Then, it uses the lineage
    tree connection to resolve each RF object's new parent.

    """

    old_parent = project.parents_all().first()
    if old_parent.id == new_parent.id:
        if verbosity > 0:
            print("New parent same as current parent")
        return
    # change parents of RF items
    change_candidates = get_rf_change_candidates(project, new_parent)
    for key, candidates in change_candidates.items():
        model, parent_attr, _ = RF_MODELS_CONFIG[key]
        for item_id, target_id in candidates.items():
            if verbosity > 1:
                print(f"Change {key} parent of {item_id} to {target_id}")
            model.objects.filter(id__in=[item_id]).update(**{f"{parent_attr}_id": target_id})
    if verbosity > 0:
        print(f"Change project {project.title} (ID:{project.id}) parent to {new_parent.title} (ID:{new_parent.id})")
    RelatedProject.objects.filter(
        project=old_parent, related_project=project, relation='2'
    ).update(project=new_parent)
    RelatedProject.objects.filter(
        related_project=old_parent, project=project, relation='1'
    ).update(related_project=new_parent)
    # Handle any results etc only on the new parent, but not on the old parent.
    project.do_import_results(new_parent)
    # FIXME: The function could possibly be re-written to make this
    # unnecessary? The new ordering is only necessary at the child level if
    # parent has no ordering...
    ordering = sorted([
        # Avoid int vs None comaparison errors
        tuple(9999 if it is None else it for it in each)
        for each
        in project.results.values_list('parent_result__order', 'parent_result__id', 'order', 'id')
    ])
    for order, (_, _, _, result_id) in enumerate(ordering, start=1):
        project.results.filter(id=result_id).update(order=order)