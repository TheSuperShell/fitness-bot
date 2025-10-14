import datetime
from typing import Annotated

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel

from config import config
from utils.time import current_timestamp_utc

Weight = Annotated[
    float,
    Field(
        ge=config.weight_lower_limit,
        le=config.weight_upper_limit,
        description="Body Weight, kg",
    ),
]
StatRatio = Annotated[
    float,
    Field(
        ge=0,
        le=1,
        description="Stat Ratio, %",
    ),
]
Height = Annotated[
    float,
    Field(
        ge=config.height_lower_limit,
        le=config.height_upper_limit,
        description="Height, cm",
    ),
]


class ParamRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="RESTRICT")
    created_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=current_timestamp_utc,
    )
    measured_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=current_timestamp_utc,
    )
    modified_at: datetime.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, onupdate=current_timestamp_utc
        ),
        default_factory=current_timestamp_utc,
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

    def __str__(self) -> str:
        return (
            f"weight: {self.weight:.0f};"
            + (f" fat weight: {self.fat_weight:.0f};" if self.fat_percent else "")
            + (
                f" muscle weight: {self.muscle_weight:.0f}"
                if self.muscle_percent
                else ""
            )
        )
