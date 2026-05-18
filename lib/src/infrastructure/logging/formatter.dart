import 'package:talker/talker.dart';

/// A simple formatter that only returns the log message as a string.
class SimpleFormatter implements LoggerFormatter {
  /// Creates a [SimpleFormatter] instance.
  const SimpleFormatter();

  @override
  String fmt(LogDetails details, TalkerLoggerSettings settings) {
    return details.message?.toString() ?? '';
  }
}
