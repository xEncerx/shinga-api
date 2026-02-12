from taskiq_redis import RedisStreamBroker, RedisAsyncResultBackend
from taskiq import SmartRetryMiddleware

from src.core import settings

__all__ = ["parsing_broker", "email_broker"]

default_retry_middleware = SmartRetryMiddleware(
    default_retry_count=3,
    default_delay=10,
    use_jitter=True,
    use_delay_exponent=True,
    max_delay_exponent=300,
)

result_backend = RedisAsyncResultBackend(
    redis_url=str(settings.REDIS_DSN),
    result_ex_time=6 * 60 * 60,  # 6 hours
)

parsing_broker = (
    RedisStreamBroker(url=str(settings.REDIS_DSN), queue_name="parsing_queue")
    .with_result_backend(result_backend)
    .with_middlewares(default_retry_middleware)
)

email_broker = (
    RedisStreamBroker(url=str(settings.REDIS_DSN), queue_name="email_queue")
    .with_result_backend(result_backend)
    .with_middlewares(default_retry_middleware)
)
