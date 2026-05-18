import 'package:shinga_api/src/src.dart';
import 'package:talker/talker.dart';

/// A class that holds all the dependencies for the application.
final class Deps {
  static bool _initialized = false;

  /// The logger instance for the application.
  static late final Talker logger;

  /// The environment configuration for the application.
  static late final EnvConfig env;

  /// Initializes the dependencies.
  ///
  /// This should be called before using any of the dependencies.
  static Future<void> init() async {
    if (_initialized) throw StateError('Deps already initialized');

    logger = Talker(logger: TalkerLogger(formatter: const SimpleFormatter()));
    env = EnvConfig();

    _initialized = true;
  }
}
