#!/usr/bin/env python3
"""Explorateur DPE : petit serveur local (Python 3, bibliothèque standard uniquement).

    python3 serveur_dpe.py          # ouvre http://localhost:8765 dans le navigateur
    python3 serveur_dpe.py --test   # vérifie l'API ADEME (champs, total, pagination, lien rapport)
    python3 serveur_dpe.py --veille-minutes 30   # veille plus fréquente (0 = désactivée)

Le serveur sert index.html et relaie (proxy) les appels vers data.ademe.fr, geo.api.gouv.fr
et recherche-entreprises.api.gouv.fr, au cas où le navigateur refuserait les appels directs (CORS).
Il fait aussi tourner une veille : toutes les N minutes, il mémorise dans veille_dpe.json les DPE
de Rennes Métropole publiés ces 14 derniers jours et signale les nouveaux dans la page.
"""
import argparse
import datetime
import http.server
import json
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

ICI = Path(__file__).resolve().parent
HOTES_AUTORISES = {"data.ademe.fr", "geo.api.gouv.fr", "recherche-entreprises.api.gouv.fr"}
EPCI_RENNES = "https://geo.api.gouv.fr/epcis/243500139/communes?fields=nom,code"
FICHIER_VEILLE = ICI / "veille_dpe.json"
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
        if chemin.path == "/api/status":
            return self.repondre(200, "application/json", json.dumps(VEILLE.etat()).encode())
        if chemin.path == "/api/recent":
            return self.repondre(200, "application/json", json.dumps(VEILLE.recents()).encode())
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


class Veille(threading.Thread):
    """Interroge l'ADEME à intervalle régulier et garde les DPE récents de Rennes Métropole."""

    JOURS = 14
    SELECT = {
        LOGEMENT: "numero_dpe,date_etablissement_dpe,type_batiment,adresse_ban,surface_habitable_logement,etiquette_dpe,_geopoint",
        TERTIAIRE: "numero_dpe,date_etablissement_dpe,adresse_ban,surface_utile,etiquette_dpe,secteur_activite,_geopoint",
    }

    def __init__(self, minutes):
        super().__init__(daemon=True)
        self.minutes = minutes
        self.verrou = threading.Lock()
        self.memoire = {}
        self.statut = {"enabled": minutes > 0, "running": False, "total": 0, "new": 0, "last_run": None,
                       "last_success": None, "error": None, "interval_minutes": minutes}
        try:
            donnees = json.loads(FICHIER_VEILLE.read_text(encoding="utf-8"))
            self.memoire = donnees.get("dpe", {})
            self.statut["last_success"] = donnees.get("last_success")
        except (OSError, ValueError):
            pass
        self.statut["total"] = len(self.memoire)

    def etat(self):
        with self.verrou:
            return dict(self.statut)

    def recents(self):
        with self.verrou:
            items = sorted(self.memoire.values(), key=lambda r: (r.get("vu_le", ""), r.get("date", "")), reverse=True)
        return items[:200]

    def run(self):
        while True:
            self.passe()
            time.sleep(self.minutes * 60)

    def passe(self):
        with self.verrou:
            self.statut.update(running=True, last_run=datetime.datetime.now().isoformat(timespec="seconds"))
        try:
            codes = [c["code"] for c in lire(EPCI_RENNES)] or ["35238"]
            depuis = (datetime.date.today() - datetime.timedelta(days=self.JOURS)).isoformat()
            maintenant = datetime.datetime.now().isoformat(timespec="seconds")
            premiere_passe = not self.memoire
            nouveaux = 0
            for ds, select in self.SELECT.items():
                url = lignes(ds, size=1000, select=select, sort="-date_etablissement_dpe",
                             date_etablissement_dpe_gte=depuis, code_insee_ban_in=",".join(codes))
                for _ in range(20):   # au plus 20 000 lignes par passe
                    page = lire(url)
                    for r in page.get("results", []):
                        n = r.get("numero_dpe")
                        if not n or n in self.memoire:
                            continue
                        lat = lon = None
                        try:
                            lat, lon = (float(x) for x in str(r.get("_geopoint", "")).split(","))
                        except ValueError:
                            pass
                        self.memoire[n] = {
                            "numero": n, "date": r.get("date_etablissement_dpe"),
                            "type": "tertiaire" if ds == TERTIAIRE else r.get("type_batiment"),
                            "adresse": r.get("adresse_ban"), "secteur": r.get("secteur_activite"),
                            "surface": r.get("surface_utile" if ds == TERTIAIRE else "surface_habitable_logement"),
                            "etiquette": r.get("etiquette_dpe"), "lat": lat, "lon": lon, "vu_le": maintenant,
                        }
                        nouveaux += 1
                    if not page.get("next") or not page.get("results"):
                        break
                    url = page["next"]
            # On oublie ce qui est sorti de la fenêtre de 14 jours (+ 30 jours de marge).
            limite = (datetime.date.today() - datetime.timedelta(days=self.JOURS + 30)).isoformat()
            self.memoire = {k: v for k, v in self.memoire.items() if (v.get("date") or "") >= limite}
            FICHIER_VEILLE.write_text(json.dumps({"last_success": maintenant, "dpe": self.memoire}, ensure_ascii=False), encoding="utf-8")
            with self.verrou:
                self.statut.update(total=len(self.memoire), new=0 if premiere_passe else nouveaux,
                                   last_success=maintenant, error=None)
            print(f"[veille] {maintenant} : {nouveaux} DPE ajoutés, {len(self.memoire)} en mémoire")
        except Exception as e:  # réseau, API…
            with self.verrou:
                self.statut["error"] = str(e)[:200]
            print(f"[veille] erreur : {e}")
        finally:
            with self.verrou:
                self.statut["running"] = False


VEILLE = Veille(0)


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
    p.add_argument("--veille-minutes", type=int, default=60, help="intervalle de la veille automatique (0 = désactivée)")
    a = p.parse_args()
    if a.test:
        sys.exit(test())
    global VEILLE
    VEILLE = Veille(max(0, a.veille_minutes))
    if a.veille_minutes > 0:
        VEILLE.start()
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
