from aiogtrans import Translator as ATG
from openai import AsyncOpenAI
from httpx import AsyncClient
from typing import Any

from app.core import (
    logger,
    settings,
    Language,
    TranslatorProvider,
)

DEFAULT_PROMPT = """
<prompt>
  <context>
    Вы профессиональный переводчик азиатской литературы (манги, манхвы, маньхуа, новелл и т.д.).  
    Ваша задача — переводить только предоставленный текст на {target_lang}, избегая пояснений и технических комментариев.  
    Стиль: естественный, адаптированный под целевую аудиторию, с сохранением культурных отсылок.  
    Если известен официальный перевод — используйте его. Если нет — подберите максимально точный и идиоматичный вариант.  
  </context>

  <rules>
    <title_translation>
      <requirement>Название должно звучать естественно в {target_lang}, сохраняя смысл или эмоцию оригинала.</requirement>
      <example input="FFF-Class Trashero" output="Ублюдок FFF-ранга"/>  
      <example input="Solo Leveling" output="Поднятие уровня в одиночку"/>  
    </title_translation>
    <description_translation>
      <requirement>Описание переводится литературно, с адаптацией реалий (например, " cultivation " → "путь совершенствования").</requirement>
      <example input="A hero summoned to another world rebels against the clichés." output="Призванный в другой мир герой бросает вызов клише."/>  
    </description_translation>
  </rules>

  <output_format>
    <strict>Только готовый текст, без кавычек, пояснений или меток.</strict>
  </output_format>

  <task>
    <input_type>title|description</input_type>
    <text>Текст для перевода</text>
    <target_lang>{target_lang}</target_lang>
  </task>
</prompt>
"""


class Translator:
    def __init__(
        self,
        base_url: str = settings.OPENAI_API_BASE,
        api_model: str = settings.OPENAI_API_MODEL,
    ) -> None:
        self._model = api_model
        self._base_url = base_url

    async def translate(
        self,
        text: str,
        openai_api_key: str | None = None,
        target_lang: Language = Language.RU,
        temperature: float = 0.2,
        prompt: str = DEFAULT_PROMPT,
        proxy: str | None = None,
        provider: TranslatorProvider = TranslatorProvider.OPENAI,
    ) -> str:
        """
        Translate text using OpenAI's API.

        :param text: Text to translate.
        :param openai_api_key: OpenAI API key (used if provider is OPENAI).
        :param target_lang: Target language for translation.
        :param temperature: Sampling temperature for the model (0.0 - 1.0).
        :param prompt: Custom prompt for translation. Use `{target_lang}` in your prompt to provide target language
        :param proxy: Proxy URL for the OpenAI API request.
        :param provider: Translator provider to use (e.g., OPENAI, GOOGLE).
        :param kwargs: Additional parameters for the OpenAI API call.

        :return: Translated text.
        """
        if not text:
            return text

        try:
            match provider:
                case TranslatorProvider.OPENAI:
                    if not openai_api_key:
                        raise ValueError("OpenAI API key is required for OpenAI translation.")

                    return await self._openai_translate(
                        text=text,
                        target_lang=target_lang,
                        temperature=temperature,
                        openai_api_key=openai_api_key,
                        proxy=proxy,
                        prompt=prompt,
                    )
                case TranslatorProvider.GOOGLE:
                    return await self._google_translate(
                        text=text,
                        target_lang=target_lang,
                    )
                case _:
                    raise ValueError(f"Unsupported translator provider: {provider}")

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    async def _openai_translate(
        self,
        text: str,
        openai_api_key: str,
        target_lang: Language = Language.RU,
        proxy: str | None = None,
        temperature: float = 0.2,
        prompt: str = DEFAULT_PROMPT,
    ) -> str:
        async with AsyncOpenAI(
            api_key=openai_api_key,
            base_url=self._base_url,
            http_client=AsyncClient(
                proxy=proxy
            )
        ) as client:
            response = await client.chat.completions.create(
                model=self._model,
                temperature=temperature,
                messages=[
                    {
                        "role": "system",
                        "content": prompt.format(target_lang=target_lang.full),
                    },
                    {"role": "user", "content": text},
                ],
            )
            return response.choices[0].message.content or ""

    async def _google_translate(
        self,
        text: str,
        target_lang: Language = Language.RU,
    ) -> str:
        async with ATG() as client:
            response = await client.translate(
                text=text,
                dest=target_lang,
            )
            return response.text