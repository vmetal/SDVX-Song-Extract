import os
import shutil
import subprocess
# import jaconv
import platform, getopt
from bs4 import BeautifulSoup

relativeSongFolderPath = "data/music"
relativeMusicDbPath = "data/others/music_db.xml"

# Directory to save converted music to
outputDir = "SDVX Music"

audioFormats = {
    "mp3": "MP3 V0       (verly gud bang for your disk space buck)",
    "wav": "WAV 1411kbps (only choose this if you hate .ASF format)",
    "asf": "ASF VBR      (Original, lol .s3v is just .asf but renamed)"
    }

rankMap = {
    1: "NOV",
    2: "ADV",
    3: "EXH",
    # 4: "INF/GRV",
    # 5: "MXM"
    }

rankSuffix = ["1n","2a","3e","4i","4g","4h","5m"]

VERSIONS = {
    1: "SOUND VOLTEX BOOTH",
    2: "SOUND VOLTEX ii Infinite Infection",
    3: "SOUND VOLTEX III GRAVITY WARS",
    4: "SOUND VOLTEX IV HEAVENLY HAVEN",
    5: "SOUND VOLTEX V Vivid Wave",
    6: "SOUND VOLTEX EXCEED GEAR"
    }


if "Windows" == platform.system():
    FFMPEG = r"ffmpeg.exe"
else:
    # FFMPEG = r"/usr/bin/env ffmpeg"
    FFMPEG = r"/opt/homebrew/bin/ffmpeg"

OVERWRITE = False

