import 'package:shinga_api/src/domain/domain.dart';

/// A set of public URLs for a processed cover image.
typedef CoverPaths = ({
  String thumbnailUrl,
  String originalUrl,
});

/// Use case for processing and saving manga covers.
class ProcessCoverUseCase {
  /// Creates a [ProcessCoverUseCase] instance.
  const ProcessCoverUseCase({
    required MediaDownloader downloader,
    required ImageProcessor processor,
    required MediaStorage storage,
  }) : _downloader = downloader,
       _processor = processor,
       _storage = storage;

  final MediaDownloader _downloader;
  final ImageProcessor _processor;
  final MediaStorage _storage;

  /// Executes the use case to download, process, and save a cover image.
  ///
  /// [hash] is the unique identifier for the image (used for file naming).
  /// [url] is the source URL to download the original cover from.
  Future<CoverPaths> execute({
    required String hash,
    required String url,
  }) async {
    final rawBytes = await _downloader.downloadImage(url);

    final thumb = await _processor.resizeAndConvert(
      rawBytes,
      width: 150,
      height: 225,
    );
    final sw = Stopwatch()..start();
    final original = await _processor.resizeAndConvert(
      rawBytes,
      width: 300,
      height: 450,
    );
    sw.stop();
    print('Processing time: ${sw.elapsedMilliseconds} ms');

    final thumbPath = await _storage.write(
      '$hash/thumb.${thumb.format}',
      thumb.bytes,
      overwrite: true,
    );
    final originalPath = await _storage.write(
      '$hash/original.${original.format}',
      original.bytes,
      overwrite: true,
    );

    return (
      thumbnailUrl: _storage.getPublicUrl(thumbPath),
      originalUrl: _storage.getPublicUrl(originalPath),
    );
  }
}
