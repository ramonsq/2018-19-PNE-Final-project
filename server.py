from http.server import BaseHTTPRequestHandler
import socketserver
import requests
import termcolor
import json

PORT = 8000


def error_page():
    # This function return the html code of an error page
    file = open("Error.html", "r")
    return file.read()
# ----------------------------------------------


class MyServer(BaseHTTPRequestHandler):
    JSON = False

    def verify_client(self):
        if self.path.split('?')[1].endswith('&json=1'):
            self.JSON = True
            return self.path.split('?')[1].replace('&json=1', '')
        elif self.path.split('?')[1].endswith('json=1'):
            self.JSON = True
            return self.path.split('?')[1].replace('json=1', '')
        else:
            return self.path.split('?')[1]

    def get_list_input(self):
        if self.path.find('?') > 0:
            user_input = self.verify_client()
            if self.path.find('='):
                if self.path.find('&') > 0:
                    input_a = user_input.split("&")[0]
                    input_b = user_input.split("&")[1]
                    input_c = user_input.split("&")[2]
                    value_a = input_a.split("=")[1]
                    value_b = input_b.split("=")[1]
                    value_c = input_c.split("=")[1]
                    return value_a, value_b, value_c
                else:
                    return False
            else:
                return False
        else:
            return False

    def get_input_value(self):
        if self.path.find('?') > 0:
            # user_input = self.path.split("?")[1]
            user_input = self.verify_client()
            if len(user_input) == 0:
                return False
            if user_input.find('='):
                if user_input.find('&') > 0:
                    input_a = user_input.split("&")[0]
                    input_b = user_input.split("&")[1]
                    value_a = input_a.split("=")[1]
                    value_b = input_b.split("=")[1]
                    if input_a.split("=")[0] == "specie":
                        return value_a, value_b
                    elif input_a.split("=")[0] == "chromo":
                        return value_b, value_a
                    else:
                        return False
                else:
                    input_value = user_input.split("=")[1]
                    return input_value
            else:
                return False
        else:
            return False

    def do_GET(self):
        termcolor.cprint(self.requestline + "\n", 'green')
        action = self.path.split("?")[0]
    # ------------------------------------------------------------------> INDEX PAGE
        if action == "/":
            file = open("index.html", "r")
            contents = file.read()
    # ---------------------------------------------------------------------------> BASIC
        elif action == "/listSpecies":
            input_value = self.get_input_value()
            try:
                if input_value:
                    list_of_species = self.list_species(int(input_value))
                else:
                    list_of_species = self.list_species("all")
                if self.JSON:
                    contents = json.dumps(list_of_species)
                else:
                    file = open("listSpecies.html", "r")
                    contents = file.read()
                    contents += "<h1>Here is the list of species:</h1><ul>"
                    for item in list_of_species:
                        contents += "<li>" + item + "</li>"
                    contents += "</ul></body></html>"
            except ValueError:
                if self.JSON:
                    print("Error: There is something wrong with your request!")
                else:
                    contents = error_page()
    # -------------------------------------------------------------------------------
        elif action == "/karyotype":
            file = open("karyotype.html", "r")
            contents = file.read()
            input_value = self.get_input_value()
            if input_value:
                kt = self.karyotype(input_value)
                if self.JSON:
                    contents = json.dumps(kt)
                else:
                    contents += "Karyotype of " + input_value.upper() + ":<ul>"
                    if not isinstance(kt, list):
                        # Show 404 page
                        print(kt)
                        contents = error_page()
                    elif len(kt) == 0:
                        contents += "<p><strong>It has None Karyotype</strong></p>"
                    else:
                        for item in kt:
                            contents += "<li>" + item + "</li>"
            if not self.JSON:
                contents += "</body></html>"
    # ---------------------------------------------------------------------------------
        elif action == "/chromosomeLength":
            file = open("chromosomeLength.html", "r")
            contents = file.read()
            input_value = self.get_input_value()
            if input_value:
                specie, chromo = input_value
                if self.JSON:
                    contents = json.dumps(self.chromosomeLength(specie, chromo.upper()))
                else:
                    contents += "The Chromosome " + chromo.upper() + " lenght of " + specie.upper() + ": "
                    chrom_len = self.chromosomeLength(specie, chromo.upper())
                    if isinstance(chrom_len, int):
                        contents += "<strong>" + str(chrom_len) + "</strong>"
                    else:
                        contents = error_page()

    # ---------------------------------------------------------------------------------> M E D I U M
        elif action == "/geneSeq":
            file = open("geneSeq.html", "r")
            contents = file.read()
            input_value = self.get_input_value()
            if input_value:
                gene = input_value
                if self.JSON:
                    contents = json.dumps(self.geneSeq(gene.upper()))
                else:
                    contents += "Sequence of human gene " + gene.upper() + ": "
                    seq = self.geneSeq(gene.upper())
                    if isinstance(seq, str):
                        contents += "<br><div style=\"overflow-wrap: break-word;\">"
                        contents += "<strong>" + str(seq) + "</strong></div>"
                    else:
                        contents = error_page()
            if not self.JSON:
                contents += "</body></html>"
    # --------------------------------------------------------------------------------
        elif action == "/geneInfo":
            file = open("geneInfo.html", "r")
            contents = file.read()
            input_value = self.get_input_value()
            if input_value:
                gene = input_value
                if self.JSON:
                    contents = json.dumps(self.geneInfo(gene.upper()))
                else:
                    contents += "<h2>Information about human gene " + gene.upper() + ":</h2>"
                    gene_info = self.geneInfo(gene.upper())
                    if isinstance(gene_info, dict):
                        contents += "<p> ID: " + gene_info['id'] + "</p>"
                        contents += "<p> Start: " + gene_info['start'] + "</p>"
                        contents += "<p> End: " + gene_info['end'] + "</p>"
                        contents += "<p> Lenght: " + gene_info['lenght'] + "</p>"
                        contents += "<p> Chromosome: " + gene_info['chromo'] + "</p>"
                    else:
                        contents = error_page()
            if not self.JSON:
                contents += "</body></html>"
    # --------------------------------------------------------------------------------
        elif action == "/geneCalc":
            file = open("geneCalc.html", "r")
            contents = file.read()
            input_value = self.get_input_value()
            if input_value:
                gene = input_value
                if self.JSON:
                    contents = json.dumps(self.geneCalc(gene.upper()))
                else:
                    contents += "<h2>Information about human gene " + gene.upper() + " bases:</h2>"
                    bases = self.geneCalc(gene.upper())
                    if isinstance(bases, dict):
                        contents += "<h4>Lenghts:</h4><ul>"
                        contents += "<li> A: " + bases['Base A'] + "</li>"
                        contents += "<li> C: " + bases['Base C'] + "</li>"
                        contents += "<li> G: " + bases['Base G'] + "</li>"
                        contents += "<li> T: " + bases['Base T'] + "</li></ul>"
                        contents += "<h4>Percentages:</h4><ul>"
                        contents += "<li> A: " + bases['Percentage A'] + "</li>"
                        contents += "<li> C: " + bases['Percentage C'] + "</li>"
                        contents += "<li> G: " + bases['Percentage G'] + "</li>"
                        contents += "<li> T: " + bases['Percentage T'] + "</li></ul>"
                    else:
                        contents = error_page()
            if not self.JSON:
                contents += "</body></html>"
    # --------------------------------------------------------------------------------
        elif action == "/geneList":
            file = open("geneList.html", "r")
            contents = file.read()
            input_value = self.get_input_value()
            if input_value:
                chromo, start, end = self.get_list_input()
                if self.JSON:
                    contents = json.dumps(self.geneList(chromo, start, end))
                else:
                    contents += "<h2>Genes located in the chromosome " + chromo.upper() + " </h2>"
                    names = self.geneList(chromo, start, end)
                    if isinstance(names, list):
                        contents += "<ul>"
                        for item in names:
                            contents += "<li>" + item + "</li>"
                        contents += "</ul>"
                    else:
                        contents = error_page()
            if not self.JSON:
                contents += "</body></html>"

    # --------------------------------------------------------------------------------
        else:
            # Show 404 page
            contents = error_page()

        self.send_response(200)  # -- Status line: OK!
        if self.JSON:
            self.send_header('Content-Type', 'application/json')
        else:
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
    def geneSeq(self, gene):
        try:
            server = "http://rest.ensembl.org"
            ext = "/xrefs/symbol/human/" + gene
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})
            if not r.ok:
                r.raise_for_status()
            decoded = r.json()
            id = decoded[0].get('id')
            server = "http://rest.ensembl.org"
            ext = "/sequence/id/" + id
            r = requests.get(server + ext, headers={"Content-Type": "text/plain"})
            if not r.ok:
                r.raise_for_status()
            print("Seq: " + str(type(r.text)))
            return r.text
        except Exception as e:
            return e.args

