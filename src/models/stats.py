import datetime
from typing import Annotated

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

from utils.time import current_timestamp

Weight = Annotated[float, Field(ge=0, le=500, description="Body Weight, kg")]
StatRatio = Annotated[float, Field(ge=0, le=1, description="Stat Ratio, %")]
Height = Annotated[float, Field(ge=10, le=300, description="Height, cm")]


class ParamRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="RESTRICT")
    created_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=current_timestamp,
    )
    measured_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=current_timestamp,
    )
    modified_at: datetime.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, onupdate=current_timestamp
        ),
        default_factory=current_timestamp,
    )
    deleted_at: datetime.datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    weight: Weight
    height: Height
    fat_percent: StatRatio | None
    muscle_percent: StatRatio | None

    @property
    def fat_weight(self) -> Weight | None:
        return None if not self.fat_percent else self.weight * self.fat_percent

    @property
    def muscle_weight(self) -> Weight | None:
        return None if not self.muscle_percent else self.weight * self.muscle_percent
