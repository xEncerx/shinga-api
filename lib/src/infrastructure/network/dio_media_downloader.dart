import 'dart:typed_data';

import 'package:dio/dio.dart';
import 'package:shinga_api/src/domain/domain.dart';

/// A class responsible for downloading media files from the network.
class DioMediaDownloader implements MediaDownloader {
  /// Creates a [MediaDownloader] instance.
  const DioMediaDownloader(this._dio);

  final Dio _dio;

  @override
  Future<Uint8List> downloadImage(String url) async {
    final response = await _dio.get<List<int>>(
      url,
      options: Options(responseType: ResponseType.bytes),
    );

    final data = response.data;
    if (data == null) {
      throw const UnknownNetworkException('Received null data from response');
    }

    return Uint8List.fromList(data);
  }
}
