import requests
import json
import os
from dotenv import load_dotenv
from utils.logger import Logger


class PwnDoc:
    def __init__(self, args):
        load_dotenv()
        self._log = Logger("PwnDoc")
        
        if not args.username:
            args.username = os.getenv("PWNDOC_USERNAME")
        
        if not args.password:
            args.password = os.getenv("PWNDOC_PASSWORD")

        if not args.url:
            args.url = os.getenv("PWNDOC_URL")

        self._username = args.username
        self._password = args.password
        error = False

        if self._username is None:
            self._log.error("Debes especificar el nombre de usuario")
            error = True

        if self._password is None:
            self._log.error("Debes especificar la contraseña del usuario")
            error = True

        if args.url is None:
            self._log.error("Debes especificar la URL de pwndoc")
            error = True

        if error == True:
            raise Exception("Error en la autenticación")
        
        api = args.url

        self._login = f'{api}/users/token'
        self._audits = f'{api}/audits'
        self._audit = api + '/audits/{id}'
        #AUDIT  = API + '/audits/{id}'
        self._headers = {
                    'Content-type': 'application/json'
                }
        
        self.login(self._username, self._password)
    
    def _do_request(self, method:str, url:str, data=None):
        return requests.request(method=method, url=url, data=data, headers=self._headers, timeout=10)#, proxies={'https':'http://10.0.0.3:8080'}, verify=False)
    
    def _dog_get(self, url:str):
        return self._do_request('GET', url)

    def _dog_post(self, url:str, data):
        return self._do_request('POST', url, json.dumps(data))

    def login(self, username, password):
        if "Cookie" in self._headers:
            return True
        
        result = self._dog_post(self._login, {"username":username, "password":password})
        login = result.json()

        if login["status"]=="success":
            self._headers["Cookie"] = f'token=JWT {login["datas"]["token"]}'
            return True

        self._log.warning(f"Autenticación fallida: {username}")
        return False

    def get_audit(self, id:str):
        response = self._dog_get(self._audit.format(id=id))
        findings = response.json()["datas"]["findings"]
        return findings