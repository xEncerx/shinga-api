import 'dart:io' as io;
import 'dart:typed_data';

import 'package:path/path.dart' as p;
import 'package:shinga_api/src/domain/domain.dart';

/// An implementation of [MediaStorage] that handles media storage locally on the device.
class LocalMediaStorage implements MediaStorage {
  /// Creates a [LocalMediaStorage] instance.
  const LocalMediaStorage({
    required this.basePath,
    required this.publicPrefix,
    this.subfolder,
  });

  /// The base path where media files will be stored locally.
  final String basePath;

  /// The prefix used to construct the public URL for the files.
  final String publicPrefix;

  /// An optional subfolder inside [basePath] where files for this specific
  /// storage instance will be saved (e.g., 'covers' or 'avatars').
  final String? subfolder;

  String get _effectiveBasePath => subfolder != null ? p.join(basePath, subfolder) : basePath;

  @override
  Future<String> write(String path, Uint8List bytes, {bool overwrite = false}) async {
    // Sanitize path to prevent directory traversal
    if (path.contains('..') || p.isAbsolute(path)) {
      throw const InvalidPathException(
        'Invalid path provided. Path traversal or absolute paths are not allowed.',
      );
    }

    final fullPath = p.join(_effectiveBasePath, path);
    final file = io.File(fullPath);

    // We use async io methods here because dart_frog is a web server and we don't want to block the thread.
    // ignore: avoid_slow_async_io
    if (await file.exists() && !overwrite) {
      throw FileAlreadyExistsException('File at path "$path" already exists.');
    }

    try {
      final parentDir = file.parent;
      // We use async io methods here because dart_frog is a web server and we don't want to block the thread.
      // ignore: avoid_slow_async_io
      if (!await parentDir.exists()) {
        await parentDir.create(recursive: true);
      }

      await file.writeAsBytes(bytes);
      return path;
    } on io.FileSystemException catch (e) {
      final message = e.message.toLowerCase();
      if (message.contains('permission denied') || message.contains('access is denied')) {
        throw FilePermissionException('Permission denied when writing to $path: ${e.message}');
      }
      throw FileWriteException('Failed to write file to $path: ${e.message}');
    } catch (e) {
      throw FileWriteException('Unexpected error writing to $path: $e');
    }
  }

  @override
  String getPublicUrl(String relativePath) {
    // Ensure publicPrefix ends with /
    var prefix = publicPrefix.endsWith('/') ? publicPrefix : '$publicPrefix/';

    // Append subfolder to the prefix if it exists
    if (subfolder != null) {
      final cleanSubfolder = subfolder!.startsWith('/') ? subfolder!.substring(1) : subfolder!;
      prefix += cleanSubfolder.endsWith('/') ? cleanSubfolder : '$cleanSubfolder/';
    }

    final cleanPath = relativePath.startsWith('/') ? relativePath.substring(1) : relativePath;

    return '$prefix$cleanPath';
  }
}
