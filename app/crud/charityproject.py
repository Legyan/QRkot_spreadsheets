from typing import Optional, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_project_id_by_name(
        self,
        name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == name)
        )
        db_project_id = db_project_id.scalars().first()
        return db_project_id

    async def get_project_invested_amount(
        self,
        project_id: int,
        session: AsyncSession,
    ) -> int:
        project_invested_amount = await session.execute(
            select(CharityProject.invested_amount).where(
                CharityProject.id == project_id
            )
        )
        return project_invested_amount.scalars().first()

    async def get_project_fully_invested(
        self,
        project_id: int,
        session: AsyncSession,
    ) -> bool:
        project_fully_invested = await session.execute(
            select(CharityProject.fully_invested).where(
                CharityProject.id == project_id
            )
        )
        return project_fully_invested.scalars().first()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession,
    ) -> List[CharityProject]:
        sorted_projects = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested
            ).order_by(
                func.julianday(CharityProject.close_date) -
                func.julianday(CharityProject.create_date)
            )
        )
        return sorted_projects.scalars().all()


charityproject_crud = CRUDCharityProject(CharityProject)
