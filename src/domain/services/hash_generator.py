import hashlib


class MediaHashGenerator:
    """A service for generating hashes for media files."""

    @staticmethod
    def generate_cover_hash(source_name: str, external_id: str) -> str:
        """Generate a unique hash for a cover image based on its source and external ID."""

        hash_input = f"{source_name}:{external_id}".encode("utf-8")
        full_hash = hashlib.sha256(hash_input).hexdigest()
        return full_hash[:16]
