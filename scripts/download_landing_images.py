import os
import requests

IMAGES = {
    'hero_mandi_dawn.jpg': 'https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&q=80&w=1200',
    'marketplace_staples.jpg': 'https://images.unsplash.com/photo-1596797038530-2c107229654b?auto=format&fit=crop&q=80&w=1200',
    'vendor_stall_morning.jpg': 'https://images.unsplash.com/photo-1626132647523-66f5bf380027?auto=format&fit=crop&q=80&w=1200'
}

OUTPUT_DIR = 'my_app/static/uploads'

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for name, url in IMAGES.items():
        path = os.path.join(OUTPUT_DIR, name)
        print(f"Downloading {name} from Unsplash...")
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(r.content)
                print(f"Saved to {path}")
            else:
                print(f"Failed to download {name}: Status {r.status_code}")
        except Exception as e:
            print(f"Error downloading {name}: {e}")

if __name__ == '__main__':
    main()
