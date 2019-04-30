from http.server import BaseHTTPRequestHandler
import socketserver
import requests
import termcolor
import sys

PORT = 8000


def error_page():
    # Show 404 page
    file = open("Error.html", "r")
    return file.read()
# ----------------------------------------------


class MyServer(BaseHTTPRequestHandler):
    def do_HEAD(self):
        return

    def get_input_value(self):
        if self.path.find('?') > 0:
            input = self.path.split("?")[1]
            if self.path.find('='):
                if self.path.find('&') > 0:
                    input_a = input.split("&")[0]
                    input_b = input.split("&")[1]
                    value_a = input_a.split("=")[1]
                    value_b = input_b.split("=")[1]
                    if input_a.split("=")[0] == "specie":
                        return value_a, value_b
                    elif input_a.split("=")[0] == "chromo":
                        return value_b, value_a
                    else:
                        return False
                else:
                    input_value = input.split("=")[1]
                    return input_value
            else:
                return False
        else:
            return False

    def do_GET(self):
        termcolor.cprint(self.requestline + "\n", 'green')
        action = self.path.split("?")[0]
    # --------------------------------------------------
        if action == "/":
            file = open("index.html","r")
            contents = file.read()
    # -------------------------------------------------------------------------------
        elif action == "/listSpecies":
            input_value = self.get_input_value()
            try:
                if input_value:
                    list_of_species = self.list_species(int(input_value))
                else:
                    list_of_species = self.list_species("all")
                file = open("listSpecies.html", "r")
                contents = file.read()
                contents += "<h1>Here is the list of species:</h1><ul>"
                for item in list_of_species:
                    contents += "<li>" + item + "</li>"
                contents += "</ul></body></html>"
            except ValueError:
                contents = error_page()
    # -------------------------------------------------------------------------------
        elif action == "/karyotype":
            file = open("karyotype.html", "r")
            contents = file.read()
            if self.get_input_value():
                kt = self.karyotype(self.get_input_value())
                contents += "Karyotype of " + self.get_input_value().upper() + ":<ul>"
                if len(kt) == 0:
                    contents += "<p><strong>It has None Karyotype</strong></p>"
                #elif str(kt[0]).split(" ")[0] != '200':
                    # Show 404 page
                 #   contents = error_page()
                else:
                    for item in kt:
                        contents += "<li>" + item + "</li>"
            contents += "</body></html>"
    # ---------------------------------------------------------------------------------
        elif action == "/chromosomeLength":
            file = open("chromosomeLength.html", "r")
            contents = file.read()
            if self.get_input_value():
                specie, chromo = self.get_input_value()
                contents += "The Chromosome " + chromo.upper() + " lenght of " + specie.upper() + ": "
                chrom_len = self.chromosomeLength(specie, chromo.upper())
                if isinstance(chrom_len,int):
                    contents += "<strong>" + str(chrom_len) + "</strong>"
                else:
                    contents = error_page()

            contents += "</body></html>"
    # ---------------------------------------------------------------------------------
        else:
            # Show 404 page
            contents = error_page()

        self.send_response(200)  # -- Status line: OK!
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(str.encode(contents)))
        self.end_headers()
        self.wfile.write(str.encode(contents))

# ---------------------------------------------------------------------------------
    def list_species(self, limit):
        server = "https://rest.ensembl.org"
        ext = "/info/species?"
        r = requests.get(server + ext, headers={"Content-Type": "application/json"})
        if not r.ok:
            r.raise_for_status()
            sys.exit()
        decoded = r.json()
        results = decoded.get('species')
        sp_list = []
        if limit == 'all':
            n = len(results)
        else:
            n = int(limit)
        i = 1
        if results:
            for specie in results:
                name = specie['name']
                sp_list.append(name)
                if i < n:
                    i += 1
                else:
                    break
        return sp_list

# ---------------------------------------------------------------------------------
    def karyotype(self, specie):
        server = "http://rest.ensembl.org"
        ext = "/info/assembly/" + specie
        r = requests.get(server + ext, headers={"Content-Type": "application/json"})
        if not r.ok:
            try:
                r.raise_for_status()
                return r.status_code
            except Exception as e:
                return e.args

        decoded = r.json()
        kt_list = decoded['karyotype']
        return kt_list

# ---------------------------------------------------------------------------------
    def chromosomeLength(self, specie, chromo):
        server = "http://rest.ensembl.org"
        ext = "/info/assembly/"+specie
        r = requests.get(server + ext, headers={"Content-Type": "application/json"})
        if not r.ok:
            try:
                r.raise_for_status()
                return r.status_code
            except Exception as e:
                return e.args

        decoded = r.json()
        results = decoded.get('top_level_region')
        if results:
            for item in results:
                if item['name'] == chromo:
                    return item['length']
            return "None"

# ---------------------------------------------------------------------------------


if __name__ == '__main__':
    # ------------------------
    # - Server MAIN program
    # ------------------------
    # -- Set the new handler
    Handler = MyServer

    # -- Open the socket server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Serving at PORT", PORT)
        # -- Main loop: Attend the client. Whenever there is a new
        # -- clint, the handler is called
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("")
            print("Stopped by the user")
            httpd.server_close()

    print("Server Stopped")
