from ..base_parser import *

from typing import Any


class ShikimoriParser(BaseParserProvider):
    @staticmethod
    def parse(data: dict[str, Any]) -> TitleData:
        return TitleData(
            source_id=data["id"],
            source_provider=SourceProvider.SHIKIMORI,
            source_url=data.get("url"),
            mal_id=data.get("malId"),
            cover=TitleCoverData(
                url=data["poster"]["originalUrl"] if data["poster"] else None,
                small_url=None,
                large_url=None,
            ),
            name_en=data.get("english") or data.get("name"),
            name_ru=data.get("russian") or data.get("licenseNameRu"),
            alt_names=data.get("synonyms", []) or [],
            type_=TypeConverter.from_shikimori(data["kind"]),
            chapters=data.get("chapters", 0) or 0,
            volumes=data.get("volumes", 0) or 0,
            status=StatusConverter.from_shikimori(data["status"]),
            date=TitleReleaseDateData(
                from_=(
                    f"{date}T00:00:00+00:00"
                    if (date := data["airedOn"]["date"])
                    else None
                ),
                to=(
                    f"{date}T00:00:00+00:00"
                    if (date := data["releasedOn"]["date"])
                    else None
                ),
            ),
            rating=data.get("score", 0.0) or 0.0,
            scored_by=sum(i["count"] for i in data["scoresStats"]),
            favorites=sum(i["count"] for i in data["statusesStats"]),
            description=TitleDescriptionData(
                en=None,
                ru=tag_remover(
                    data.get("description"),
                ),
            ),
            authors=[
                i.get("person", {}).get("name", "unknown")
                for i in data.get("personRoles", [])
            ],
            genres=[
                genre
                for item in data.get("genres", [])
                if (genre := TitleGenre.get(item["name"])) is not None
            ],
        )

    @classmethod
    def parse_page(cls, data: dict[str, Any]) -> TitlePagination[TitleData]:
        parsed_titles = []
        for item in data["data"]["mangas"]:
            try:
                parsed_titles.append(cls.parse(item))
            except (ValueError, KeyError) as e:
                logger.warning(
                    f"Skipping Shikimori title id={item.get('id', 'unknown')}: {e}"
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error parsing Shikimori title id={item.get('id', 'unknown')}: {e}",
                    exc_info=True,
                )
                continue

        return TitlePagination[TitleData](data=parsed_titles)
