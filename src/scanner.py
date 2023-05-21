# coding=utf-8
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import requests
import json

with open("db.json") as data_file:
    data = json.load(data_file)


class ServiceHandler(BaseHTTPRequestHandler):
    def set_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        length = int(self.headers["Content-Length"])
        content = self.rfile.read(length)
        temp = str(content).strip('b\'')
        self.end_headers()
        return temp

    def do_POST(self):
        temp = self.set_headers()

        task = ''
        ip_start = ''
        num_hosts = 0
        target = ''
        method = ''
        headers = ''

        payload = json.loads(temp)
        for key in payload:
            if key == 'task':
                task = payload[key]
            elif key == 'ip_start':
                ip_start = payload[key]
            elif key == 'num_hosts':
                num_hosts = payload[key]
            elif key == 'target':
                target = payload[key]
            elif key == 'method':
                method = payload[key]
            elif key == 'headers':
                headers = payload[key]
            else:
                pass

        if task == 'scan':
            i = 0
            ip_parts = ip_start.split('.')
            network_ip = ip_parts[0] + '.' + ip_parts[1] + '.' + ip_parts[2] + '.'
            for num in range(num_hosts):
                scanned_ip = network_ip + str(int(ip_parts[3]) + num)
                response = os.popen(f'ping -n 1 -w 500 {scanned_ip}')
                res = response.readlines()
                print(scanned_ip, res)
                for line in res:
                    if line.count('TTL'):
                        i += 1
                        self.wfile.write((f"[{i}] Result of scanning: {scanned_ip} {res[2].encode('cp1251').decode('cp866')}").encode())
            self.wfile.write(f"Devices found in network: {i}".encode())
        elif task == 'sendhttp':
            headers_dict = dict()
            if headers:
                for header in headers.split(' '):
                    header_name = header.split(':')[0]
                    header_value = header.split(':')[1:]
                    headers_dict[header_name] = ':'.join(header_value)
            if method == "GET":
                response = requests.get(target, headers=headers_dict)
            elif method == "POST":
                response = requests.post(target, headers=headers_dict, data=payload)
            self.wfile.write((f"Response status code: {response.status_code} \n " \
                   f"Response headers: {json.dumps(dict(response.headers), indent=4, sort_keys=True)} \n" \
                   f"        Response content:\n {response.text}").encode())
            print(method, target, headers)
        else:
            self.wfile.write(("Incorrect request").encode())



server = HTTPServer(('0.0.0.0', 5000), ServiceHandler)
server.serve_forever()

