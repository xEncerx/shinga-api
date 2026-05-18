import 'package:dotenv/dotenv.dart';
import 'package:shinga_api/src/domain/domain.dart';

/// A class that provides access to environment variables for the application.
class EnvConfig {
  static final _env = DotEnv(includePlatformEnvironment: true, quiet: true)..load();

  /// The current flavor of the application (e.g., dev, prod).
  static EnvFlavor get flavor => EnvFlavor.fromString(_env['FLAVOR'] ?? 'dev');

  /// The proxy URL for the application, if any.
  static String? get proxy => _env['PROXY'];

  /// The PostgreSQL username.
  static String get postgresUser => _env['POSTGRES_USER'] ?? 'postgres';

  /// The PostgreSQL password, if configured.
  static String? get postgresPassword => _env['POSTGRES_PASSWORD'];

  /// The PostgreSQL host.
  static String get postgresHost => _env['POSTGRES_HOST'] ?? 'localhost';

  /// The PostgreSQL database name.
  static String get postgresDb => _env['POSTGRES_DB'] ?? 'shinga_db';

  /// The PostgreSQL port.
  static int get postgresPort => int.tryParse(_env['POSTGRES_PORT'] ?? '5432') ?? 5432;

  /// The Redis host.
  static String get redisHost => _env['REDIS_HOST'] ?? 'localhost';

  /// The Redis port.
  static int get redisPort => int.tryParse(_env['REDIS_PORT'] ?? '6379') ?? 6379;

  /// The SMTP host, if configured.
  static String? get smtpHost => _env['SMTP_HOST'];

  /// The SMTP port, if configured.
  static int? get smtpPort => int.tryParse(_env['SMTP_PORT'] ?? '587');

  /// The SMTP username, if configured.
  static String? get smtpUsername => _env['SMTP_USERNAME'];

  /// The SMTP password, if configured.
  static String? get smtpPassword => _env['SMTP_PASSWORD'];

  /// The email domain, if configured.
  static String? get emailDomain => _env['EMAIL_DOMAIN'];

  /// Whether SMTP should use TLS.
  static bool get smtpUseTls => _env['SMTP_USE_TLS']?.toLowerCase() == 'true';

  /// The base path used for file storage.
  static String get storageBasePath => _env['STORAGE_BASE_PATH'] ?? 'storage/';

  /// The public prefix used for serving static files.
  static String get storagePublicPrefix => _env['PUBLIC_STATIC_PREFIX'] ?? '/static/';

  /// The application secret key, if configured.
  static String? get secretKey => _env['SECRET_KEY'];
}
