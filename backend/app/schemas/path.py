from typing import Literal

from pydantic import BaseModel

NodeStatus = Literal["locked", "available", "completed"]
NodeType = Literal["lesson", "review", "chest", "assessment"]


class LessonSummaryRead(BaseModel):
    slug: str
    title: str


class NodeRead(BaseModel):
    key: str
    type: NodeType
    status: NodeStatus
    # El siguiente paso sugerido: la primera lección disponible que aún no se completa.
    is_current: bool
    lesson: LessonSummaryRead | None


class UnitRead(BaseModel):
    slug: str
    title: str
    nodes: list[NodeRead]


class SectionRead(BaseModel):
    slug: str
    title: str
    units: list[UnitRead]


class StageRead(BaseModel):
    slug: str
    title: str
    sections: list[SectionRead]


class PathRead(BaseModel):
    stages: list[StageRead]
