from dependency_injector import containers, providers

from app.core.config_service import ConfigService
from app.services.auth_service import AuthService
from app.services.database_service import DatabaseService
from app.services.logging_service import LoggingService


class Container(containers.DeclarativeContainer):
    """Application container."""

    config = providers.Singleton(ConfigService)
    database = providers.Singleton(DatabaseService, db_url=config.provided.database_url_with_args)
    logging = providers.Factory(LoggingService, service_name=config.provided.APP_NAME)
    auth = providers.Factory(AuthService, db=database.provided.get_session)
