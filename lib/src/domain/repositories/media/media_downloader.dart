import 'dart:typed_data';

/// An interface for downloading media, such as images, from a given URL.
abstract interface class MediaDownloader {
  /// Downloads an image from the specified [url] and returns it as a [Uint8List].
  Future<Uint8List> downloadImage(String url);
}
