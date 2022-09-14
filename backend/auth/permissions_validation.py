from project.shared.necessities import AppStaffPermissions
from fastapi.exceptions import HTTPException


def validate_app_staff_permissions(requested_permissions: AppStaffPermissions, giver_permissions: AppStaffPermissions):
    if requested_permissions.can_create_designation and (len(requested_permissions.permitted_roles_for_designation.create_designation_in_roles) == 0 or len(requested_permissions.permitted_roles_for_designation.create_permission_levels)==0):
        raise HTTPException(
            406, "if can_create_designation is true, create_designation_in_roles and create_permission_levels must have at least one role.")
    if requested_permissions.can_authorize_someone_to_create_designation and (len(requested_permissions.permitted_roles_for_designation.authorize_to_create_designation_in_roles) == 0 or len(requested_permissions.permitted_roles_for_designation.authorize_to_create_permission_levels)==0):
        raise HTTPException(
            406, "if can_authorize_someone_to_create_designation is true, authorize_to_create_designation_in_roles and authorize_to_create_permission_levels must have at least one role.")
    if requested_permissions.can_authorize_someone_to_permit_other_to_create_designation and (len(requested_permissions.permitted_roles_for_designation.authorize_to_permit_others_for_creation_in_roles) == 0 or len(requested_permissions.permitted_roles_for_designation.authorize_to_permit_others_for_creation_in_levels)==0):
        raise HTTPException(
            406, "if can_authorize_someone_to_permit_other_to_create_designation is true, authorize_to_permit_others_for_creation_in_roles and authorize_to_permit_others_for_creation_in_levels must have at least one role.")
    if not requested_permissions.can_create_designation and (len(requested_permissions.permitted_roles_for_designation.create_designation_in_roles) != 0 or len(requested_permissions.permitted_roles_for_designation.create_permission_levels!=0)):
        raise HTTPException(
            406, "if can_create_designation is false, create_designation_in_roles and create_permission_levels must be empty list.")
    if not requested_permissions.can_authorize_someone_to_create_designation and (len(requested_permissions.permitted_roles_for_designation.authorize_to_create_designation_in_roles) != 0 or len(requested_permissions.permitted_roles_for_designation.authorize_to_create_permission_levels)!=0):
        raise HTTPException(
            406, "if can_authorize_someone_to_create_designation is false, authorize_to_create_designation_in_roles and authorize_to_create_permission_levels must be empty list.")
    if not requested_permissions.can_authorize_someone_to_permit_other_to_create_designation and (len(requested_permissions.permitted_roles_for_designation.authorize_to_permit_others_for_creation_in_roles) != 0 or len(requested_permissions.permitted_roles_for_designation.authorize_to_permit_others_for_creation_in_levels)!=0):
        raise HTTPException(
            406, "if can_authorize_someone_to_permit_other_to_create_designation is false, authorize_to_permit_others_for_creation_in_roles and authorize_to_permit_others_for_creation_in_levels must be empty list.")
    if giver_permissions.all_auth:
        return True
    if requested_permissions.can_add_new_staff and not giver_permissions.can_authorize_some_staff_to_add_new_one:
        raise HTTPException(
            406, "You are not authorized to permit someone to add new staff.")
    if requested_permissions.can_onboard and not giver_permissions.can_authorize_some_staff_to_onboard:
        raise HTTPException(
            406, "You are not authorized to permit someone to onboard.")
    if requested_permissions.can_create_designation and not giver_permissions.can_authorize_someone_to_create_designation:
        raise HTTPException(
            406, "You are not authorized to permit someone to create designation.")
    if requested_permissions.can_create_designation and giver_permissions.can_authorize_someone_to_create_designation:
        for requested_role in requested_permissions.permitted_roles_for_designation.create_designation_in_roles:
            if requested_role not in giver_permissions.permitted_roles_for_designation.authorize_to_create_designation_in_roles:
                raise HTTPException(
                    406, f"You are not authorized to permit someone to create designation for role {requested_role}")
        for requested_role in requested_permissions.permitted_roles_for_designation.create_permission_levels:
            if requested_role not in giver_permissions.permitted_roles_for_designation.authorize_to_create_permission_levels:
                raise HTTPException(
                    406, f"You are not authorized to permit someone to create designation for permission level {requested_role}")
    if requested_permissions.can_authorize_someone_to_create_designation and not giver_permissions.can_authorize_someone_to_permit_other_to_create_designation:
        raise HTTPException(
            406, "You are not authorized to permit others to further permit for designation.")
    if requested_permissions.can_authorize_someone_to_create_designation and giver_permissions.can_authorize_someone_to_permit_other_to_create_designation:
        for requested_role in requested_permissions.permitted_roles_for_designation.authorize_to_create_designation_in_roles:
            if requested_role not in requested_permissions.permitted_roles_for_designation.authorize_to_permit_others_for_creation_in_roles:
                raise HTTPException(
                    406, "You are not authorized to permit someone to permit further for creating designation in "+requested_role)
        for requested_role in requested_permissions.permitted_roles_for_designation.authorize_to_create_permission_levels:
            if requested_role not in requested_permissions.permitted_roles_for_designation.authorize_to_permit_others_for_creation_in_levels:
                raise HTTPException(
                    406, "You are not authorized to permit someone to permit further for creating designation in "+requested_role)
    if (
        requested_permissions.can_authorize_some_staff_to_add_new_one
        or requested_permissions.can_authorize_some_staff_to_onboard
        or requested_permissions.all_auth
        or requested_permissions.can_authorize_someone_to_permit_other_to_create_designation
    ) and not giver_permissions.all_auth:
        raise HTTPException(
            406, "You are not authorized to authorize someone to permit another one for onboarding or adding new staff.")
    return True
