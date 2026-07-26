import sys
import requests
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urlparse
from PIL import Image, ImageDraw, ImageFont
import os
from uuid import uuid4
import argparse
from time import sleep
from utils.logger import Logger
from snapshot.data import DBData
# from redops.utils.colors import Color
# from redops.utils.folder import Folder
# from data import DBData

class Browser:

    def __init__(self, visible=True):
        self._headers = {}
        
    
    def get_snapshot(self):
        return self._driver.get_screenshot_as_base64()
    
    def get_response(self, url):
        for request in self._driver.requests:
            if request.url == url:
                return request.response
    
    def close(self):
        self._driver.quit()

from flask import Flask, render_template, request
from base64 import b64encode
from pathlib import Path

class API:

    def __init__(self, args):
        self.app = Flask(__name__)
        db_file = os.path.join(args.output,'data.db')
        self._data = DBData(db_file)
        self.register_routes()
    
    def register_routes(self):
        @self.app.route('/')
        def index():
            ext = request.args.get('q', '')
            if ext:
                pages = self._data.get_by_extension(ext)
            else:
                pages = self._data.get_all()
            
            items = []
            extensions = set()
            for page in pages:
                if not page.content.replace('\t','').replace('\n','').strip():
                    continue
                if os.path.exists(page.path):
                
                    image = None
                    file_path = Path(page.url)
                    name = file_path.name
                    extension = file_path.suffix
                    extensions.add(extension)

                    with open(page.path, 'rb') as img:
                        image = b64encode(img.read()).decode('utf-8')

                    items.append(
                        {
                            "url":page.url,
                            "image":image
                            
                        }
                    )
            return render_template("index.html", pages=items, extensions=extensions)
    
    def run(self):
        self.app.debug = True
        self.app.run(host="0.0.0.0")
    

        

