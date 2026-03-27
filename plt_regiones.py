# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 19:12:53 2026

@author: Enzo
"""

from playwright.sync_api import sync_playwright

URL = "https://app.ceplan.gob.pe/ConsultaCEPLAN/consulta/Default.aspx"

ANIO = "2025"
MODULO = "Actividades/Proyectos"


# -------------------------------------------------
# UTILIDADES
# -------------------------------------------------

def obtener_frame_principal(page):
    for frame in page.frames:
        try:
            if "Consulta_" in frame.url and "ActProy" in frame.url:
                return frame
        except:
            pass
    return None


def esperar_frame_principal(page, timeout_ms=20000):
    transcurrido = 0
    while transcurrido < timeout_ms:
        frame = obtener_frame_principal(page)
        if frame:
            return frame
        page.wait_for_timeout(500)
        transcurrido += 500

    raise RuntimeError("No se encontró el frame principal")


def esperar_selector(frame, selector, timeout=15000):
    frame.locator(selector).wait_for(state="attached", timeout=timeout)


# -------------------------------------------------
# ACCIONES
# -------------------------------------------------

def seleccionar_dropdown(frame, selector, valor):
    esperar_selector(frame, selector)
    frame.locator(selector).select_option(label=valor)


def click_boton(frame, selector, nombre):
    print(f"[INFO] Activando botón {nombre}...")

    btn = frame.locator(selector)

    if btn.count() == 0:
        raise RuntimeError(f"No se encontró el botón {nombre}")

    try:
        btn.click(timeout=5000)
        print(f"[OK] {nombre} con click normal")
        return
    except:
        pass

    try:
        btn.click(force=True)
        print(f"[OK] {nombre} con force=True")
        return
    except:
        pass

    btn.evaluate("(el) => el.click()")
    print(f"[OK] {nombre} con JavaScript")


# -------------------------------------------------
# TABLA #tbl_data (primer nivel)
# -------------------------------------------------

def seleccionar_fila_tbl_data(frame, texto):
    print(f"[INFO] Buscando fila en tbl_data: {texto}")

    esperar_selector(frame, "#tbl_data")

    filas = frame.locator("#tbl_data tr")
    total = filas.count()

    objetivo = texto.upper()

    for i in range(total):
        fila = filas.nth(i)
        contenido = fila.inner_text().upper()

        if objetivo in contenido:
            fila.click(force=True)
            print("[OK] Fila seleccionada")
            return

    raise RuntimeError(f"No se encontró: {texto}")


# -------------------------------------------------
# TABLA #ctl00_CPH1_Mt0 (segundo nivel)
# -------------------------------------------------

def seleccionar_fila_por_codigo(frame, codigo):
    print(f"[INFO] Buscando código: {codigo}")

    esperar_selector(frame, "#ctl00_CPH1_Mt0")

    fila = frame.locator(f"#ctl00_CPH1_Mt0 tr[onclick*=\"kCod='{codigo}'\"]")

    if fila.count() == 0:
        raise RuntimeError(f"No se encontró el código {codigo}")

    fila.first.click(force=True)
    print(f"[OK] Código {codigo} seleccionado")


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        # -----------------------------------------
        # 1. Abrir portal
        # -----------------------------------------
        print("[INFO] Abriendo portal...")
        page.goto(URL, wait_until="load")
        page.wait_for_timeout(8000)

        frame = esperar_frame_principal(page)
        print("[OK] Frame inicial listo")

        # -----------------------------------------
        # 2. Año
        # -----------------------------------------
        seleccionar_dropdown(frame, "#ctl00_CPH1_DrpYear", ANIO)
        page.wait_for_timeout(5000)

        frame = esperar_frame_principal(page)

        # -----------------------------------------
        # 3. Módulo
        # -----------------------------------------
        seleccionar_dropdown(frame, "#ctl00_CPH1_DrpActProy", MODULO)
        page.wait_for_timeout(5000)

        frame = esperar_frame_principal(page)

        # -----------------------------------------
        # 4. Nivel de Gobierno
        # -----------------------------------------
        click_boton(frame, "#ctl00_CPH1_BtnTipoGobierno", "Nivel de Gobierno")
        page.wait_for_timeout(5000)

        frame = esperar_frame_principal(page)

        # -----------------------------------------
        # 5. Seleccionar R
        # -----------------------------------------
        seleccionar_fila_tbl_data(frame, "R: GOBIERNOS REGIONALES")
        page.wait_for_timeout(5000)

        frame = esperar_frame_principal(page)

        # -----------------------------------------
        # 6. Botón Gob.Reg.Mancom. (VISIBLE REAL)
        # -----------------------------------------
        click_boton(frame, "#ctl00_CPH1_BtnSector", "Gob.Reg.Mancom.")
        page.wait_for_timeout(5000)

        frame = esperar_frame_principal(page)

      
# -------------------------------------------------

if __name__ == "__main__":
    main()