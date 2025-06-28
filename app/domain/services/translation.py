from app.utils import AsyncHttpClient
import json

from app.core import (
    Language,
    settings,
    logger,
)

DEFAULT_PROMPT = """
<prompt>
  <context>
    Вы профессиональный переводчик азиатской литературы (манги, манхвы, маньхуа, новелл и т.д.).  
    Ваша задача — переводить только предоставленный текст на {target_lang}, избегая пояснений и технических комментариев.  
    Стиль: естественный, адаптированный под целевую аудиторию, с сохранением культурных отсылок.  
    Если известен официальный перевод — используйте его. Если нет — подберите максимально точный и идиоматичный вариант.
  </context>

  <input_format>
    Принимается JSON-объект с полями:
    - title (необязательно): название для перевода
    - description (необязательно): описание для перевода
    Пример: {{"title": "FFF-Class Trashero", "description": "A hero summoned..."}}
  </input_format>

  <rules>
    <title>
      <requirement>Название должно звучать естественно в {target_lang}, сохраняя смысл или эмоцию оригинала</requirement>
      <example input="FFF-Class Trashero" output="Ублюдок FFF-ранга"/>  
      <example input="Solo Leveling" output="Поднятие уровня в одиночку"/>  
    </title>
    <description>
      <requirement>Описание переводится литературно, с адаптацией реалий (например, " cultivation " → "путь совершенствования").</requirement>
      <example input="Rebels against clichés" output="Бросает вызов клише"/>  
    </description>
  </rules>

  <output_format>
    Возвращайте ТОЛЬКО ТЕКСТ с переведенными полями БЕЗ ПОЯСНЕНИЙ, ЛИШНИХ СИМВОЛОВ и ФОРМАТИРОВАНИЯ:
    {{
      "title": "переведенное название",  // если было в запросе
      "description": "переведенное описание"  // если было в запросе
    }}
  </output_format>

  <task>
    <target_lang>{target_lang}</target_lang>
  </task>
</prompt>
"""


class Translator(AsyncHttpClient):
    """
    Translation service using OpenAI API.
    """
    def __init__(
        self,
        base_url: str = settings.OPENAI_API_BASE,
        api_model: str = settings.OPENAI_API_MODEL,
    ) -> None:
        """
        Initialize the Translator with OpenAI API configuration.
        
        Args:
            base_url (str): Base URL for OpenAI API. Defaults to settings.OPENAI_API_BASE.
            api_model (str): OpenAI model to use for translation. Defaults to settings.OPENAI_API_MODEL.
        """
        self._model = api_model
        super().__init__(
            base_url=base_url
        )

    async def __aenter__(self) -> "Translator":
        """
        Async context manager entry.
        
        Returns:
            Translator: Self instance for use in async with statements.
        """
        await super().__aenter__()
        return self

    async def translate(
        self,
        text: dict[str, str],
        openai_api_key: str | None = None,
        target_lang: Language = Language.RU,
        temperature: float = 0.2,
        prompt: str = DEFAULT_PROMPT,
        proxy: str | None = None,
    ) -> dict[str, str] | None:
        """
        Translate text content using OpenAI API.
        
        This method translates content to the target language.
        
        Args:
            text (dict[str, str]): Dictionary containing text to translate.
            openai_api_key (str | None): OpenAI API key for authentication. Required.
            target_lang (Language): Target language for translation. Defaults to Language.RU.
            temperature (float): Creativity parameter for translation (0.0-1.0). 
                Lower values produce more consistent translations. Defaults to 0.2.
            prompt (str): System prompt template for translation context. 
                Defaults to DEFAULT_PROMPT.
            proxy (str | None): Proxy URL for API requests. Defaults to None.
            
        Returns:
            result (dict[str, str] | None): Dictionary with translated text using same keys as input,
                or None if translation fails or response is empty.
                
        Raises:
            ValueError: If openai_api_key is not provided.
            Exception: If API request fails or other unexpected errors occur.
            
        Examples:
            >>> async with Translator() as translator:
            >>>     result = await translator.translate(
            ...         {"title": "Solo Leveling", "description": "A hunter becomes stronger"},
            ...         openai_api_key="sk-...",
            ...         target_lang=Language.RU
            ...     )
            >>> # Returns: {"title": "Поднятие уровня в одиночку", "description": "..."}
        """
        if not text: return text
        if not openai_api_key:
            raise ValueError("OpenAI API key is required for OpenAI translation.")
        
        try:
            response = await self.post(
                url="chat/completions",
                proxy=proxy,
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._model,
                    "messages": [
                        {
                            "role": "system",
                            "content": prompt.format(target_lang=target_lang.full),
                        },
                        {"role": "user", "content": json.dumps(text)},
                    ],
                    "temperature": temperature,
                }
            )
            if not response:
                logger.error("Empty response from OpenAI API.")
                return None

            return json.loads(response["choices"][0]["message"]["content"])
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON response from OpenAI API.")
        except Exception as e:
            logger.error(f"Error during translation: {e}")