# Credits to giltay @ stackoverflow 120656
def listdirFP(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

# Friendly interface to use the program
def CLI():
    print("Welcome to SDVX song extractor")
    # Fetch game folder path
    while True:
        gameFolder = input("Insert path to SDVX folder > ")
        modulesDir = gameFolder + "/modules"
        if "Windows" == platform.system():
            modulesDir = modulesDir.replace("/", "\\")
        
        if os.path.exists(gameFolder) and "soundvoltex.dll" in os.listdir(modulesDir):
            print("OK, that path looks legit, yesssss")
            break
        else:
            print("I can't see any soundvoltex.dll here :C")
    # Fetch audio format choice
    while True:
        print("Choose your format!\n", "-"*30)
        for i, audioFormat in audioFormats.items():
            print("%s = %s}" % (i, audioFormat))
        format = input("> ")
        if format in audioFormats.keys():
            print("OK starting...")
            break
        else:
            print("Incorrect format specified")
    return gameFolder, format

# Gets list of all full relative paths to wanted .s3v files
def getSongPaths(gameFolder):
    songPaths = []
    songsFolder = os.path.join(gameFolder, relativeSongFolderPath)
    for songFolder in listdirFP(songsFolder):
        if os.path.isdir(songFolder):
            for filename in listdirFP(songFolder):
                if filename.endswith(".s3v") and not filename.endswith("_pre.s3v"):
                    songPaths.append(filename)
                elif filename.endswith(".2dx") and not filename.endswith("_pre.2dx"):
                    songPaths.append(filename)
    return songPaths

# Convert and-or copy songs and place them in music directory
def extractSongs(songPaths, format, metadatum):
    outputFolder = os.path.join(outputDir, format)
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
    for name in VERSIONS.values():
        if not os.path.exists(os.path.join(outputFolder, name)):
            os.makedirs(os.path.join(outputFolder, name))
    # ID3v2.3
    meta_params = {
        "title": '%s',                      # Title
        "artist": '%s',                     # Artist
        "album_artist": "Various Artist",   # Album Artist
        "album": '%s',                      # Album
        "genre": '%s',                      # Genre
        "date": '%04d',                     # Year
        "track": '%d',                      # Track
        "disc": '%d',                       # Disc (Version)
        "TBPM": '%s',                       # BPM
    }
    cmd = {
        "wav": FFMPEG + ''' -y -ss 0.9 -i "%s" -i "%s" -map 0:0 -map 1:0 -id3v2_version 3''',
        "mp3": FFMPEG + ''' -y -ss 0.9 -i "%s" -i "%s" -map 0:0 -map 1:0 -id3v2_version 3 -q:a 0''',
        "asf": False
    }[format]

    for key, meta in meta_params.items():
        cmd += ''' -metadata:g %s="%s"''' % (key, meta)
    cmd += r' "%s"'

    for songPath in songPaths:
        filename = os.path.basename(songPath)
        songId = filename.split("_")[0]
        if (int(songId) not in metadatum):
            print("Skipping %s, because removed from music_db.xml <= %s" % (songId, filename))
            continue
        meta = metadatum[int(songId)]
        outputFile = os.path.join(outputFolder, VERSIONS[meta["version"]], filename[:-3] + format)
        overwrite = False
        # overwrite = "&" in meta["title"] or "&" in meta["artist"]
        if (not os.path.exists(outputFile)) or overwrite:
            jacketPath = getJacket(songPath,int(songId))

            bpm = meta["bpm_min"]
            if not bpm == meta["bpm_max"]:
                bpm = meta["bpm_max"]
            
            title = meta["title"]
            artist = meta["artist"]


            if filename.endswith(".2dx"):
                # .2dx file needs convert to wave files
                iidx_cmd = r'2dx_extract\\bin\\2dx_extract.exe "%s"' % (songPath)
                subprocess.run(iidx_cmd, shell=True, check=True)
                filename = filename.replace(".2dx",".s3v")
                # rename to s3v file
                songPath = songPath.replace(".2dx", ".s3v")
                if os.path.exists(songPath) == False:
                    # copy extracted from .2dx wave file as .s3v
                    shutil.copy2("1.wav", songPath)
                # remove temporary files
                for wfiles in os.listdir("."):
                    if os.path.isfile(wfiles) and wfiles.endswith(".wav"):
                        os.remove(wfiles)

            exec_cmd = cmd % (
                songPath,
                jacketPath,
                cmdEscape(title),
                cmdEscape(artist),
                VERSIONS[meta["version"]],
                meta["genre"],
                int(meta["release_year"]),
                int(songId),
                int(meta["version"]),
                bpm,
                outputFile,
                )
            try:
                print("Executing command:", exec_cmd)
                subprocess.run(exec_cmd, shell=True, check=True) \
                if cmd else shutil.copy2(songPath, outputFile)
            except subprocess.CalledProcessError as e:
                print("\n===================================\n" \
                    + str(exec_cmd) + \
                    "\n===================================\n")
                print("ERROR", e.stderr)
                print("Return code:", e.returncode)  # Error code
                print("Output:", e.output)  # Error message

def getJacket(songPath, songId):
    songDir = os.path.dirname(songPath)
    dataDir = os.path.normpath(os.path.join(songDir, os.path.pardir, os.path.pardir))
    file_suffix = os.path.splitext(os.path.basename(songPath))[0].split("_")[-1]
    if file_suffix in rankSuffix :
        jkFile = 'jk_{0:04d}_{1}_b.png'.format(songId, file_suffix[0])
        jkPath = os.path.join(songDir,jkFile)
        if os.path.exists(jkPath):
            return jkPath
    for rank in sorted(rankMap.keys(), reverse=True):
        jkFile = 'jk_{0:04d}_{1}_b.png'.format(songId, rank)
        jkPath = os.path.join(songDir,jkFile)
        if os.path.exists(jkPath):
            return jkPath
    return os.path.join(dataDir, "graphics", "jk_dummy_b.png")

def extractSongsMetadata(songPaths, gameFolder):
    metadatum={}
    songIds = [int(os.path.basename(filename).split("_")[0]) for filename in songPaths]

    with open(os.path.join(gameFolder, relativeMusicDbPath), "r", encoding="Shift-JIS", errors="ignore") as xmlFile:
        soup = BeautifulSoup(xmlFile.read(), features="lxml")

    musics = soup.find_all("music")
    for music in musics:
        metadatum[int(music["id"])] = {
            "title": fixBrokenChars(music.find("title_name").text),
            "artist": fixBrokenChars(music.find("artist_name").text),
            "genre": music.find("genre").text,
            # "title_sort": jaconv.h2z(music.find("title_yomigana").text),
            # "artist_sort": jaconv.h2z(music.find("artist_yomigana").text),
            "release_year": music.find("distribution_date").text[:4],
            "version": int(music.find("version").text),
            "bpm_max": (int(music.find("bpm_max").text) / 100),
            "bpm_min": (int(music.find("bpm_min").text) / 100),
            "volume": int(music.find("volume").text) / 127.0,
            "track": int(music["id"])
        }
    
    metadatum[9001] = {
        "title": "SOUND VOLTEX Tutorial",
        "artist": "SOUND VOLTEX Team",
        "genre": "Tutorial",
        # "title_sort": "さうんどぼるてっくすちゅーとりある",
        # "artist_sort": "さうんどぼるてっくすちーむ",
        "release_year": "2020",
        "version": 6,
        "bpm_max": 110,
        "bpm_min": 110,
        "volume": 127.0,
        "track": 9001
    }

    return metadatum

# ref: https://gist.github.com/hannahherbig/d67c2bfefcca207640c001e0ddd5e000
def fixBrokenChars(name):
    map = [
        ['\u00D7', '×'],
        ['\u1FE6', 'ῦ'],
        ['\u203E', '~'],
        ['\u301C', '～'],
        ['\u49FA', 'ê'],
        ['\u58B8', ' ']
        ['\u58EC', 'ê'],
        ['\u5F5C', 'ū'],
        ['\u66E6', 'à'],
        ['\u66E9', 'è'],
        ['\u7011', 'À'],
        ['\u7162', 'ø'],
        ['\u745F', 'ō'],
        ['\u76E5', '⚙'],
        ['\u8D81', 'Ǣ'],
        ['\u8E59', 'ℱ'],
        ['\u8E94', '🐾'],
        ['\u91C1', '🍄'],
        ['\u9448', '♦'],
        ['\u9477', 'ゔ'],
        ['\u95C3', 'Ā'],
        ['\u96CB', 'Ǜ'],
        ['\u96CD', 'Ü'],
        ['\u973B', '♠'],
        ['\u983D', 'ä'],
        ['\u992E', 'Ƶ'],
        ['\u994C', '²'],
        ['\u9A2B', 'á'],
        ['\u9A69', 'Ø'],
        ['\u9A6A', 'ō'],
        ['\u9A6B', 'ā'],
        ['\u9AAD', 'ü'],
        ['\u9B06', 'Ý'],
        ['\u9B25', 'Ã'],
        ['\u9B2E', '¡'],
        ['\u9B2F', 'ī'],
        ['\u9B32', 'Ý'],
        ['\u9B3B', '♃'],
        ['\u9E79', 'Ĥ'],
        ['\u9EF7', 'ē'],
        ['\u9EFB', '*'],
        ['\u9F63', 'Ú'],
        ['\u9F67', 'Ä'],
        ['\u9F6A', '♣'],
        ['\u9F72', '♥'],
        ['\u9F76', '♡'],
        ['\u9F77', 'é'],
        ['\u9F77', 'é'],
        ['\u9F95', '€'],
    ]
    for m in map:
        name = name.replace(m[0], m[1])
    return name


def cmdEscape(str):
    if "Windows" == platform.system():
        # For PowerSehll 
        map = [
            ['"', '\\"'],
            ['&', '&'],
        ]
    else:
        # Linux
        map = [
            ['"', '\\"'],
            ['$', '\\$']
        ]
    for repl in map:
        str = str.replace(repl[0], repl[1])
    return str


def main(argv = None):
    try:
        opts, args = getopt.getopt(argv, "hw",["help","overwrite"])
    except getopt.GetoptError:
      print("$0 -i <inputfile> -o <outputfile>")

    gameFolder, format = CLI()
    songPaths = getSongPaths(gameFolder)
    print("Loading meta datum...")
    metadatas = extractSongsMetadata(songPaths, gameFolder)
    print("Extract songs...")
    extractSongs(songPaths, format, metadatas)
    print("Finished !")
main()
