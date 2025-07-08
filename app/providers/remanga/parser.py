from app.utils import tag_remover
from ..base_parser import *


class RemangaParser(BaseParserProvider):
    @staticmethod
    def parse(data: dict[str, Any]) -> Title:
        return Title(
            id=f"{SourceProvider.REMANGA.name}|{data['id']}",
            cover=TitleCover(
                url="https://remanga.org" + data["cover"]["mid"],
                small_url="https://remanga.org" + data["cover"]["low"],
                large_url="https://remanga.org" + data["cover"]["high"],
            ),
            name_en=data["secondary_name"],
            name_ru=data["main_name"],
            alt_names=(
                [name for i in data["another_name"].split("/") if (name := i.strip())]
                if data.get("another_name")
                else []
            ),
            type_=TypeConverter.from_remanga(data["type"]["name"]),
            chapters=data.get("count_chapters") or 0,
            volumes=0,  # Remanga does not provide volume count
            views=data.get("total_views") or 0,
            status=StatusConverter.from_remanga(data["status"]["name"]),
            date=TitleReleaseTime(
                from_=(
                    f"{date}-01-01T00:00:00+00:00"
                    if (date := data["issue_year"])
                    else None
                ),
                to=None,  # Remanga does not provide end date
            ),
            rating=float(data["avg_rating"] or 0),
            scored_by=data.get("count_rating") or 0,
            popularity=0,  # Remanga does not provide popularity
            favorites=data.get("count_bookmarks") or 0,
            description=TitleDescription(
                en=None,
                ru=tag_remover(desc) if (desc := data.get("description")) else None,
            ),
            authors=[],  # Remanga does not provide authors
            genres=[
                x
                for genre in data["genres"]
                if genre and (x := TitleGenre.get(ru=genre["name"]))
            ],
            source_provider=SourceProvider.REMANGA,
            source_id=data["dir"],
        )

    @classmethod
    def parse_page(cls, data: dict[str, Any]) -> TitlePagination:
        return TitlePagination(
            data=[cls.parse(item) for item in data["results"]],
        )
