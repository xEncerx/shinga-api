part of 'base.dart';

/// Base exception class for all network-related errors.
sealed class NetworkException extends BaseException {
  const NetworkException(super.details, {this.statusCode});

  /// The HTTP status code associated with the error, if any.
  final int? statusCode;
}

/// Exception thrown when a network request times out.
final class TimeoutException extends NetworkException {
  /// Creates a [TimeoutException] instance.
  const TimeoutException(super.details) : super(statusCode: 408);
}

/// Exception thrown when a requested resource is not found (HTTP 404).
final class NotFoundException extends NetworkException {
  /// Creates a [NotFoundException] instance.
  const NotFoundException(super.details) : super(statusCode: 404);
}

/// Exception thrown when the client is rate limited (HTTP 429).
final class RateLimitException extends NetworkException {
  /// Creates a [RateLimitException] instance.
  const RateLimitException(super.details, {this.retryAfter}) : super(statusCode: 429);

  /// The duration to wait before retrying the request, if provided by the server.
  final Duration? retryAfter;
}

/// Exception thrown when the server encounters an internal error (HTTP 500+).
final class ServerException extends NetworkException {
  /// Creates a [ServerException] instance.
  const ServerException(super.details, {super.statusCode});
}

/// Exception thrown when the client request is invalid (HTTP 400-499, excluding 404 and 429).
final class ClientException extends NetworkException {
  /// Creates a [ClientException] instance.
  const ClientException(super.details, {super.statusCode});
}

/// Exception thrown when there is no internet connection or DNS resolution fails.
final class ConnectionException extends NetworkException {
  /// Creates a [ConnectionException] instance.
  const ConnectionException(super.details);
}

/// Exception thrown for any other unexpected network error.
final class UnknownNetworkException extends NetworkException {
  /// Creates an [UnknownNetworkException] instance.
  const UnknownNetworkException(super.details);
}
