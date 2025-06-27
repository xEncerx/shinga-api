from ..base_parser import *
from ...domain.services.translation import Translator, TranslatorProvider


class MalParser(BaseProviderParser):
    @staticmethod
    async def parse(data: dict[str, Any]) -> Title:
        return Title(
            id=data["mal_id"],
            cover=TitleCover(
                url=data["images"]["webp"]["image_url"],
                small_url=data["images"]["webp"]["small_image_url"],
                large_url=data["images"]["webp"]["large_image_url"],
            ),
            name_en=data["title"],
            name_ru=data["title"],
            # name_ru=await translator.translate(data["title"]),
            alt_names=data["title_synonyms"],
            type_=TitleType(data["type"].lower()),
            chapters=data.get("chapters", 0),
            volumes=data.get("volumes", 0),
            status=TitleStatus(data["status"].lower()),
            published=data["publishing"],
            date=TitleReleaseTime(
                from_=data["published"]["from"],
                to=data["published"].get("to", None),
            ),
            rating=data.get("score", 0.0),
            scored_by=data.get("scored_by", 0),
            popularity=data.get("popularity", 0),
            favorites=data.get("favorites", 0),
            description=TitleDescription(
                en=data.get("synopsis", ""),
                ru=data.get("synopsis", "")
                # ru=await translator.translate(data.get("synopsis", "")),
            ),
            authors=[author["name"] for author in data.get("authors", [])],
            genres=[
                TitleGenre(
                    en=genre["name"],
                    ru=genre["name"],
                    # ru=await translator.translate(
                    #     genre["name"],
                    #     provider=TranslatorProvider.GOOGLE,
                    # ),
                )
                for genre in data.get("genres", [])
            ],
        )
