import os
import requests
from PIL import Image
from io import BytesIO

# Define species and their corresponding GBIF taxon keys
species_info = {
    "Puccinellia maritima": {"gbif_taxon_key": 2704687},
    "Glaux maritima": {"gbif_taxon_key": 5414349},
    "Spartina maritima": {"gbif_taxon_key": 2704689}
}

def get_next_image_index(directory):
    os.makedirs(directory, exist_ok=True)
    existing_files = [f for f in os.listdir(directory) if f.endswith('.jpg')]
    if not existing_files:
        return 0
    indices = [int(f.split('_')[-1].split('.')[0]) for f in existing_files if f.split('_')[-1].split('.')[0].isdigit()]
    return max(indices) + 1 if indices else 0

def download_inaturalist_images(species_name, max_images, output_dir):
    print(f"Downloading {max_images} images of '{species_name}' from iNaturalist...")
    count = get_next_image_index(output_dir)
    page = 1
    per_page = 100

    while count < max_images:
        params = {
            "taxon_name": species_name,
            "photos": "true",
            "per_page": per_page,
            "page": page
        }
        try:
            response = requests.get("https://api.inaturalist.org/v1/observations", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from iNaturalist: {e}")
            break

        results = data.get('results', [])
        if not results:
            print("No more results from iNaturalist.")
            break

        for result in results:
            photos = result.get('photos', [])
            for photo in photos:
                if count >= max_images:
                    break
                url = photo.get('url')
                if url:
                    img_url = url.replace("square", "original")
                    try:
                        img_response = requests.get(img_url, timeout=10)
                        img_response.raise_for_status()
                        img = Image.open(BytesIO(img_response.content))
                        img_path = os.path.join(output_dir, f"{species_name.replace(' ', '_')}_{count}.jpg")
                        img.save(img_path)
                        count += 1
                    except Exception as e:
                        print(f"Error downloading image: {e}")
                        continue
        page += 1
    print(f"Downloaded {count} images of '{species_name}' from iNaturalist.")

def download_gbif_images(species_name, taxon_key, max_images, output_dir):
    print(f"Downloading {max_images} images of '{species_name}' from GBIF...")
    count = get_next_image_index(output_dir)
    offset = 0
    limit = 300

    while count < max_images:
        params = {
            "mediaType": "StillImage",
            "taxonKey": taxon_key,
            "limit": limit,
            "offset": offset
        }
        try:
            response = requests.get("https://api.gbif.org/v1/occurrence/search", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching data from GBIF: {e}")
            break

        results = data.get('results', [])
        if not results:
            print("No more results from GBIF.")
            break

        for result in results:
            media = result.get('media', [])
            for item in media:
                if count >= max_images:
                    break
                img_url = item.get('identifier')
                if img_url:
                    try:
                        img_response = requests.get(img_url, timeout=10)
                        img_response.raise_for_status()
                        img = Image.open(BytesIO(img_response.content))
                        img_path = os.path.join(output_dir, f"{species_name.replace(' ', '_')}_{count}.jpg")
                        img.save(img_path)
                        count += 1
                    except Exception as e:
                        print(f"Error downloading image: {e}")
                        continue
        offset += limit
    print(f"Downloaded {count} images of '{species_name}' from GBIF.")

def main():
    max_images_per_source = 10000  # Adjust as needed
    for species, info in species_info.items():
        output_dir = species.replace(" ", "_")
        os.makedirs(output_dir, exist_ok=True)
        download_inaturalist_images(species, max_images_per_source, output_dir)
        download_gbif_images(species, info["gbif_taxon_key"], max_images_per_source, output_dir)

if __name__ == "__main__":
    main()
