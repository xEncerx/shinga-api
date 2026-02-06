from src.core import logger
from ..base_parser import *


class AniListParser(BaseParser):
    @staticmethod
    def parse_title(data: dict) -> SourceTitleData:
        source_metadata = SourceMetadata(
            source=Source.ANILIST,
            external_id=str(data["id"]),
            source_url=data.get("siteUrl"),
        )

        rating, scored_by = AniListParser._calculate_rating_stats(
            data.get("stats", {}).get("scoreDistribution", [])
        )
        ci = data["coverImage"]
        staff = data["staff"]["edges"]

        title_data = TitleData(
            mal_id=data.get("idMal"),
            name_en=data["title"]["userPreferred"] or data["title"]["english"],
            description_en=tag_remover(data["description"]),
            type=TitleType.MANGA,  # AniList client only have manga type
            status=AniListParser.convert_status(data["status"]),
            popularity=data["popularity"] or 0,
            chapters=data["chapters"] or 0,
            volumes=data["volumes"] or 0,
            favorites=data["favourites"] or 0,
            rating=rating or 0.0,
            scored_by=scored_by or 0,
            released_at=(
                AniListParser._parse_date_dict(x) if (x := data["startDate"]) else None
            ),
            ended_at=(
                AniListParser._parse_date_dict(x) if (x := data["endDate"]) else None
            ),
            genres=[
                genre
                for genre_name in data.get("genres", [])
                if (genre := AniListParser.convert_genre(genre_name))
            ],
            categories=[
                category
                for category_name in data["tags"]
                if (category := AniListParser.convert_category(category_name["name"]))
            ],
            authors=[i["node"]["name"]["full"] for i in staff],
            alt_names=data["synonyms"],
            cover=TitleCover(
                thumbnail=ci["medium"],
                original=ci["extraLarge"] or ci["large"],
            ),
        )

        return SourceTitleData(
            source_metadata=source_metadata,
            title_data=title_data,
        )

    @staticmethod
    def parse_page(data: dict) -> list[SourceTitleData]:
        parsed_titles = []
        for item in data["data"]["results"]["media"]:
            try:
                parsed_titles.append(AniListParser.parse_title(item))
            except (ValueError, KeyError) as e:
                logger.error(
                    f"Skipping AniList title id={item['id']}: {e}", exc_info=True
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error parsing AniList title id={item['id']}: {e}",
                    exc_info=True,
                )
                continue

        return parsed_titles

    # === Converters ===
    @staticmethod
    def convert_status(data: str) -> TitleStatus:
        return AniListParser._STATUS_MAPPING.get(data, TitleStatus.UNKNOWN)

    @staticmethod
    def convert_genre(data: str) -> TitleGenre | None:
        return AniListParser._GENRE_MAPPING.get(data)

    @staticmethod
    def convert_category(data: str) -> TitleCategory | None:
        return AniListParser._CATEGORY_MAPPING.get(data)

    # === Mapping Dictionaries ===
    _GENRE_MAPPING: dict[str, TitleGenre] = {
        "Action": TitleGenre.ACTION,
        "Adventure": TitleGenre.ADVENTURE,
        "Comedy": TitleGenre.COMEDY,
        "Drama": TitleGenre.DRAMA,
        "Ecchi": TitleGenre.ECCHI,
        "Fantasy": TitleGenre.FANTASY,
        "Hentai": TitleGenre.HENTAI,
        "Horror": TitleGenre.HORROR,
        "Mahou Shoujo": TitleGenre.MAHOU_SHOUJO,
        "Mecha": TitleGenre.MECHA,
        "Music": TitleGenre.MUSIC,
        "Mystery": TitleGenre.MYSTERY,
        "Psychological": TitleGenre.PSYCHOLOGICAL,
        "Romance": TitleGenre.ROMANCE,
        "Sci-Fi": TitleGenre.SCIENCE_FICTION,
        "Slice of Life": TitleGenre.SLICE_OF_LIFE,
        "Sports": TitleGenre.SPORTS,
        "Supernatural": TitleGenre.SUPERNATURAL,
        "Thriller": TitleGenre.THRILLER,
    }

    _CATEGORY_MAPPING: dict[str, TitleCategory] = {
        "4-koma": TitleCategory.YONKOMA,
        "Achromatic": TitleCategory.ACHROMATIC,
        "Achronological Order": TitleCategory.ACHRONOLOGICAL_ORDER,
        "Acrobatics": TitleCategory.ACROBATICS,
        "Acting": TitleCategory.ACTING,
        "Adoption": TitleCategory.ADOPTION,
        "Advertisement": TitleCategory.ADVERTISEMENT,
        "Afterlife": TitleCategory.AFTERLIFE,
        "Age Gap": TitleCategory.AGE_GAP,
        "Age Regression": TitleCategory.AGE_REGRESSION,
        "Agender": TitleCategory.AGENDER,
        "Agriculture": TitleCategory.AGRICULTURE,
        "Ahegao": TitleCategory.AHEGAO,
        "Airsoft": TitleCategory.AIRSOFT,
        "Alchemy": TitleCategory.ALCHEMY,
        "Aliens": TitleCategory.ALIENS,
        "Alternate Universe": TitleCategory.ALTERNATE_UNIVERSE,
        "American Football": TitleCategory.AMERICAN_FOOTBALL,
        "Amnesia": TitleCategory.AMNESIA,
        "Amputation": TitleCategory.AMPUTATION,
        "Anachronism": TitleCategory.ANACHRONISM,
        "Anal Sex": TitleCategory.ANAL_SEX,
        "Ancient China": TitleCategory.ANCIENT_CHINA,
        "Angels": TitleCategory.ANGELS,
        "Animals": TitleCategory.ANIMALS,
        "Anthology": TitleCategory.ANTHOLOGY,
        "Anthropomorphism": TitleCategory.ANTHROPOMORPHIC,
        "Anti-Hero": TitleCategory.ANTIHERO,
        "Archery": TitleCategory.ARCHERY,
        "Armpits": TitleCategory.ARMPITS,
        "Aromantic": TitleCategory.AROMANTIC,
        "Arranged Marriage": TitleCategory.ARRANGED_MARRIAGE,
        "Artificial Intelligence": TitleCategory.ARTIFICIAL_INTELLIGENCE,
        "Asexual": TitleCategory.ASEXUAL,
        "Ashikoki": TitleCategory.ASHIKOKI,
        "Asphyxiation": TitleCategory.ASPHYXIATION,
        "Assassins": TitleCategory.ASSASSINS,
        "Astronomy": TitleCategory.ASTRONOMY,
        "Athletics": TitleCategory.ATHLETICS,
        "Augmented Reality": TitleCategory.AUGMENTED_REALITY,
        "Autobiographical": TitleCategory.AUTOBIOGRAPHICAL,
        "Aviation": TitleCategory.AVIATION,
        "Badminton": TitleCategory.BADMINTON,
        "Ballet": TitleCategory.BALLET,
        "Band": TitleCategory.BAND,
        "Bar": TitleCategory.BAR,
        "Baseball": TitleCategory.BASEBALL,
        "Basketball": TitleCategory.BASKETBALL,
        "Battle Royale": TitleCategory.BATTLE_ROYALE,
        "Biographical": TitleCategory.BIOGRAPHICAL,
        "Bisexual": TitleCategory.BISEXUAL,
        "Blackmail": TitleCategory.BLACKMAIL,
        "Board Game": TitleCategory.BOARD_GAME,
        "Boarding School": TitleCategory.BOARDING_SCHOOL,
        "Body Horror": TitleCategory.BODY_HORROR,
        "Body Image": TitleCategory.BODY_IMAGE,
        "Body Swapping": TitleCategory.BODY_SWAPPING,
        "Bondage": TitleCategory.BONDAGE,
        "Boobjob": TitleCategory.BOOBJOB,
        "Bowling": TitleCategory.BOWLING,
        "Boxing": TitleCategory.BOXING,
        "Boys' Love": TitleCategory.BOYS_LOVE,
        "Bullying": TitleCategory.BULLYING,
        "Butler": TitleCategory.BUTLER,
        "Calligraphy": TitleCategory.CALLIGRAPHY,
        "Camping": TitleCategory.CAMPING,
        "Cannibalism": TitleCategory.CANNIBALISM,
        "Card Battle": TitleCategory.CARD_BATTLE,
        "Cars": TitleCategory.CARS,
        "Centaur": TitleCategory.CENTAUR,
        "Cervix Penetration": TitleCategory.CERVIX_PENETRATION,
        "CGI": TitleCategory.CGI,
        "Cheerleading": TitleCategory.CHEERLEADING,
        "Cheating": TitleCategory.CHEATING,
        "Chibi": TitleCategory.CHIBI,
        "Chimera": TitleCategory.CHIMERA,
        "Chuunibyou": TitleCategory.CHUUNIBYOU,
        "Circus": TitleCategory.CIRCUS,
        "Class Struggle": TitleCategory.CLASS_STRUGGLE,
        "Classic Literature": TitleCategory.CLASSIC_LITERATURE,
        "Classical Music": TitleCategory.CLASSICAL_MUSIC,
        "Clone": TitleCategory.CLONE,
        "Coastal": TitleCategory.COASTAL,
        "Cohabitation": TitleCategory.COHABITATION,
        "College": TitleCategory.COLLEGE,
        "Coming of Age": TitleCategory.COMING_OF_AGE,
        "Conspiracy": TitleCategory.CONSPIRACY,
        "Cosmic Horror": TitleCategory.COSMIC_HORROR,
        "Cosplay": TitleCategory.COSPLAY,
        "Cowboys": TitleCategory.COWBOYS,
        "Creature Taming": TitleCategory.CREATURE_TAMING,
        "Crime": TitleCategory.CRIME,
        "Criminal Organization": TitleCategory.CRIMINAL_ORGANIZATION,
        "Crossdressing": TitleCategory.CROSSDRESSING,
        "Crossover": TitleCategory.CROSSOVER,
        "Cult": TitleCategory.CULT,
        "Cultivation": TitleCategory.CULTIVATION,
        "Cumflation": TitleCategory.CUMFLATION,
        "Cunnilingus": TitleCategory.CUNNILINGUS,
        "Curses": TitleCategory.CURSES,
        "Cute Boys Doing Cute Things": TitleCategory.CBDCT,
        "Cute Girls Doing Cute Things": TitleCategory.CGDCT,
        "Cyberpunk": TitleCategory.STEAMPUNK,
        "Cyborg": TitleCategory.CYBORG,
        "Cycling": TitleCategory.CYCLING,
        "Dancing": TitleCategory.DANCING,
        "Death Game": TitleCategory.DEATH_GAME,
        "Deepthroat": TitleCategory.DEEPTHROAT,
        "Defloration": TitleCategory.DEFLORATION,
        "Delinquents": TitleCategory.DELINQUENTS,
        "Demons": TitleCategory.DEMONS,
        "Denpa": TitleCategory.DENPA,
        "Desert": TitleCategory.DESERT,
        "Detective": TitleCategory.DETECTIVE,
        "DILF": TitleCategory.DILF,
        "Dinosaurs": TitleCategory.DINOSAURS,
        "Disability": TitleCategory.DISABILITY,
        "Dissociative Identities": TitleCategory.DISSOCIATIVE_IDENTITIES,
        "Double Penetration": TitleCategory.DOUBLE_PENETRATION,
        "Dragons": TitleCategory.DRAGONS,
        "Drawing": TitleCategory.DRAWING,
        "Drugs": TitleCategory.DRUGS,
        "Dullahan": TitleCategory.DULLAHAN,
        "Dungeon": TitleCategory.DUNGEONS,
        "Dystopian": TitleCategory.DYSTOPIA,
        "Eco-Horror": TitleCategory.ECO_HORROR,
        "E-Sports": TitleCategory.ESPORTS,
        "Economics": TitleCategory.ECONOMICS,
        "Educational": TitleCategory.EDUCATIONAL,
        "Elderly Protagonist": TitleCategory.ELDERLY_PROTAGONIST,
        "Elf": TitleCategory.ELF,
        "Ensemble Cast": TitleCategory.ENSEMBLE_CAST,
        "Environmental": TitleCategory.ENVIRONMENTAL,
        "Episodic": TitleCategory.EPISODIC,
        "Ero Guro": TitleCategory.ERO_GURO,
        "Erotic Piercings": TitleCategory.EROTIC_PIERCINGS,
        "Espionage": TitleCategory.ESPIONAGE,
        "Estranged Family": TitleCategory.ESTRANGED_FAMILY,
        "Exhibitionism": TitleCategory.EXHIBITIONISM,
        "Exorcism": TitleCategory.EXORCISM,
        "Facial": TitleCategory.FACIAL,
        "Fairy": TitleCategory.FAIRY,
        "Fairy Tale": TitleCategory.FAIRY_TALE,
        "Fake Relationship": TitleCategory.FAKE_RELATIONSHIP,
        "Family Life": TitleCategory.FAMILY_LIFE,
        "Fashion": TitleCategory.FASHION,
        "Female Harem": TitleCategory.FEMALE_HAREM,
        "Female Protagonist": TitleCategory.FEMALE_PROTAGONIST,
        "Feet": TitleCategory.FEET,
        "Fellatio": TitleCategory.FELLATIO,
        "Femboy": TitleCategory.FEMBOY,
        "Femdom": TitleCategory.FEMDOM,
        "Fencing": TitleCategory.FENCING,
        "Filmmaking": TitleCategory.FILMMAKING,
        "Fingering": TitleCategory.FINGERING,
        "Firefighters": TitleCategory.FIREFIGHTERS,
        "Fishing": TitleCategory.FISHING,
        "Fisting": TitleCategory.FISTING,
        "Fitness": TitleCategory.FITNESS,
        "Flash": TitleCategory.FLASH,
        "Flat Chest": TitleCategory.FLAT_CHEST,
        "Food": TitleCategory.COOKING,
        "Football": TitleCategory.FOOTBALL,
        "Foreign": TitleCategory.FOREIGN,
        "Found Family": TitleCategory.FOUND_FAMILY,
        "Fugitive": TitleCategory.FUGITIVE,
        "Full CGI": TitleCategory.FULL_CGI,
        "Full Color": TitleCategory.FULL_COLOR,
        "Futanari": TitleCategory.FUTANARI,
        "Gambling": TitleCategory.GAMBLING,
        "Gangs": TitleCategory.GANGS,
        "Gender Bending": TitleCategory.GENDER_BENDING,
        "Ghost": TitleCategory.GHOST,
        "Go": TitleCategory.GO,
        "Goblin": TitleCategory.GOBLIN,
        "Gods": TitleCategory.GODS,
        "Golf": TitleCategory.GOLF,
        "Gore": TitleCategory.GORE,
        "Group Sex": TitleCategory.GROUP_SEX,
        "Guns": TitleCategory.GUNS,
        "Gyaru": TitleCategory.GYARU,
        "Hair Pulling": TitleCategory.HAIR_PULLING,
        "Handball": TitleCategory.HANDBALL,
        "Handjob": TitleCategory.HANDJOB,
        "Henshin": TitleCategory.HENSHIN,
        "Heterosexual": TitleCategory.HAREM,
        "Hikikomori": TitleCategory.HIKIKOMORI,
        "Hip-hop Music": TitleCategory.HIP_HOP_MUSIC,
        "Historical": TitleCategory.HISTORICAL,
        "Homeless": TitleCategory.HOMELESS,
        "Horticulture": TitleCategory.HORTICULTURE,
        "Human Pet": TitleCategory.HUMAN_PET,
        "Hypersexuality": TitleCategory.HYPERSEXUALITY,
        "Ice Skating": TitleCategory.ICE_SKATING,
        "Idol": TitleCategory.IDOLS_FEMALE,
        "Incest": TitleCategory.INCEST,
        "Indigenous Cultures": TitleCategory.HISTORICAL,
        "Inn": TitleCategory.INN,
        "Inseki": TitleCategory.INSEKI,
        "Isekai": TitleCategory.ISEKAI,
        "Irrumatio": TitleCategory.IRRUMATIO,
        "Iyashikei": TitleCategory.IYASHIKEI,
        "Jazz Music": TitleCategory.JAZZ_MUSIC,
        "Josei": TitleCategory.JOSEI,
        "Judo": TitleCategory.JUDO,
        "Kabuki": TitleCategory.KABUKI,
        "Kaiju": TitleCategory.KAIJU,
        "Karuta": TitleCategory.KARUTA,
        "Kemonomimi": TitleCategory.KEMONOMIMI,
        "Kids": TitleCategory.KIDS,
        "Kingdom Management": TitleCategory.KINGDOM_MANAGEMENT,
        "Konbini": TitleCategory.KONBINI,
        "Kuudere": TitleCategory.KUUDERE,
        "Lactation": TitleCategory.LACTATION,
        "Lacrosse": TitleCategory.LACROSSE,
        "Language Barrier": TitleCategory.LANGUAGE_BARRIER,
        "Large Breasts": TitleCategory.LARGE_BREASTS,
        "LGBTQ+ Themes": TitleCategory.LGBTQ_THEMES,
        "Long Strip": TitleCategory.LONG_STRIP,
        "Lost Civilization": TitleCategory.LOST_CIVILIZATION,
        "Love Triangle": TitleCategory.LOVE_TRIANGLE,
        "Mafia": TitleCategory.MAFIA,
        "Magic": TitleCategory.MAGIC,
        "Mahjong": TitleCategory.MAHJONG,
        "Maids": TitleCategory.MAIDS,
        "Makeup": TitleCategory.MAKEUP,
        "Male Harem": TitleCategory.MALE_HAREM,
        "Male Pregnancy": TitleCategory.MALE_PREGNANCY,
        "Male Protagonist": TitleCategory.MALE_PROTAGONIST,
        "Manzai": TitleCategory.MANZAI,
        "Marriage": TitleCategory.MARRIAGE,
        "Martial Arts": TitleCategory.MARTIAL_ARTS,
        "Masochism": TitleCategory.MASOCHISM,
        "Matchmaking": TitleCategory.MATCHMAKING,
        "Masturbation": TitleCategory.MASTURBATION,
        "Matriarchy": TitleCategory.MATRIARCHY,
        "Mating Press": TitleCategory.MATING_PRESS,
        "Medicine": TitleCategory.MEDICAL,
        "Medieval": TitleCategory.MEDIEVAL,
        "Memory Manipulation": TitleCategory.MEMORY_MANIPULATION,
        "Mermaid": TitleCategory.MERMAID,
        "Meta": TitleCategory.META,
        "Metal Music": TitleCategory.METAL_MUSIC,
        "MILF": TitleCategory.MILF,
        "Military": TitleCategory.MILITARY,
        "Mixed Gender Harem": TitleCategory.MIXED_GENDER_HAREM,
        "Mixed Media": TitleCategory.MIXED_MEDIA,
        "Modeling": TitleCategory.MODELING,
        "Monster Boy": TitleCategory.MONSTER_BOY,
        "Monster Girl": TitleCategory.MONSTER_GIRL,
        "Mopeds": TitleCategory.MOPEDS,
        "Motorcycles": TitleCategory.MOTORCYCLES,
        "Mountaineering": TitleCategory.MOUNTAINEERING,
        "Musical Theater": TitleCategory.MUSICAL_THEATER,
        "Mythology": TitleCategory.MYTHOLOGY,
        "Nakadashi": TitleCategory.NAKADASHI,
        "Natural Disaster": TitleCategory.NATURAL_DISASTER,
        "Necromancy": TitleCategory.NECROMANCY,
        "Nekomimi": TitleCategory.NEKOMIMI,
        "Netorare": TitleCategory.NETORARE,
        "Netorase": TitleCategory.NETORASE,
        "Netori": TitleCategory.NETORI,
        "Ninja": TitleCategory.NINJA,
        "No Dialogue": TitleCategory.NO_DIALOGUE,
        "Noir": TitleCategory.NOIR,
        "Non-fiction": TitleCategory.NON_FICTION,
        "Nudity": TitleCategory.NUDITY,
        "Nun": TitleCategory.NUN,
        "Office": TitleCategory.OFFICE,
        "Office Lady": TitleCategory.OFFICE_WORKERS,
        "Oiran": TitleCategory.OIRAN,
        "Ojou-sama": TitleCategory.OJOU_SAMA,
        "Omegaverse": TitleCategory.OMEGAVERSE,
        "Orphan": TitleCategory.ORPHAN,
        "Otaku Culture": TitleCategory.OTAKU_CULTURE,
        "Outdoor Activities": TitleCategory.OUTDOOR_ACTIVITIES,
        "Oyakodon": TitleCategory.OYAKODON,
        "Pandemic": TitleCategory.PANDEMIC,
        "Parenthood": TitleCategory.PARENTHOOD,
        "Parkour": TitleCategory.PARKOUR,
        "Parody": TitleCategory.PARODY,
        "Performing Arts": TitleCategory.PERFORMING_ARTS,
        "Pet Play": TitleCategory.PET_PLAY,
        "Philosophy": TitleCategory.PHILOSOPHY,
        "Photography": TitleCategory.PHOTOGRAPHY,
        "Pirates": TitleCategory.PIRATES,
        "Poker": TitleCategory.POKER,
        "Police": TitleCategory.POLICE,
        "Politics": TitleCategory.POLITICS,
        "Polyamorous": TitleCategory.POLYAMOROUS,
        "Post-Apocalyptic": TitleCategory.POST_APOCALYPTIC,
        "POV": TitleCategory.PSYCHOLOGICAL,
        "Pregnancy": TitleCategory.PREGNANCY,
        "Primarily Adult Cast": TitleCategory.PRIMARILY_ADULT_CAST,
        "Primarily Animal Cast": TitleCategory.PRIMARILY_ANIMAL_CAST,
        "Primarily Child Cast": TitleCategory.PRIMARILY_CHILD_CAST,
        "Primarily Female Cast": TitleCategory.PRIMARILY_FEMALE_CAST,
        "Primarily Male Cast": TitleCategory.PRIMARILY_MALE_CAST,
        "Primarily Teen Cast": TitleCategory.PRIMARILY_TEEN_CAST,
        "Prison": TitleCategory.PRISON,
        "Prostitution": TitleCategory.PROSTITUTION,
        "Proxy Battle": TitleCategory.PROXY_BATTLE,
        "Psychosexual": TitleCategory.PSYCHOSEXUAL,
        "Public Sex": TitleCategory.PUBLIC_SEX,
        "Puppetry": TitleCategory.PUPPETRY,
        "Rakugo": TitleCategory.RAKUGO,
        "Rape": TitleCategory.RAPE,
        "Real Robot": TitleCategory.REAL_ROBOT,
        "Rehabilitation": TitleCategory.REHABILITATION,
        "Reincarnation": TitleCategory.REINCARNATION,
        "Religion": TitleCategory.RELIGION,
        "Rescue": TitleCategory.RESCUE,
        "Restaurant": TitleCategory.RESTAURANT,
        "Revenge": TitleCategory.REVENGE,
        "Reverse Isekai": TitleCategory.REVERSE_ISEKAI,
        "Rimjob": TitleCategory.RIMJOB,
        "Robots": TitleCategory.ROBOTS,
        "Rock Music": TitleCategory.ROCK_MUSIC,
        "Rotoscoping": TitleCategory.ROTOSCOPING,
        "Royal Affairs": TitleCategory.ROYAL_AFFAIRS,
        "Rugby": TitleCategory.RUGBY,
        "Rural": TitleCategory.RURAL,
        "Sadism": TitleCategory.SADISM,
        "Samurai": TitleCategory.SAMURAI,
        "Satire": TitleCategory.SATIRE,
        "Scat": TitleCategory.SCAT,
        "School": TitleCategory.SCHOOL,
        "School Club": TitleCategory.SCHOOL_CLUB,
        "Scissoring": TitleCategory.SCISSORING,
        "Scuba Diving": TitleCategory.SCUBA_DIVING,
        "Seinen": TitleCategory.SEINEN,
        "Sex Toys": TitleCategory.SEX_TOYS,
        "Shapeshifting": TitleCategory.SHAPESHIFTING,
        "Shimaidon": TitleCategory.SHIMAIDON,
        "Ships": TitleCategory.SHIPS,
        "Shogi": TitleCategory.SHOGI,
        "Shoujo": TitleCategory.SHOUJO,
        "Shounen": TitleCategory.SHOUNEN,
        "Shrine Maiden": TitleCategory.SHRINE_MAIDEN,
        "Skateboarding": TitleCategory.SKATEBOARDING,
        "Skeleton": TitleCategory.SKELETON,
        "Slapstick": TitleCategory.SLAPSTICK,
        "Slavery": TitleCategory.SLAVERY,
        "Snowscape": TitleCategory.SNOWSCAPE,
        "Software Development": TitleCategory.SOFTWARE_DEVELOPMENT,
        "Space": TitleCategory.SPACE,
        "Space Opera": TitleCategory.SPACE_OPERA,
        "Spearplay": TitleCategory.SPEARPLAY,
        "Squirting": TitleCategory.SQUIRTING,
        "Steampunk": TitleCategory.STEAMPUNK,
        "Stop Motion": TitleCategory.STOP_MOTION,
        "Strategy Game": TitleCategory.STRATEGY_GAME,
        "Succubus": TitleCategory.SUCCUBUS,
        "Suicide": TitleCategory.SUICIDE,
        "Sumata": TitleCategory.SUMATA,
        "Sumo": TitleCategory.SUMO,
        "Super Power": TitleCategory.SUPER_POWER,
        "Super Robot": TitleCategory.SUPER_ROBOT,
        "Superhero": TitleCategory.SUPERHEROES,
        "Surfing": TitleCategory.SURFING,
        "Surreal Comedy": TitleCategory.SURREAL_COMEDY,
        "Survival": TitleCategory.SURVIVAL,
        "Swapping ": TitleCategory.SWAPPING,
        "Sweat": TitleCategory.SWEAT,
        "Swimming": TitleCategory.SWIMMING,
        "Swordplay": TitleCategory.SWORDPLAY,
        "Table Tennis": TitleCategory.TABLE_TENNIS,
        "Tanks": TitleCategory.TANKS,
        "Tanned Skin": TitleCategory.TANNED_SKIN,
        "Teacher": TitleCategory.TEACHER,
        "Teens' Love": TitleCategory.TEENS_LOVE,
        "Tennis": TitleCategory.TENNIS,
        "Tentacles": TitleCategory.TENTACLES,
        "Terrorism": TitleCategory.TERRORISM,
        "Threesome": TitleCategory.THREESOME,
        "Time Loop": TitleCategory.TIME_LOOP,
        "Time Manipulation": TitleCategory.TIME_MANIPULATION,
        "Time Skip": TitleCategory.TIME_SKIP,
        "Tokusatsu": TitleCategory.TOKUSATSU,
        "Tomboy": TitleCategory.TOMBOY,
        "Torture": TitleCategory.TORTURE,
        "Tragedy": TitleCategory.TRAGEDY,
        "Traditional Games": TitleCategory.TRADITIONAL_GAMES,
        "Trains": TitleCategory.TRAINS,
        "Transgender": TitleCategory.TRANSGENDER,
        "Travel": TitleCategory.TRAVEL,
        "Triads": TitleCategory.TRIADS,
        "Tsundere": TitleCategory.TSUNDERE,
        "Twins": TitleCategory.TWINS,
        "Unrequited Love": TitleCategory.UNREQUITED_LOVE,
        "Urban": TitleCategory.URBAN,
        "Urban Fantasy": TitleCategory.URBAN_FANTASY,
        "Vampire": TitleCategory.VAMPIRE,
        "Vertical Video": TitleCategory.VERTICAL_VIDEO,
        "Veterinarian": TitleCategory.VETERINARIAN,
        "Video Games": TitleCategory.VIDEO_GAME,
        "Vikings": TitleCategory.VIKINGS,
        "Villainess": TitleCategory.VILLAINESS,
        "Virginity": TitleCategory.VIRGINITY,
        "Virtual World": TitleCategory.VIRTUAL_WORLD,
        "Vocal Synth": TitleCategory.VOCAL_SYNTH,
        "Volleyball": TitleCategory.VOLLEYBALL,
        "Vore": TitleCategory.VORE,
        "Voyeur": TitleCategory.VOYEUR,
        "VTuber": TitleCategory.VTUBER,
        "War": TitleCategory.WAR,
        "Watersports": TitleCategory.WATERSPORTS,
        "Werewolf": TitleCategory.WEREWOLF,
        "Western": TitleCategory.WESTERN,
        "Wilderness": TitleCategory.WILDERNESS,
        "Witch": TitleCategory.WITCH,
        "Work": TitleCategory.WORKPLACE,
        "Wrestling": TitleCategory.WRESTLING,
        "Writing": TitleCategory.WRITING,
        "Wuxia": TitleCategory.WUXIA,
        "Yakuza": TitleCategory.YAKUZA,
        "Yandere": TitleCategory.YANDERE,
        "Youkai": TitleCategory.YOUKAI,
        "Yuri": TitleCategory.YURI,
        "Zombie": TitleCategory.ZOMBIES,
        "Zoophilia": TitleCategory.ZOOPHILIA,
    }

    _STATUS_MAPPING: dict[str, TitleStatus] = {
        "FINISHED": TitleStatus.FINISHED,
        "RELEASING": TitleStatus.ONGOING,
        "NOT_YET_RELEASED": TitleStatus.ANONS,
        "CANCELLED": TitleStatus.DISCONTINUED,
        "HIATUS": TitleStatus.FROZEN,
    }

    # === Utilities ===
    @staticmethod
    def _calculate_rating_stats(score_distribution: list[dict]) -> tuple[float, int]:
        """
        Calculate rating (0-10) and scored_by from score distribution.

        Args:
            score_distribution: List of dicts with 'score' and 'amount' keys

        Returns:
            Tuple of (rating, scored_by)
        """
        if not score_distribution:
            return 0.0, 0

        total_score = 0
        total_amount = 0

        for item in score_distribution:
            score = item["score"]
            amount = item["amount"]
            total_score += score * amount
            total_amount += amount

        if total_amount == 0:
            return 0.0, 0

        rating = (total_score / total_amount) / 10

        return round(rating, 2), total_amount

    @staticmethod
    def _parse_date_dict(data: dict[str, int | None]) -> datetime | None:
        year = data.get("year")
        month = data.get("month") or 1
        day = data.get("day") or 1

        if year is None:
            return None

        return datetime(year, month, day).replace(tzinfo=None)
