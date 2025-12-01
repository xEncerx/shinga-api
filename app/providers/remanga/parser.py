from ..base_parser import *


class RemangaParser(BaseParserProvider):
    @staticmethod
    def parse(data: dict[str, Any]) -> TitleData:
        cover = data["cover"]

        return TitleData(
            source_id=data["dir"],
            source_provider=SourceProvider.REMANGA,
            source_url="https://remanga.org/manga/" + data["dir"],
            cover=TitleCoverData(
                url="https://remanga.org" + cover["mid"] if "mid" in cover else None,
                small_url=(
                    "https://remanga.org" + cover["low"] if "low" in cover else None
                ),
                large_url=(
                    "https://remanga.org" + cover["high"] if "high" in cover else None
                ),
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
            views=data.get("total_views") or 0,
            status=StatusConverter.from_remanga(data["status"]["name"]),
            date=TitleReleaseDateData(
                from_=(
                    f"{date}-01-01T00:00:00+00:00"
                    if (date := data["issue_year"])
                    else None
                ),
            ),
            rating=float(data["avg_rating"] or 0),
            scored_by=data.get("count_rating") or 0,
            favorites=data.get("count_bookmarks") or 0,
            description=TitleDescriptionData(
                en=None,
                ru=tag_remover(desc) if (desc := data.get("description")) else None,
            ),
            genres=[
                x
                for genre in data["genres"]
                if genre and (x := TitleGenre.get(ru=genre["name"]))
            ],
        )

    @classmethod
    def parse_page(cls, data: dict[str, Any]) -> TitlePagination[TitleData]:
        parsed_titles = []
        for item in data["results"]:
            try:
                parsed_titles.append(cls.parse(item))
            except (ValueError, KeyError) as e:
                logger.warning(
                    f"Skipping Remanga title slug={item.get('dir', 'unknown')}: {e}"
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error parsing Remanga title slug={item.get('dir', 'unknown')}: {e}",
                    exc_info=True,
                )
                continue

        return TitlePagination[TitleData](data=parsed_titles)
