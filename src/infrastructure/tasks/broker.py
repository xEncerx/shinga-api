from taskiq_redis import RedisStreamBroker, RedisAsyncResultBackend
from taskiq import SmartRetryMiddleware

from src.core import settings

__all__ = ["broker"]

result_backend = RedisAsyncResultBackend(
    redis_url=str(settings.REDIS_DSN),
    result_ex_time=6 * 60 * 60,  # 6 hours
)

broker = (
    RedisStreamBroker(
        url=str(settings.REDIS_DSN),
    )
    .with_result_backend(result_backend)
    .with_middlewares( 
        SmartRetryMiddleware(
            default_retry_count=3,
            default_delay=10,
            use_jitter=True,
            use_delay_exponent=True,
            max_delay_exponent=300,
        )
    )
)
