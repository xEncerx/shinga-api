from ..base_parser import *


class MalParser(BaseParserProvider):
    @staticmethod
    def parse(data: dict[str, Any]) -> Title:
        return Title(
            id=f"{SourceProvider.MAL.name}|{data['mal_id']}",
            cover=TitleCover(
                url=data["images"]["webp"]["image_url"],
                small_url=data["images"]["webp"]["small_image_url"],
                large_url=data["images"]["webp"]["large_image_url"],
            ),
            name_en=data["title"],
            name_ru=None,
            alt_names=data["title_synonyms"],
            type_=TitleType(data["type"].lower()),
            chapters=data["chapters"] or 0,
            volumes=data["volumes"] or 0,
            status=TitleStatus(data["status"].lower()),
            date=TitleReleaseTime(
                from_=data["published"]["from"],
                to=data["published"].get("to", None),
            ),
            rating=data["score"] or 0.0,
            scored_by=data["scored_by"] or 0,
            popularity=data["popularity"] or 0,
            favorites=data["favorites"] or 0,
            description=TitleDescription(en=data.get("synopsis", ""), ru=None),
            authors=[author["name"] for author in data.get("authors", [])],
            genres=[
                genre
                for key in ("genres", "themes")
                for item in data.get(key, [])
                if (genre := Genre.get(item["name"])) is not None
            ],
            source_provider=SourceProvider.MAL,
            source_id=str(data["mal_id"]),
        )

    @staticmethod
    def parse_page(data: dict[str, Any]) -> TitlePagination:
        return TitlePagination(
            pagination=Pagination(**data["pagination"]),
            data=[MalParser.parse(item) for item in data["data"]],
        )
