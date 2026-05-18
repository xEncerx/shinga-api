import 'dart:typed_data';

import 'package:image/image.dart' as img;
import 'package:shinga_api/src/domain/repositories/media/image_processor.dart';

/// An image processor implementation using the Dart image library for image manipulation.
class DartImageProcessor implements ImageProcessor {
  /// Creates a [DartImageProcessor] instance.
  const DartImageProcessor();

  @override
  Future<ImageCoverResult> resizeAndConvert(
    Uint8List bytes, {
    required int width,
    required int height,
    int quality = 100,
  }) async {
    final cmd = img.Command()
      ..decodeImage(bytes)
      ..copyResize(
        width: width,
        height: height,
        maintainAspect: true,
        interpolation: img.Interpolation.linear,
      )
      ..encodeJpg(quality: quality);

    final result = await cmd.getBytes();
    if (result == null) {
      throw StateError('Failed to process image: command produced no output.');
    }
    return (
      bytes: result,
      format: 'jpg',
    );
  }
}
