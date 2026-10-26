#!/usr/bin/env python3
"""Explorateur DPE : petit serveur local (Python 3, bibliothèque standard uniquement).

    python3 serveur_dpe.py          # ouvre http://localhost:8765 dans le navigateur
    python3 serveur_dpe.py --test   # vérifie l'API ADEME (champs, total, pagination, lien rapport)

Le serveur sert index.html et relaie (proxy) les appels vers data.ademe.fr et
geo.api.gouv.fr, au cas où le navigateur refuserait les appels directs (CORS).
"""
import argparse
import http.server
import json
import ssl
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

ICI = Path(__file__).resolve().parent
HOTES_AUTORISES = {"data.ademe.fr", "geo.api.gouv.fr"}
API = "https://data.ademe.fr/data-fair/api/v1/datasets/"
LOGEMENT = "meg-83tjwtg8dyz4vv7h1dqe"
TERTIAIRE = "j9ol0fwjqckyf49vr29nknbu"
UA = "ExplorateurDPE/1.0 (Agence des Lices)"


def contexte_ssl():
    try:
        import certifi  # facultatif : corrige les certificats manquants de Python sur macOS
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL = contexte_ssl()


def telecharger(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout, context=SSL) as r:
        return r.status, r.headers.get("Content-Type", "application/json"), r.read()


class Gestionnaire(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ICI), **kwargs)

    def log_message(self, fmt, *args):
        if "/proxy" not in self.path:
            super().log_message(fmt, *args)

    def do_GET(self):
        chemin = urllib.parse.urlsplit(self.path)
        if chemin.path == "/proxy/ping":
            return self.repondre(200, "application/json", b'{"ok":true}')
        if chemin.path == "/proxy":
            cible = urllib.parse.parse_qs(chemin.query).get("url", [""])[0]
            hote = urllib.parse.urlsplit(cible).hostname
            if not cible.startswith("https://") or hote not in HOTES_AUTORISES:
                return self.repondre(400, "text/plain", "Hôte non autorisé".encode())
            try:
                statut, ctype, corps = telecharger(cible)
            except urllib.error.HTTPError as e:
                statut, ctype, corps = e.code, e.headers.get("Content-Type", "text/plain"), e.read()
            except Exception as e:  # réseau, délai dépassé…
                return self.repondre(504, "text/plain", f"Proxy : {e}".encode())
            return self.repondre(statut, ctype, corps)
        return super().do_GET()

    def repondre(self, statut, ctype, corps):
        self.send_response(statut)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corps)


def lignes(dataset, **params):
    return API + dataset + "/lines?" + urllib.parse.urlencode(params)


def lire(url):
    return json.loads(telecharger(url)[2])


def test():
    ok = True
    print("1) CORS : appel direct depuis un navigateur autorisé ?")
    req = urllib.request.Request(lignes(LOGEMENT, size=1), headers={"Origin": "http://localhost:8765", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=SSL) as r:
        acao = r.headers.get("Access-Control-Allow-Origin")
    print(f"   Access-Control-Allow-Origin : {acao!r} ->",
          "la page peut appeler l'API en direct" if acao in ("*", "http://localhost:8765") else "proxy nécessaire (utilisez ce serveur)")

    print("2) Champs présents dans le schéma de l'API")
    attendus = {
        LOGEMENT: "numero_dpe date_etablissement_dpe type_batiment adresse_ban code_postal_ban nom_commune_ban code_insee_ban "
                  "complement_adresse_logement surface_habitable_logement periode_construction type_energie_principale_chauffage "
                  "etiquette_dpe conso_5_usages_par_m2_ep etiquette_ges emission_ges_5_usages_par_m2 cout_total_5_usages _geopoint",
        TERTIAIRE: "numero_dpe date_etablissement_dpe adresse_ban code_insee_ban secteur_activite surface_utile conso_kwhep_m2_an "
                   "emission_ges_kg_co2_m2_an frais_annuel_energie_n1 methode_dpe etiquette_dpe etiquette_ges _geopoint",
    }
    for ds, champs in attendus.items():
        cles = {c["key"] for c in lire(API + ds).get("schema", [])}
        manquants = [c for c in champs.split() if c not in cles]
        ok &= not manquants
        print(f"   {ds} : {'tous présents' if not manquants else 'ABSENTS : ' + ', '.join(manquants)}")

    print("3) Recherche test : Rennes, maisons, octobre 2026")
    url = lignes(LOGEMENT, size=1000, select="numero_dpe,date_etablissement_dpe,_geopoint", sort="-date_etablissement_dpe",
                 code_insee_ban_eq="35238", type_batiment_in="maison",
                 date_etablissement_dpe_gte="2026-10-01", date_etablissement_dpe_lte="2026-10-31")
    page = lire(url)
    total, recus, premier = page.get("total"), [], None
    while True:
        recus += page.get("results", [])
        if not page.get("next") or not page.get("results"):
            break
        page = lire(page["next"])
    if recus:
        premier = recus[0]["numero_dpe"]
    ok &= total == len(recus)
    print(f"   total annoncé par l'API : {total} · DPE reçus après pagination : {len(recus)} ->",
          "OK" if total == len(recus) else "ÉCART")
    if recus:
        print(f"   DPE le plus récent de la sélection : {recus[0]['date_etablissement_dpe']} ({premier})")

    print("4) Dernier DPE publié (tous logements)")
    j = lire(lignes(LOGEMENT, size=1, select="date_etablissement_dpe", sort="-date_etablissement_dpe"))
    print("   ", j["results"][0]["date_etablissement_dpe"] if j.get("results") else "?")

    if premier:
        print("5) Lien « Rapport ADEME »")
        rapport = "https://observatoire-dpe-audit.ademe.fr/afficher-dpe/" + premier
        try:
            req = urllib.request.Request(rapport, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60, context=SSL) as r:
                html = r.read().decode("utf-8", "replace")
            print(f"   {rapport} -> HTTP {r.status}", "(n° trouvé dans la page)" if premier in html else
                  "(page servie ; le contenu se charge en JavaScript, ouvrez-la dans le navigateur pour vérifier)")
        except Exception as e:
            ok = False
            print(f"   {rapport} -> ERREUR {e}")
    print("\nRésultat :", "tout est bon" if ok else "à vérifier (voir ci-dessus)")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--test", action="store_true", help="tester l'API ADEME puis quitter")
    p.add_argument("--no-browser", action="store_true", help="ne pas ouvrir le navigateur")
    a = p.parse_args()
    if a.test:
        sys.exit(test())
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), Gestionnaire)
    url = f"http://localhost:{a.port}/"
    print(f"Explorateur DPE : {url}  (Ctrl+C pour arrêter)")
    if not a.no_browser:
        threading.Timer(0.6, webbrowser.open, [url]).start()
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt.")


if __name__ == "__main__":
    main()
