/// Defines the different environment flavors for the application.
enum EnvFlavor {
  /// The development environment flavor.
  dev,

  /// The production environment flavor.
  prod
  ;

  /// Creates an [EnvFlavor] from a string representation.
  static EnvFlavor fromString(String flavor) {
    switch (flavor.toLowerCase()) {
      case 'dev':
        return EnvFlavor.dev;
      case 'prod':
        return EnvFlavor.prod;
      default:
        throw ArgumentError('Unknown environment flavor: $flavor');
    }
  }
}
