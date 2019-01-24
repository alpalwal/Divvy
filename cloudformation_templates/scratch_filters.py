#API Key By User
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
        )
    ]
)
def service_access_key_by_username(query, db_cls, settings_config):
    db = DivvyCloudGatewayORM()
    return query.filter(
        db_cls.user_resource_id.in_(
            db.session.query(
                dbo.ServiceUser.resource_id
            ).filter(
                dbo.ServiceUser.user_name.in_(settings_config['user_names'])
            )
        )
    )


#regex by name exclusion:
@QueryRegistry.register(
    query_id='divvy.filter.resource_name_regex_exclusion',
    name='Resource Name Regular Expression Exclusion',
    supported_resources=[],
    description=(
        'Exclude resources by name using regular expressions. Note that '
        'only valid regular expressions will work. As an example, to '
        'search for for resources that do not include "test" in their '
        'names, use test'
    ),
    settings_config=[
        StringField(
            name='regex_exclusion',
            display_name='Exclude Regular Expression',
            description=(
                'Exclude resources with names matching this expression.'
            ),
            options=[FieldOptions.REQUIRED, FieldOptions.MONOSPACE]
        )
    ]
)
def resource_name_regex_exclusion(query, db_cls, settings_config):
    expression = settings_config.get('regex_exclusion')
    try:
        name_column = get_name_column(db_cls)
    except ValueError:
        pass
    else:
        query = query.filter(
            not_(name_column.op('regexp')(r'%s' % expression))
        )
    return query