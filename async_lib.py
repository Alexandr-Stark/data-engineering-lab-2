import aiohttp
import aiofiles
from zipfile import ZipFile
from os import makedirs, path, remove

async def get_filename_from_request_async(resp: aiohttp.ClientResponse) -> str:
    content_disposition = resp.headers.get("Content-Disposition")
    if content_disposition:
        return content_disposition.split("filename=")[-1].strip('"')
    else:
        return resp.url.parts[-1]

async def unzip_contents_async(zip_save_dir: str, output_dir: str):
    """Витягує файли CSV з архіву ZIP. Після розпакування видаляє архів."""
    with ZipFile(zip_save_dir, "r") as zip_ref:
        csv_files = [file for file in zip_ref.namelist() if file.endswith(".csv") and "__MACOSX" not in file]

        if not csv_files:
            print("У ZIP-архіві не знайдено файлів CSV\n")
            return

        for csv_file in csv_files:
            zip_ref.extract(csv_file, path=output_dir)
            print(f"Файл успішно розпаковано {csv_file}.\n")

    remove(zip_save_dir)

async def download_resource_async(url: str, output_dir: str, session: aiohttp.ClientSession):
    makedirs(output_dir, exist_ok=True)

    print(f"Завантаження ресурсу з {url}...\n")
    
    async with session.get(url, allow_redirects=True) as response:
        if response.status != 200:
            print(f"Під час отримання ресурсів із {url} сталася помилка. Код стану: {response.status}.\n")
            return
        content_type = response.headers.get("Content-Type")
        if 'zip' not in content_type:
            print(f"Завантаження ресурсу з указаної URL-адреси {url} не є архівом ZIP.\n")
            return

        filename = await get_filename_from_request_async(response)
        zip_save_dir = path.join(output_dir, filename)

        async with aiofiles.open(zip_save_dir, 'wb') as f:
            await f.write(await response.read())

        print(f"Успішно збережено {filename} до {output_dir} каталогу.\n")
        await unzip_contents_async(zip_save_dir, output_dir)
