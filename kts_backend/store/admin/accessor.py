import typing

from sqlalchemy import select

from kts_backend.admin.model import Admin, AdminModel
from kts_backend.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class AdminAccessor(BaseAccessor):
    async def get_by_email(self, email: str) -> Admin | None:
        async with self.app.database.session() as session:
            query = select(AdminModel).where(AdminModel.email == email)
            res = await session.scalars(query)
            admin = res.one_or_none()
            if admin:
                return Admin(
                    id=admin.id, email=admin.email, password=admin.password
                )
            return None

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session() as session:
            admin = AdminModel(email=email, password=password)
            session.add(admin)
            await session.commit()
            return Admin(id=admin.id, email=admin.email)
