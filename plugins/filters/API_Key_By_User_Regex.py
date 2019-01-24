#API Key By User
@QueryRegistry.register(
    query_id='divvy.filter.service_access_key_by_username_regex_exclusion',
    name='API Key By User Regular Expression Exclusion',
    description=(
    'Exclude API keys by user using regular expressions. Note that '
    'only valid regular expressions will work. As an example, to '
    'search for for resources that do not include "test" in their '
    'names, use test'
    ),
    supported_clouds=[
        CloudType.ALICLOUD,
        CloudType.AMAZON_WEB_SERVICES,
        CloudType.AMAZON_WEB_SERVICES_GOV,
        CloudType.AMAZON_WEB_SERVICES_CHINA
    ],
    supported_resources=[ResourceType.SERVICE_ACCESS_KEY],
    settings_config=[
        StringField(
            name='regex_exclusion',
            display_name='Exclude Regular Expression',
            description=(
                'Exclude API Keys with names matching this expression.'
            ),
            options=[FieldOptions.REQUIRED, FieldOptions.MONOSPACE]
        )
    ]
)

def service_access_key_by_username_regex_exclusion(query, db_cls, settings_config):
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

## From exclude resource by name:

#     expression = settings_config.get('regex_exclusion')
#     try:
#         name_column = get_name_column(db_cls)
#     except ValueError:
#         pass
#     else:
#         query = query.filter(
#             not_(name_column.op('regexp')(r'%s' % expression))
#         )
#     return query