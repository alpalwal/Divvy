from sqlalchemy import func 

from DivvyDb import DivvyDbObjects
from DivvyDb.DivvyCloudGatewayORM import DivvyCloudGatewayORM
from DivvyDb.QueryFilters.cloud_types import CloudType
from DivvyDb.QueryFilters.registry import QueryRegistry
from DivvyResource import ResourceType
from DivvyUtils.field_definition import SelectionField, FieldOptions

default_filters_author = 'Customer'

@QueryRegistry.register(
    query_id='custom.filter.storage_container_without_bucket_policy',
    name='Storage Container Without Bucket Public Policies Enabled On Parent Cloud',
    description=(
        'Identifies AWS S3 buckets which do not have the supplied bucket '
        'policies enabled at the parent cloud level.'
    ),
    supported_resources=[ResourceType.STORAGE_CONTAINER],
    settings_config=[
        SelectionField(
            name='policy_option',
            display_name='Policy Option',
            description='The setting to validate against',
            choices=[
                'IgnorePublicAcls',
                'BlockPublicPolicy',
                'BlockPublicAcls',
                'RestrictPublicBuckets'
            ],
            options=[FieldOptions.REQUIRED]
        )
    ],
    supported_clouds=[CloudType.AMAZON_WEB_SERVICES],
    version='19.2'
)
def storage_container_without_bucket_policy(query, db_cls, settings_config):
    # Avoid circular imports
    from DivvyWorkers.Harvesters.base import CorePropertyNames
    db = DivvyCloudGatewayORM()
    subq = db.session.query(
        DivvyDbObjects.OrganizationService.organization_service_id
    ).filter(
        DivvyDbObjects.OrganizationService.resource_id.notin_(
            db.session.query(
                DivvyDbObjects.ResourceProperty.resource_id
            ).filter(
                DivvyDbObjects.ResourceProperty.name == CorePropertyNames.bucket_public_policy
            ).filter(
                func.json_extract(
                    DivvyDbObjects.ResourceProperty.value,
                    '$."{0}"'.format(settings_config['policy_option'])
                ) == True
            )
        )
    )

    return query.filter(db_cls.organization_service_id.notin_(subq))

@QueryRegistry.register(
    query_id='custom.filter.storage_container_with_bucket_policy',
    name='Storage Container With Bucket Public Policies Enabled On Parent Cloud',
    description=(
        'Identifies AWS S3 buckets which do not have the supplied bucket '
        'policies enabled at the parent cloud level.'
    ),
    supported_resources=[ResourceType.STORAGE_CONTAINER],
    settings_config=[
        SelectionField(
            name='policy_option',
            display_name='Policy Option',
            description='The setting to validate against',
            choices=[
                'IgnorePublicAcls',
                'BlockPublicPolicy',
                'BlockPublicAcls',
                'RestrictPublicBuckets'
            ],
            options=[FieldOptions.REQUIRED]
        )
    ],
    supported_clouds=[CloudType.AMAZON_WEB_SERVICES],
    version='19.2'
)
def storage_container_with_bucket_policy(query, db_cls, settings_config):
    # Avoid circular imports
    from DivvyWorkers.Harvesters.base import CorePropertyNames
    db = DivvyCloudGatewayORM()
    subq = db.session.query(
        DivvyDbObjects.OrganizationService.organization_service_id
    ).filter(
        DivvyDbObjects.OrganizationService.resource_id.in_(
            db.session.query(
                DivvyDbObjects.ResourceProperty.resource_id
            ).filter(
                DivvyDbObjects.ResourceProperty.name == CorePropertyNames.bucket_public_policy
            ).filter(
                func.json_extract(
                    DivvyDbObjects.ResourceProperty.value,
                    '$."{0}"'.format(settings_config['policy_option'])
                ) == True
            )
        )
    )

    return query.filter(db_cls.organization_service_id.notin_(subq))

def load():
    pass
