import 'package:dio/dio.dart';
import 'package:shinga_api/src/domain/domain.dart';

/// An interceptor that catches [DioException]s and transforms them into domain-specific [NetworkException]s.
class ErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    final domainException = _transformDioException(err);
    handler.reject(
      DioException(
        requestOptions: err.requestOptions,
        response: err.response,
        type: err.type,
        error: domainException,
      ),
    );
  }

  NetworkException _transformDioException(DioException err) {
    switch (err.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return TimeoutException('Connection timed out: ${err.message}');

      case DioExceptionType.connectionError:
        return ConnectionException('Connection failed: ${err.message}');

      case DioExceptionType.badResponse:
        final statusCode = err.response?.statusCode;
        final details = 'Received bad response: $statusCode';

        if (statusCode == 404) {
          return NotFoundException(details);
        } else if (statusCode == 429) {
          // Try to parse Retry-After header
          Duration? retryAfter;
          final headerVal = err.response?.headers.value('retry-after');
          if (headerVal != null) {
            final seconds = int.tryParse(headerVal);
            if (seconds != null) {
              retryAfter = Duration(seconds: seconds);
            }
          }
          return RateLimitException(details, retryAfter: retryAfter);
        } else if (statusCode != null && statusCode >= 500) {
          return ServerException(details, statusCode: statusCode);
        } else if (statusCode != null && statusCode >= 400) {
          return ClientException(details, statusCode: statusCode);
        }
        return UnknownNetworkException(details);

      case DioExceptionType.cancel:
        return const UnknownNetworkException('Request was cancelled');

      case DioExceptionType.badCertificate:
        return ConnectionException('Bad certificate: ${err.message}');

      case DioExceptionType.unknown:
        return UnknownNetworkException('Unknown network error: ${err.error ?? err.message}');
    }
  }
}
