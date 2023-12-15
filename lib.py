from os import makedirs, path, remove
from zipfile import ZipFile
from requests import Response, get

from utils import measure_time, sep_print_block


def get_filename_from_request(resp: Response) -> str:
    """Витягує назву файлу з тіла відповіді. В іншому випадку повертає назву файлу з URL-адреси."""
    content_disposition = resp.headers.get("Content-Disposition")
    if content_disposition:
        return content_disposition.split("filename=")[-1].strip('"')
    else:
        return resp.url.split("/")[-1]

def unzip_contents(zip_save_dir: str, output_dir: str) -> None:
    """Витягує файли CSV з архіву ZIP. Після розпакування видаліть архів."""
    with ZipFile(zip_save_dir, "r") as zip_ref:
        csv_files = [file for file in zip_ref.namelist() if file.endswith(".csv") and "__MACOSX" not in file]

        if not csv_files:
            print("У ZIP-архіві не знайдено файлів CSV.")
            return

        for csv_file in csv_files:
            zip_ref.extract(csv_file, path=output_dir)
            print(f"Файл успішно розпаковано {csv_file}.")

    remove(zip_save_dir)

@sep_print_block(symbol="=")
@measure_time
def download_resource(url: str, output_dir: str) -> None:
    makedirs(output_dir, exist_ok=True)

    print(f"Завантаження ресурсу з {url}...")
    response = get(url, allow_redirects=True)

    if response.status_code != 200:
        print(
            f"Сталася помилка під час отримання ресурсів із {url}. Код стану: {response.status_code}."
        )
        return
    content_type = response.headers.get("Content-Type")
    if 'zip' not in content_type:
        print(
            f"Завантаження ресурсу з указаної URL-адреси {url} не є архівом ZIP."
        )
        return
    
    filename = get_filename_from_request(response)

    zip_save_dir = path.join(output_dir, filename)
    with open(zip_save_dir, "wb") as f:
        f.write(response.content)
    print(f"Успішно збережено {filename} до {output_dir} каталогу.")

    unzip_contents(zip_save_dir, output_dir)