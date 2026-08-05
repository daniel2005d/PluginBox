import argparse
import os
import sys
import sqlite3
from utils.logger import Logger
from uuid import uuid4


class NXCReader:
    def __init__(self, args):
        self._log = Logger("export_nxc")
        self._db = args.db
        self._file = args.file

        self.smb_options = [
            {"title": "Exportar Credenciales", "action": self.credentials},
            {"title": "Exportar Carpetas Compartidas", "action": None},
        ]

        self.rdp_options = [
            {"title": "No NLA", "action": self.get_NONLA}
        ]

        self._options = None
        if args.db == 'smb':
            self._options = self.smb_options
        elif args.db == 'rdp':
            self._options = self.rdp_options


    def execute(self, query):
        result_array = None
        with sqlite3.connect(self._file) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            result_array = [dict(zip(columns, row)) for row in rows]

        return result_array


    def mask_password(self, password: str, visibles_inicio: int = 1, visibles_final: int = 1, caracter_mascara: str = "*") -> str:
        """Enmascara una contraseña dejando visibles algunos caracteres al inicio y al final."""

        longitud = len(password)
        visibles_totales = visibles_inicio + visibles_final
        
        # Si la contraseña es tan corta que mostrar caracteres revela casi todo,
        # es más seguro ocultarla por completo.
        if longitud <= visibles_totales:
            return caracter_mascara * longitud
        
        inicio = password[:visibles_inicio]
        final = password[-visibles_final:] if visibles_final > 0 else ""
        oculto = caracter_mascara * (longitud - visibles_totales)
        
        return f"{inicio}{oculto}{final}"


    def get_NONLA(self):
        try:
            query = "Select ip,hostname, domain, nla from hosts where nla=0"
            hosts = self.execute(query)
            self._log.info(f"Total de Hosts sin NLA {len(hosts)}")
            outputfile = os.path.join('/tmp',f'{str(uuid4())}.csv')
            with open(outputfile, 'w') as fb:
                fb.write(f'Dirección IP,Nombre de Host,Dominio,NLA Habilitado \n')
                for host in hosts:
                    fb.write(f'{host["ip"]},{host["hostname"]},{host["domain"]},"No"\n')

            self._log.warning(f"Archivo generado en {outputfile}")
        except Exception as e:
            self._log.error(e)


    def credentials(self):
        query = 'select domain,username, password,credtype from users'
        credentials = self.execute(query)
        self._log.info(f"Total de Contraseñas {len(credentials)}")
        outputfile = os.path.join('/tmp',f'{str(uuid4())}.csv')
        with open(outputfile, 'w') as fb:
            for cred in credentials:
                password = self.mask_password(cred["password"])
                fb.write(f'{cred["username"]},{password},{cred["domain"]},{cred["credtype"]}\n')

        self._log.warning(f"Archivo generado en {outputfile}")

        

    def menu(self):
        while True:
            print("\n" + "=" * 30)
            print("    MENÚ PRINCIPAL")
            print("=" * 30)

            for index, option in enumerate(self._options, start=1):
                print(f"{index}. {option['title']}")

            exit_option = len(self._options) + 1
            print(f"{exit_option}. Salir")
            
            option = input(f"\nSelecciona una opción (1-{exit_option}): ").strip()

            if not option.isdigit():
                print("\n[!] Entrada inválida. Introduce un número.")
                continue

            option_num = int(option)
            if option_num == exit_option:
                print("\n[+] Saliendo del menú...")
                break

            # Validar que el número esté dentro del rango de opciones disponibles
            if 1 <= option_num <= len(self._options):
                # Obtener el diccionario correspondiente y ejecutar su función asociada
                selected_action = self._options[option_num - 1]["action"]
                print(f"\n[>] Ejecutando: {self._options[option_num - 1]['title']}...")
                
                # Invocamos la función directamente
                selected_action()
            else:
                print(f"\n[!] Opción fuera de rango. Elige entre 1 y {exit_option}.")
        
    def start(self):
        if not os.path.exists(self._file):
            self.log.error(f'El archivo {self._file} no existe')
            return

        self.menu()
        


    


def run(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--db",choices=['smb','ldap','rdp'], required=True, help="SMB DB")
    parser.add_argument("file")
    parse_args = parser.parse_args(args)
    nxc = NXCReader(parse_args)
    nxc.start()
    