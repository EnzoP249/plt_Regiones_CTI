# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 19:12:53 2026

@author: Enzo
"""

from playwright.sync_api import sync_playwright

URL = "https://app.ceplan.gob.pe/ConsultaCEPLAN/consulta/Default.aspx"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("[INFO] Abriendo portal...")
        page.goto(URL, wait_until="load", timeout=60000)
        page.wait_for_timeout(8000)

        print("[INFO] URL actual:", page.url)
        print("[INFO] Título:", page.title())

        input("Presiona Enter para cerrar...")
        browser.close()

if __name__ == "__main__":
    main()
    
    
    