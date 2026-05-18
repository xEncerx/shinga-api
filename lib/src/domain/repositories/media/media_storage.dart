import 'dart:typed_data';

/// An interface for storing media.
abstract interface class MediaStorage {
  /// Writes the given bytes to the specified path and returns the relative path of the stored media.
  ///
  /// If [overwrite] is true, it will overwrite the file if it already exists.
  Future<String> write(String path, Uint8List bytes, {bool overwrite = false});

  /// Retrieves the public URL for the media stored at the given relative path.
  String getPublicUrl(String relativePath);
}
