from sqlalchemy import func, or_, and_, not_

from DivvyDb import DivvyDbObjects as dbo
from DivvyDb.DivvyCloudGatewayORM import DivvyCloudGatewayORM
from DivvyDb.QueryFilters.cloud_types import CloudType
from DivvyDb.QueryFilters.registry import QueryRegistry
from DivvyDb.QueryFilters.service_policy import policy_contains_permissions
from DivvyDb.QueryFilters.tag import RESOURCES_SUPPORTING_TAGS
from DivvyResource.resource_types import ResourceType
from DivvyUtils.field_definition import (
    BooleanField, MultiSelectionField, FieldOptions
)

default_filters_author = 'Discover'

@QueryRegistry.register(
    query_id='discover.filter.identity_resource_with_invalid_policy',
    name='Identity Resource Contains Invalid Actions (With Group Walking)',
    description=(
        'Identifies Users, Groups and Roles with attached/inline policies '
        'which contain specific actions (e.g. ec2:*). Note that ec2:* will '
        'directly match the permission ec2:*. If you want to search for '
        'wildcard permissions then use ec2:Create% which will surface '
        'only permissions prefixed with ec2:Create.'
    ),
    supported_clouds=[
        CloudType.ALICLOUD,
        CloudType.AMAZON_WEB_SERVICES,
        CloudType.AMAZON_WEB_SERVICES_GOV,
        CloudType.AMAZON_WEB_SERVICES_CHINA,
        CloudType.GOOGLE_CLOUD_PLATFORM
    ],
    supported_resources=[
        ResourceType.SERVICE_GROUP,
        ResourceType.SERVICE_ROLE,
        ResourceType.SERVICE_USER
    ],
    settings_config=[
        MultiSelectionField(
            choices=[],
            name='actions',
            display_name='Cloud Actions',
            description=(
                'Enter blacklisted actions. Note that searching is case '
                'insensitive.'
            ),
            options=[FieldOptions.REQUIRED, FieldOptions.TAGS]
        ),
        MultiSelectionField(
            choices=[],
            name='resources',
            display_name='Resources (Optional and for AWS only)',
            description=(
                'Enter target resource. As an example enter * for all resources '
                'or individual ARNs. Leaving this blank will match on any '
                'resource statement.'
            ),
            options=[FieldOptions.TAGS]
        ),
        BooleanField(
            name='walk_groups',
            display_name='Walk Groups?',
            description=(
                'When enabled, the filter will include results for users who '
                'are associated with groups that match the criteria.'
            ),
            options=[FieldOptions.REQUIRED, FieldOptions.TAGS]
        )
    ]
)
def identity_resource_with_invalid_policy(query, db_cls, settings_config):
    # First we need to build a list of policy documents and iterate over them
    db = DivvyCloudGatewayORM()
    actions = [action.lower() for action in settings_config['actions']]
    resources = settings_config.get('resources', [])
    policy_resource_ids = []
    invalid_user_resource_ids = []

    for row in db.session.query(
        dbo.ServicePolicy.resource_id,
        dbo.ServicePolicyDocument.document
    ).filter(
        dbo.ServicePolicy.arn == dbo.ServicePolicyDocument.policy_arn
    ).filter(
        dbo.ServicePolicyDocument.is_default_version.is_(True)
    ).filter(
        dbo.ServicePolicy.attachment_count != 0
    ):
        if policy_contains_permissions(
            row.document, actions, row.resource_id, resources
        ):
            policy_resource_ids.append(row.resource_id)

    for row in db.session.query(
        dbo.ServiceManagedPolicy.resource_id,
        dbo.ServiceManagedPolicyDocument.document
    ).filter(
        dbo.ServiceManagedPolicy.policy_id == dbo.ServiceManagedPolicyDocument.document_id
    ).filter(
        dbo.ServiceManagedPolicyDocument.is_default_version.is_(True)
    ):
        if policy_contains_permissions(
            row.document, actions, row.resource_id, resources
        ):
            policy_resource_ids.append(row.resource_id)

    for row in db.session.query(
        db_cls.resource_id,
        db_cls.inline_policies
    ).filter(
        db_cls.inline_policies.isnot(None)
    ):
        for policy in row.inline_policies:
            if isinstance(policy, dict):
                for _policy_name, document in policy.items():  # pylint: disable=W0612
                    if policy_contains_permissions(
                        document, actions, None, resources
                    ):
                        invalid_user_resource_ids.append(row.resource_id)

    if (
        db_cls.resource_type == ResourceType.SERVICE_USER and
        settings_config.get('walk_groups') is True
    ):
        query = query.filter(or_(
            db_cls.resource_id.in_(
                db.session.query(
                    dbo.ResourceLink.left_resource_id
                ).filter(
                    dbo.ResourceLink.right_resource_id.in_(policy_resource_ids)
                )
            ),
            db_cls.resource_id.in_(invalid_user_resource_ids),
            db_cls.resource_id.in_(
                db.session.query(
                    dbo.ResourceLink.left_resource_id
                ).filter(
                    dbo.ResourceLink.right_resource_id.in_(
                        db.session.query(
                            dbo.ResourceLink.left_resource_id
                        ).filter(
                            dbo.ResourceLink.left_resource_id.like('servicegroup:%')
                        ).filter(
                            dbo.ResourceLink.right_resource_id.in_(policy_resource_ids)
                        )
                    )
                )
            )
        ))

    else:
        query = query.filter(or_(
            db_cls.resource_id.in_(
                db.session.query(
                    dbo.ResourceLink.left_resource_id
                ).filter(
                    dbo.ResourceLink.right_resource_id.in_(policy_resource_ids)
                )
            ),
            db_cls.resource_id.in_(invalid_user_resource_ids)
        ))

    return query

def load():
    pass
