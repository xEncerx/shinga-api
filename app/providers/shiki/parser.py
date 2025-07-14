from typing import Any
from app.domain.models import TitlePagination
from ..base_parser import *


class ShikiParser(BaseParserProvider):
    @staticmethod
    def parse(data: dict[str, Any]) -> Title:
        id_ = (
            f"{SourceProvider.MAL.name}|{data['malId']}"
            if data.get("malId")
            else f"{SourceProvider.SHIKIMORI.name}|{data['id']}"
        )

        return Title(
            id=id_,
            cover=TitleCover(
                url=data["poster"]["originalUrl"] if data["poster"] else None,
                small_url=None,
                large_url=None,
            ),
            name_en=data["english"],
            name_ru=data.get("russian"),
            alt_names=data.get("synonyms", []) or [],
            type_=TypeConverter.from_shiki(data["kind"]),
            chapters=data.get("chapters", 0) or 0,
            volumes=data.get("volumes", 0) or 0,
            status=StatusConverter.from_shiki(data["status"]),
            date=TitleReleaseTime(
                from_=f"{date}T00:00:00+00:00" if (date := data["airedOn"]["date"]) else None,
                to=f"{date}T00:00:00+00:00" if (date := data["releasedOn"]["date"]) else None,
            ),
            rating=data.get("score", 0.0) or 0.0,
            scored_by=sum(i["count"] for i in data["scoresStats"]),
            favorites=sum(i["count"] for i in data["statusesStats"]),
            description=TitleDescription(en=None, ru=data.get("description")),
            authors=[
                i.get("person", {}).get("name", "unknown")
                for i in data.get("personRoles", [])
            ],
            genres=[
                genre
                for item in data.get("genres", [])
                if (genre := TitleGenre.get(item["name"])) is not None
            ],
            source_provider=SourceProvider.SHIKIMORI,
            source_id=str(data["id"]),
        )

    @classmethod
    def parse_page(cls, data: dict[str, Any]) -> TitlePagination:
        return TitlePagination(
            data=[cls.parse(item) for item in data["data"]["mangas"]],
        )
