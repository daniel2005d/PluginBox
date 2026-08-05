import requests
import json
import sys
from os import path
import argparse
from pwndoc import PwnDoc
from utils.logger import Logger

log = Logger("searchpwndoc")


def searchfinding(args):
    pwn = PwnDoc(args)
    audits = pwn.get_audits()
    text = args.text_to_find
    for a in audits:
        findings = pwn.get_audit(a["_id"])

        if findings:
            for f in findings:
                title = f["title"]
                if text.lower() in title.lower():
                    log.warning(f'{a["name"]} {a["_id"]}')
                    
                    

def run(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-t","--text-to-find", required=True, help="Texto a buscar dentro de las auditorias")
    parser.add_argument('-u','--username', type=str, required=False)
    parser.add_argument('-p','--password', type=str, required=False)
    parser.add_argument('--url', required=False, help="Url de la API de PwnDoc.")
    parse_args = parser.parse_args(args)
    searchfinding(parse_args)
