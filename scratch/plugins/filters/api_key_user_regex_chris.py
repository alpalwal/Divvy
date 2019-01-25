@QueryRegistry.register(
    query_id='service_access_key_by_username',
    name='API Key By User',
    description=(
        'Match API keys which belong to specific users.'
    ),
    supported_clouds=[
        CloudType.ALICLOUD,
        CloudType.AMAZON_WEB_SERVICES,
        CloudType.AMAZON_WEB_SERVICES_GOV,
        CloudType.AMAZON_WEB_SERVICES_CHINA
    ],
    supported_resources=[ResourceType.SERVICE_ACCESS_KEY],
    settings_config=[
        MultiSelectionField(
            choices=[],
            name='user_names',
            display_name='User Names',
            description=(
                'Match API keys owned by the supplied user names.'
            ),
            options=[FieldOptions.REQUIRED, FieldOptions.TAGS]
        ),
        BooleanField(
            name='wildcard_search',
            display_name='Wildcard',
            description='Leverage wildcard search'
        ),
        BooleanField(
            name='exclude',
            display_name='Exclude',
            description=(
                'When enabled, API keys belonging to users whose names match '
                'the supplied configuration will be excluded'
            )
        )
    ]
)
def service_access_key_by_username(query, db_cls, settings_config):
    db = DivvyCloudGatewayORM()
    if settings_config.get('wildcard_search'):
        clauses = or_()  # empty starting value
        for user_name in settings_config['user_names']:
            if settings_config.get('exclude'):
                next_clause = or_(
                    db_cls.user_name.notlike('%{0}%'.format(user_name))
                )
            else:
                next_clause = or_(
                    db_cls.user_name.like('%{0}%'.format(user_name))
                )
            clauses = or_(clauses, next_clause)
        query = query.filter(clauses)
    else:
        if settings_config.get('exclude'):
            query = query.filter(
                db_cls.user_name.notin_(settings_config['user_names'])
            )
        else:
            query = query.filter(
                db_cls.user_name.in_(settings_config['user_names'])
            )

    return query