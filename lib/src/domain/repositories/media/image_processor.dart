import 'dart:typed_data';

/// A typedef for the result of image processing, containing the processed image bytes and its format.
typedef ImageCoverResult = ({
  Uint8List bytes,
  String format,
});

/// An interface for processing images, including resizing and format conversion.
abstract interface class ImageProcessor {
  /// Resizes the image provided as raw [bytes] to the specified [width] and [height].
  Future<ImageCoverResult> resizeAndConvert(
    Uint8List bytes, {
    required int width,
    required int height,
  });
}
