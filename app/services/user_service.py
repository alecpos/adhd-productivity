from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from app.services.auth_service import AuthService
from app.services.base_service import BaseService
from app.services.subscription_service import SubscriptionService


class UserService(BaseService):
    def __init__(self, db_session):
        super().__init__(db_session)
        self.auth = AuthService(db_session)
        self.subscription = SubscriptionService(db_session)