# ------------------------------------------------------------------------------------
    def geneInfo(self, gene):
        try:
            server = "http://rest.ensembl.org"
            ext = "/xrefs/symbol/human/" + gene
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})
            if not r.ok:
                r.raise_for_status()
            decoded = r.json()
            gene_id = decoded[0].get('id')
            server = "https://rest.ensembl.org"
            ext = "/sequence/id/" + gene_id + "?"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})
            if not r.ok:
                r.raise_for_status()
            decoded = r.json()
            cad = decoded['desc']
            res = {
                "id": decoded['query'],
                "start": str(cad.split(":")[3]),
                "end": str(cad.split(":")[4]),
                "lenght": str(len(decoded['seq'])),
                "chromo": str(cad.split(":")[2])
            }
            return res
        except Exception as e:
            return e.args

# ------------------------------------------------------------------------------------
    def geneCalc(self, gene):
        try:
            server = "http://rest.ensembl.org"
            ext = "/xrefs/symbol/human/" + gene
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})
            if not r.ok:
                r.raise_for_status()
            decoded = r.json()
            gene_id = decoded[0].get('id')
            server = "https://rest.ensembl.org"
            ext = "/sequence/id/" + gene_id + "?"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})
            if not r.ok:
                r.raise_for_status()
            data = {
                "Base A": str(r.text.count('A')),
                "Base C": str(r.text.count('C')),
                "Base G": str(r.text.count('G')),
                "Base T": str(r.text.count('T')),
                "Percentage A": str('{:0.2f}'.format(100 * int(r.text.count('A')) / len(r.text))) + "%",
                "Percentage C": str('{:0.2f}'.format(100 * int(r.text.count('C')) / len(r.text))) + "%",
                "Percentage G": str('{:0.2f}'.format(100 * int(r.text.count('G')) / len(r.text))) + "%",
                "Percentage T": str('{:0.2f}'.format(100 * int(r.text.count('T')) / len(r.text))) + "%"
            }
            return data
        except Exception as e:
            return e.args

# ------------------------------------------------------------------------------------
    def geneList(self, chromo, start, end):
        try:
            server = "http://rest.ensembl.org"
            ext = "/overlap/region/human/" + str(chromo) + ":" + str(start) + "-" + str(end)
            ext += "?content-type=application/json;feature=gene"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})
            if not r.ok:
                r.raise_for_status()
            results = r.json()
            sp_list = []
            if results:
                for gene in results:
                    name = gene['external_name']
                    sp_list.append(name)
            return sp_list
        except Exception as e:
            return e.args


# -----------------------------
if __name__ == '__main__':
    # ------------------------
    # - Server MAIN program
    # -- Set the new handler
    Handler = MyServer
    socketserver.TCPServer.allow_reuse_address = True
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
