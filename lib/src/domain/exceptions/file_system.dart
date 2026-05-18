part of 'base.dart';

/// Exceptions related to file system operations.
final class FileSystemException extends BaseException {
  /// Creates a [FileSystemException] instance.
  const FileSystemException(super.details);
}

/// Exception thrown when a file is not found at the specified path.
final class FileNotFoundException extends FileSystemException {
  /// Creates a [FileNotFoundException] instance.
  const FileNotFoundException(super.details);
}

/// Exception thrown when there is an error writing to a file.
final class FileWriteException extends FileSystemException {
  /// Creates a [FileWriteException] instance.
  const FileWriteException(super.details);
}

/// Exception thrown when a file already exists and overwrite is false.
final class FileAlreadyExistsException extends FileSystemException {
  /// Creates a [FileAlreadyExistsException] instance.
  const FileAlreadyExistsException(super.details);
}

/// Exception thrown when there is a permission error (e.g., cannot create directory or write file).
final class FilePermissionException extends FileSystemException {
  /// Creates a [FilePermissionException] instance.
  const FilePermissionException(super.details);
}

/// Exception thrown when the provided path is invalid or potentially unsafe (e.g., path traversal).
final class InvalidPathException extends FileSystemException {
  /// Creates a [InvalidPathException] instance.
  const InvalidPathException(super.details);
}
