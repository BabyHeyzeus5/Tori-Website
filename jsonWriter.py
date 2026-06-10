import os
import json

try:
    from pillow_heif import register_heif_opener
    from PIL import Image
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False

SOUND_EXTENSIONS = {'.mp3', '.m4a', '.wav', '.ogg', '.aac'}
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
HEIC_EXTENSIONS  = {'.heic', '.heif'}

def convert_heic(folder):
    if not HEIC_SUPPORTED:
        print("  Note: pillow-heif not installed, skipping HEIC conversion.")
        print("  Run: pip install pillow-heif\n")
        return

    heics = [
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in HEIC_EXTENSIONS
    ]
    if not heics:
        return

    print(f"  Found {len(heics)} HEIC file(s) — converting to JPG...")
    for filename in heics:
        src = os.path.join(folder, filename)
        dst = os.path.join(folder, os.path.splitext(filename)[0] + '.jpg')
        if os.path.exists(dst):
            print(f"    Skipping {filename} (JPG already exists)")
            continue
        try:
            img = Image.open(src)
            img.convert('RGB').save(dst, 'JPEG', quality=90)
            print(f"    Converted: {filename} -> {os.path.basename(dst)}")
        except Exception as e:
            print(f"    Failed to convert {filename}: {e}")
    print()

def get_files(folder, extensions):
    if not os.path.isdir(folder):
        print(f"  Warning: folder '{folder}' not found, skipping.")
        return []
    return sorted([
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in extensions
    ])

def build_entries(sounds_folder, photos_folder):
    convert_heic(photos_folder)

    sounds = get_files(sounds_folder, SOUND_EXTENSIONS)
    photos = get_files(photos_folder, PHOTO_EXTENSIONS)

    if not sounds:
        print("No sound files found. Nothing to generate.")
        return []

    entries = []
    for i, sound in enumerate(sounds):
        name = os.path.splitext(sound)[0].replace('-', ' ').replace('_', ' ')
        photo = photos[i % len(photos)] if photos else None
        entry = {
            "title": name,
            "file": f"{sounds_folder}/{sound}",
        }
        if photo:
            entry["photo"] = f"{photos_folder}/{photo}"
        entries.append(entry)

    return entries

def main():
    print("=== data.json generator ===\n")

    sounds_folder = input("Sounds folder path (e.g. sounds): ").strip().rstrip('/')
    photos_folder = input("Photos folder path (e.g. photos): ").strip().rstrip('/')
    output_file   = input("Output file name [data.json]: ").strip() or "data.json"

    print()
    entries = build_entries(sounds_folder, photos_folder)

    if not entries:
        return

    with open(output_file, 'w') as f:
        json.dump(entries, f, indent=2)

    print(f"Done! {len(entries)} entries written to '{output_file}':\n")
    for e in entries:
        photo_str = e.get('photo', '(no photo)')
        print(f"  [{e['title']}]  sound: {e['file']}  |  photo: {photo_str}")

if __name__ == '__main__':
    main()