import 'package:dio/dio.dart';
import 'package:shinga_api/lib.dart';

void main() async {
  final result =
      await ProcessCoverUseCase(
        downloader: DioMediaDownloader(Dio()),
        processor: const PixerImageProcessor(),
        storage: const LocalMediaStorage(
          basePath: './media_storage',
          publicPrefix: '/static',
          subfolder: 'covers',
        ),
      ).execute(
        hash: 'dhgsdf73142',
        url:
            'https://remanga.org/media/titles/last-reincarnation-me-and-my-comrades-using-useless-skills-in-another-world/cover_886fec5d3a864b52.webp',
      );
  print(result.originalUrl);
  print(result.thumbnailUrl);
}
