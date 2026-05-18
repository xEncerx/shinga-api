part 'file_system.dart';
part 'network.dart';

/// Base exception class for all exceptions in the application.
sealed class BaseException implements Exception {
  const BaseException(this.details);

  /// A detailed message describing the exception.
  final String details;

  @override
  String toString() => details;
}