class Main:
    def __init__(self, args):
        self._log = Logger("http_snapshot")
        self._sleep = args.sleep
        self._filelist = args.domains
        self._saved_images={}
        self._headers = None
        self._invalid_extensions = [".svg",".png",".gif",".jpg",".jpeg",".webp",".ttf","woff","woff2",".mp4"]
        if not os.path.isdir(args.output):
            self._log.error(f"La salida {args.output} debe ser un directorio.")
            sys.exit(1)
        self._folder = args.output
        db_file = os.path.join(self._folder,'data.db')

        if args.tls:
            self._schema = 'https://'
        else:
            self._schema = 'http://'

        if args.H:
            self._headers = args.H
        
        if not os.path.exists(self._folder):
            os.makedirs(self._folder)

        self._data = DBData(db_file)
 
    def _create_folder(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        output_folder = os.path.join(self._folder,parsed_url.hostname,str(parsed_url.port))
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        return output_folder
    

    def _create_html(self):
        root_dir = self._folder
        output_file = os.path.join(root_dir, "index.html")
        thumb_size = 150  # ancho en píxeles para mostrar en HTML
        image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
        images = self._data.get_all()
        # images = []
        # # Recorrer directorio y subdirectorios
        # for subdir, dirs, files in os.walk(root_dir):
        #     for file in files:
        #         if file.lower().endswith(image_extensions):
        #             img_path = os.path.join(subdir, file)
        #             rel_path = os.path.relpath(img_path, root_dir)
        #             # El nombre del subdirectorio que contiene la imagen es el dominio
        #             subdir_name = os.path.basename(subdir)
        #             images.append((rel_path, subdir_name))

        # Crear HTML
        html_content = """<!DOCTYPE html>
        <html lang="es">
        <head>
        <meta charset="UTF-8">
        <title>Galería de Imágenes</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
     <style>
        .img-thumb {
            width: 100%;
            max-width: 200px;
            height: auto;
            transition: transform 0.3s;
            border-radius: 5px;
            margin: 0 auto;
            display: block;
        }
        .img-thumb:hover {
            transform: scale(1.1);
        }
        .card {
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            transition: transform 0.3s;
            text-align: center;
            background: #fff;
        }
        .card:hover {
            transform: scale(1.05);
        }
        .card-title {
            margin-top: 10px;
            font-size: 0.95em;
            color: #333;
            word-break: break-word;
        }
        </style>
        </head>
        <body class="container my-4">
        <h1 class="mb-4 text-center">Galería de Imágenes</h1>
        <div class="row"  id="gallery">
        """

        for row in images:
            abs_path = row.path
            domain = row.url
            html_content += f'''
            <div class="col-6 col-md-4 col-lg-3">
            <div class="card p-2">
                <a href="{domain}" target="_blank">
                    <img src="file:///{abs_path}" alt="{domain}"  class="img-thumb">
                </a>
                 <div class="card-title">{domain}</div>
            </div>
                 
            </div>
            '''

        html_content += "</div></body></html>"

        # Guardar HTML
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Galería generada en {output_file}")
    
    def _create_error_page(self, path:str, text:str)->None:
        # Configuración
        width, height = 500, 200
        background_color = (255, 0, 0)  # Rojo
        text_color = (255, 255, 255)    # Blanco
        
        # Crear imagen
        img = Image.new("RGB", (width, height), color=background_color)
        draw = ImageDraw.Draw(img)

        # Elegir fuente y tamaño
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        # Calcular tamaño del texto usando textbbox
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Centrar texto
        x = (width - text_width) / 2
        y = (height - text_height) / 2

        # Dibujar texto
        draw.text((x, y), text, fill=text_color, font=font)

        # Guardar imagen
        img.save(os.path.join(path, "error.png"))

    def _validate_extension(self, url:str) -> bool:
        for ext in self._invalid_extensions:
            if url.lower().endswith(ext):
                return False
        
        return True

    def _get_page_name(self, url:str)->str:
        fragments = url.split('/')
        return fragments[-1:][0]
    
    async def scan(self):
        #self._create_html()
        # Leer lista de dominios
        domains = open(self._filelist, 'r').readlines()

        # Archivo para guardar dominios ya procesados
        pages = self._data.get_pages()
        processed_domains = set(p.strip() for p in pages)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            for index, d in enumerate(domains):
                output_folder = None
                try:
                    domain = d.strip()
                    if not self._validate_extension(domain):
                        continue

                    
                    if not domain.startswith('http'):
                        domain = f'{self._schema}{domain}'
                    
                    if not domain or domain in processed_domains:
                        continue  # Saltar dominios ya procesados

                    output_folder = self._create_folder(domain)
                    self._log.info(domain)
                    ## Primer Request
                    response = requests.get(domain, timeout=1000)
                    self._log.warning(f'{domain} {response.status_code} {response.reason}')
                    
                    if response.text:
                        await page.goto(domain, timeout=50000, wait_until="domcontentloaded")
                        await page.wait_for_selector("body")
                        title = await page.title()
                        body = await page.text_content("body")
                        if not title:
                            title = self._get_page_name(domain)

                        image_name = os.path.join(output_folder, f'{title}.png')
                        await page.screenshot(path=image_name, full_page=True)

                        self._data.add(domain, body, image_name)
                        processed_domains.add(domain)
                    else:
                        raise Exception('Página vacia')

                except Exception as e:
                    self._log.error(e)
                    if output_folder:
                        self._create_error_page(output_folder, str(e))

            self._create_html()

               
async def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-l","--domains", required=False, help="File with urls list")
    parser.add_argument("-s","--sleep", required=False, help="Time to sleep between each request. Default 2", default=2, type=int)
    parser.add_argument("-H", action="append", help="Additional headers")
    parser.add_argument("--hidden", action="store_false", help="Hide Browser.")
    parser.add_argument("-o","--output",  help="Screenshots folder.", required=True)
    parser.add_argument("--tls",action="store_true",  help="Use HTTPs if schema is not defined on file")
    parser.add_argument("--api",action="store_true",  help="Run api to check results")
    parse_args = parser.parse_args(args)

    if parse_args.api:
        a = API(parse_args)
        a.run()
    else:
        m = Main(parse_args)
        await m.scan()

def run(args):
    asyncio.run(main(args))
    




# def main():
#     asyncio.run(aync_main())


# if __name__ == '__main__':
#     asyncio.run(aync_main())