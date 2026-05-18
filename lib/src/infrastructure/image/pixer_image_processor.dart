import 'dart:typed_data';

import 'package:pixer/pixer.dart';
import 'package:shinga_api/src/domain/repositories/media/image_processor.dart';

/// An image processor implementation using the Pixer library (rust based) for efficient image manipulation.
class PixerImageProcessor implements ImageProcessor {
  /// Creates a [PixerImageProcessor] instance.
  const PixerImageProcessor();

  @override
  Future<ImageCoverResult> resizeAndConvert(
    Uint8List bytes, {
    required int width,
    required int height,
  }) async {
    final image = Pixer.fromMemory(bytes);
    try {
      final resized = image.resize(width, height, filter: FilterTypeEnum.CatmullRom);
      try {
        final contrasted = resized.contrast(10);
        try {
          return (
            bytes: contrasted.encode(PixerJpegEncoder(quality: 95)),
            format: 'jpg',
          );
        } finally {
          contrasted.dispose();
        }
      } finally {
        resized.dispose();
      }
    } finally {
      image.dispose();
    }
  }
}
