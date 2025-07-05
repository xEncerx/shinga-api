import asyncio

from app.infrastructure.parser import GlobalMalParser
from app.core import setup_logging


async def main():
    """
    Main function to run the GlobalMalParser.
    
    In this implementation, the parser collects and processes data from Jikan.moe
    
    The processing occurs in several stages:
    1. We parse the data page from https://api.jikan.moe/v4/manga?page=1 and convert it into a Title model, which is saved to the database.
    1.1. Title covers are also saved (we download the largest size and resize it to medium and small dimensions)
    2. Then the data is sent to a translation queue using the OpenAI API.
    3. If the title is ongoing, the parser will update the data to the latest version every N time
    
    For faster performance, multiple workers are used to process data in parallel.
    Therefore, for stable operation, many proxies are needed to avoid flooding from a single IP. (At least 1 proxy is required)

    Example of my usage:
    - 10 workers (8 for parsing, 2 for translation)
    - proxies: 40 units
    - OpenAI API keys: 2 keys
    -> Parsing 3084 pages took about 2 hours.

    Proxy calculations:
    - 1 page contains 25 titles.
    - Parsing 1 page uses 1 proxy + downloading all covers (25 items) uses 2 more proxies.
    - Each translation also uses 1 proxy

    P.S.: Currently, you must specify at least 1 proxy and 1 OpenAI API key
    """
    async with GlobalMalParser(num_workers=10) as parser:
        await parser.idle()


if __name__ == "__main__":
    setup_logging(file_name="parser")

    asyncio.run(main())
