from uuid import uuid4
import requests
import json
import argparse
from pwndoc import PwnDoc
from utils.logger import Logger

log = Logger("pwdoc_exporter")

def create(args):
    audit_id = args.id
    file_path = f'/tmp/{str(uuid4())}.md'
    pwndoc = PwnDoc(args)
    findings = pwndoc.get_audit(audit_id)

    markdown = open(file_path,'w')
    markdown.write("|Nombre|POC|CVSS|\n")
    markdown.write("|--|--|--|\n")
    for f in findings:
        log.info(f'[-] {f["title"]}')
        markdown.write(f'|{f["title"]}|{f["poc"]}|{f["cvssv3"]}\n')

    markdown.close()
    log.warning(f"Guardado en {file_path}")


def run(args):
    parser = argparse.ArgumentParser(description="Obtiene el listado de vulnerabilidades y lo exporta a un markdown.")
    parser.add_argument('-u','--username', type=str, required=False)
    parser.add_argument('-p','--password', type=str, required=False)
    parser.add_argument('-i','--id', type=str, help='Audit Id')
    parser.add_argument('--url', required=False, help="Url de la API de PwnDoc.")
    parse_args = parser.parse_args(args)
    create(parse_args)