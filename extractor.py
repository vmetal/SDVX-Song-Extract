import os
import shutil
import subprocess
import logging
from pathlib import Path
from typing import List, Dict
from config import SDVXConfig

logger = logging.getLogger(__name__)

class SongExtractor:
    """Handles finding, extracting, and converting song files."""
    def __init__(self, game_folder: str, output_format: str, metadata: Dict[int, dict]):
        self.game_folder = Path(game_folder)
        self.format = output_format
        self.metadata = metadata
        self.ffmpeg = SDVXConfig.get_ffmpeg_path()
        self.extract_2dx = SDVXConfig.get_2dx_extract_path()

    def run(self):
        """Main loop to process all songs found in the game folder."""
        output_base = SDVXConfig.OUTPUT_DIR / self.format
        output_base.mkdir(parents=True, exist_ok=True)

        # Pre-create version directories
        for v_name in SDVXConfig.VERSIONS.values():
            (output_base / v_name).mkdir(exist_ok=True)

        song_paths = self._find_songs()
        for path in song_paths:
            self._process_single_song(path, output_base)

    def _find_songs(self) -> List[Path]:
        """Recursively find valid .s3v and .2dx files."""
        songs_dir = self.game_folder / SDVXConfig.RELATIVE_SONG_FOLDER
        if not songs_dir.exists():
            return []
        return [p for p in songs_dir.rglob("*") 
                if p.suffix in [".s3v", ".2dx"] and "_pre" not in p.name]

    def _process_single_song(self, song_path: Path, output_base: Path):
        """Process a single file: extract, find jacket, and convert."""
        try:
            # Assumes file name starts with song ID (e.g., 1234_track.s3v)
            song_id = int(song_path.name.split("_")[0])
        except ValueError:
            return

        if song_id not in self.metadata:
            return

        meta = self.metadata[song_id]
        v_name = SDVXConfig.VERSIONS.get(meta["version"], "Unknown")
        output_file = output_base / v_name / f"{song_path.stem}.{self.format}"

        if output_file.exists():
            return

        target_path = song_path
        temp_files = []
        
        # Handle IIDX-style containers if necessary
        if song_path.suffix == ".2dx":
            target_path, temp_files = self._handle_2dx(song_path)

        # Locate the best matching jacket image
        jacket = self._find_jacket(song_path, song_id)
        
        # Execute ffmpeg conversion
        self._convert(target_path, jacket, meta, output_file)

        # Cleanup intermediate files
        for f in temp_files:
            if os.path.exists(f): os.remove(f)

    def _handle_2dx(self, song_path: Path) -> (Path, List[str]):
        """Extract wav from .2dx using external tool."""
        try:
            subprocess.run([self.extract_2dx, str(song_path)], check=True, capture_output=True)
            tmp_s3v = song_path.with_suffix(".s3v_tmp")
            if os.path.exists("1.wav"):
                shutil.copy2("1.wav", tmp_s3v)
                return tmp_s3v, ["1.wav", str(tmp_s3v)]
        except Exception as e:
            logger.error(f"2dx_extract failed for {song_path}: {e}")
        return song_path, []

    def _find_jacket(self, song_path: Path, song_id: int) -> Path:
        """Search for the jacket image based on ID and difficulty suffixes."""
        song_dir = song_path.parent
        for suffix in SDVXConfig.RANK_SUFFIX:
            jk = song_dir / f"jk_{song_id:04d}_{suffix[0]}_b.png"
            if jk.exists(): return jk
        # Fallback to dummy jacket
        return self.game_folder / "data" / "graphics" / "jk_dummy_b.png"

    def _convert(self, src: Path, jk: Path, meta: dict, dst: Path):
        """Execute ffmpeg to convert audio and embed metadata/jacket."""
        cmd = [
            self.ffmpeg, "-y", "-ss", "0.9",
            "-i", str(src),
            "-i", str(jk),
            "-map", "0:0", "-map", "1:0",
            "-id3v2_version", "3",
            "-metadata", f"title={meta['title']}",
            "-metadata", f"artist={meta['artist']}",
            "-metadata", f"album={SDVXConfig.VERSIONS.get(meta['version'], '')}",
            "-metadata", f"genre={meta['genre']}",
            "-metadata", f"date={meta['release_year']}",
            str(dst)
        ]
        if self.format == "mp3":
            cmd.insert(-1, "-q:a")
            cmd.insert(-1, "0")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Success: {meta['title']}")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
