from ..base_parser import *


class MalParser(BaseParserProvider):
    @staticmethod
    def parse(data: dict[str, Any]) -> TitleData:
        return TitleData(
            source_id=str(data["mal_id"]),
            source_provider=SourceProvider.MAL,
            source_url=data["url"],
            cover=TitleCoverData(
                url=data["images"]["webp"]["image_url"],
                small_url=data["images"]["webp"]["small_image_url"],
                large_url=data["images"]["webp"]["large_image_url"],
            ),
            name_ru=None,
            name_en=data["title"],
            alt_names=data["title_synonyms"],
            type_=TypeConverter.from_mal(data["type"]),
            chapters=data["chapters"] or 0,
            volumes=data["volumes"] or 0,
            status=StatusConverter.from_mal(data["status"]),
            date=TitleReleaseDateData(
                from_=data["published"]["from"],
                to=data["published"].get("to", None),
            ),
            rating=data["score"] or 0.0,
            scored_by=data["scored_by"] or 0,
            popularity=data["popularity"] or 0,
            favorites=data["favorites"] or 0,
            description=TitleDescriptionData(
                en=tag_remover(data.get("synopsis", "")), ru=None
            ),
            authors=[author["name"] for author in data.get("authors", [])],
            genres=[
                genre
                for key in ("genres", "themes")
                for item in data.get(key, [])
                if (genre := TitleGenre.get(item["name"])) is not None
            ],
        )

    @classmethod
    def parse_page(cls, data: dict[str, Any]) -> TitlePagination[TitleData]:
        parsed_titles = []
        for item in data["data"]:
            try:
                parsed_titles.append(cls.parse(item))
            except (ValueError, KeyError) as e:
                logger.warning(
                    f"Skipping Mal title id={item.get('mal_id', 'unknown')}: {e}"
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error parsing Mal title id={item.get('mal_id', 'unknown')}: {e}",
                    exc_info=True,
                )
                continue

        return TitlePagination[TitleData](
            pagination=Pagination(**data["pagination"]),
            data=parsed_titles,
        )
