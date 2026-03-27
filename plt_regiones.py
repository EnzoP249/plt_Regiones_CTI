# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 19:12:53 2026

@author: Enzo
"""

from playwright.sync_api import sync_playwright
import re

URL = "https://app.ceplan.gob.pe/ConsultaCEPLAN/consulta/Default.aspx"

ANIO = "2025"
MODULO = "Actividades/Proyectos"
OBJETIVO_NIVEL = "R: GOBIERNOS REGIONALES"
OBJETIVO_PLIEGO = "440: GOBIERNO REGIONAL DEL DEPARTAMENTO DE AMAZONAS"
OBJETIVO_OEI = "OEI.01-440: GARANTIZAR LA CALIDAD DE LOS SERVICIOS DE SALUD EN EL DEPARTAMENTO"
OBJETIVO_AEI = "AEI.01.01-440: ATENCIÓN INTEGRAL Y OPORTUNA PARA REDUCIR LA DESNUTRICIÓN CRÓNICA EN LA POBLACIÓN INFANTIL"


# -------------------------------------------------
# FRAMES
# -------------------------------------------------

def obtener_frame_principal(page):
    for frame in page.frames:
        try:
            if "Consulta_" in frame.url and "ActProy" in frame.url:
                return frame
        except Exception:
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


# -------------------------------------------------
# UTILIDADES
# -------------------------------------------------

def esperar_selector(frame, selector, timeout=15000):
    frame.locator(selector).wait_for(state="attached", timeout=timeout)


def normalizar_texto(texto):
    return re.sub(r"\s+", " ", texto).strip().upper()


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
    except Exception:
        pass

    try:
        btn.click(force=True)
        print(f"[OK] {nombre} con force=True")
        return
    except Exception:
        pass

    btn.evaluate("(el) => el.click()")
    print(f"[OK] {nombre} con JavaScript")


# -------------------------------------------------
# TABLA #tbl_data
# -------------------------------------------------

def seleccionar_fila_tbl_data(frame, texto):
    print(f"[INFO] Buscando fila en #tbl_data: {texto}")

    esperar_selector(frame, "#tbl_data")

    filas = frame.locator("#tbl_data tr")
    total = filas.count()
    objetivo = normalizar_texto(texto)

    for i in range(total):
        try:
            fila = filas.nth(i)
            contenido = normalizar_texto(fila.inner_text())

            if objetivo in contenido:
                fila.click(force=True)
                print("[OK] Fila seleccionada en #tbl_data")
                return
        except Exception:
            pass

    raise RuntimeError(f"No se encontró: {texto}")


# -------------------------------------------------
# TABLA #ctl00_CPH1_Mt0
# -------------------------------------------------

def seleccionar_99_gobiernos_regionales(frame):
    print("[INFO] Seleccionando 99: GOBIERNOS REGIONALES...")

    td = frame.locator("#ctl00_CPH1_RptData_ctl02_td9")
    td.wait_for(state="attached", timeout=15000)

    fila = td.locator("xpath=ancestor::tr[1]")
    if fila.count() == 0:
        raise RuntimeError("No se encontró la fila padre de 99: GOBIERNOS REGIONALES")

    fila.first.click(force=True)
    print("[OK] Fila 99: GOBIERNOS REGIONALES seleccionada")


def seleccionar_fila_en_tablas_por_texto(frame, texto):
    objetivo = normalizar_texto(texto)
    print(f"[INFO] Buscando fila por texto en tablas: {texto}")

    tablas = frame.locator("table")
    total_tablas = tablas.count()

    for t in range(total_tablas):
        try:
            tabla = tablas.nth(t)
            filas = tabla.locator("tr")
            total_filas = filas.count()

            for i in range(total_filas):
                try:
                    fila = filas.nth(i)
                    contenido = normalizar_texto(fila.inner_text())

                    if objetivo in contenido:
                        fila.click(force=True)
                        print(f"[OK] Fila encontrada en tabla {t}, fila {i}")
                        return
                except Exception:
                    pass
        except Exception:
            pass

    raise RuntimeError(f"No se encontró la fila en ninguna tabla: {texto}")


def seleccionar_fila_por_codigo_en_tablas(frame, codigo):
    print(f"[INFO] Buscando fila por código {codigo} en tablas...")

    tablas = frame.locator("table")
    total_tablas = tablas.count()

    for t in range(total_tablas):
        try:
            tabla = tablas.nth(t)
            fila = tabla.locator(f"tr[onclick*=\"kCod='{codigo}'\"]")

            if fila.count() > 0:
                fila.first.click(force=True)
                print(f"[OK] Fila con código {codigo} encontrada en tabla {t}")
                return
        except Exception:
            pass

    raise RuntimeError(f"No se encontró una fila con código {codigo} en ninguna tabla")


# -------------------------------------------------
# OEI-PEI
# -------------------------------------------------

def click_boton_oei_pei(frame):
    click_boton(frame, "#ctl00_CPH1_BtnObjetivoEstrategico", "OEI-PEI")


def seleccionar_oei_440_por_codigo(frame, codigo="440-OEI.01-11701"):
    print(f"[INFO] Buscando OEI por código: {codigo}")

    esperar_selector(frame, "#tbl_data")

    fila = frame.locator(f"#tbl_data tr[onclick*=\"kCod='{codigo}'\"]")
    if fila.count() > 0:
        fila.first.click(force=True)
        print(f"[OK] OEI seleccionado por código: {codigo}")
        return

    raise RuntimeError(f"No se encontró el OEI por código: {codigo}")


def seleccionar_oei_440_por_texto(frame, texto=OBJETIVO_OEI):
    print(f"[INFO] Buscando OEI por texto: {texto}")
    seleccionar_fila_tbl_data(frame, texto)


# -------------------------------------------------
# AEI-PEI
# -------------------------------------------------

def click_boton_aei_pei(frame):
    """
    En tu DOM aparece como BtnAccionesEstrategicas.
    """
    click_boton(frame, "#ctl00_CPH1_BtnAccionesEstrategicas", "AEI-PEI")


def seleccionar_aei_por_codigo(frame, codigo="440-AEI.01.01-48435"):
    """
    Selecciona el primer AEI usando el kCod visible en el DOM.
    """
    print(f"[INFO] Buscando AEI por código: {codigo}")

    esperar_selector(frame, "#tbl_data")

    fila = frame.locator(f"#tbl_data tr[onclick*=\"kCod='{codigo}'\"]")
    if fila.count() > 0:
        fila.first.click(force=True)
        print(f"[OK] AEI seleccionado por código: {codigo}")
        return

    raise RuntimeError(f"No se encontró el AEI por código: {codigo}")


def seleccionar_aei_por_texto(frame, texto=OBJETIVO_AEI):
    """
    Fallback por texto visible del AEI.
    """
    print(f"[INFO] Buscando AEI por texto: {texto}")
    seleccionar_fila_tbl_data(frame, texto)


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        # 1. Abrir portal
        print("[INFO] Abriendo portal...")
        page.goto(URL, wait_until="load")
        page.wait_for_timeout(8000)

        # 2. Frame principal
        frame = esperar_frame_principal(page)
        print("[OK] Frame inicial listo")

        # 3. Año
        print(f"[INFO] Seleccionando año {ANIO}...")
        seleccionar_dropdown(frame, "#ctl00_CPH1_DrpYear", ANIO)
        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        # 4. Módulo
        print(f"[INFO] Seleccionando módulo {MODULO}...")
        seleccionar_dropdown(frame, "#ctl00_CPH1_DrpActProy", MODULO)
        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        # 5. Nivel de Gobierno
        click_boton(frame, "#ctl00_CPH1_BtnTipoGobierno", "Nivel de Gobierno")
        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        # 6. Seleccionar R
        seleccionar_fila_tbl_data(frame, OBJETIVO_NIVEL)
        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        # 7. Botón Gob.Reg.Mancom. visible
        click_boton(frame, "#ctl00_CPH1_BtnSector", "Gob.Reg.Mancom.")
        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        # 8. Esperar tabla Mt0
        esperar_selector(frame, "#ctl00_CPH1_Mt0")
        page.wait_for_timeout(3000)

        # 9. Seleccionar 99
        seleccionar_99_gobiernos_regionales(frame)
        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        print("[OK] Flujo completado hasta 99: GOBIERNOS REGIONALES")

        # 10. Botón Pliego
        click_boton(frame, "#ctl00_CPH1_BtnPliego", "Pliego")
        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        # 11. Esperar tabla del nivel Pliego
        esperar_selector(frame, "#ctl00_CPH1_Mt0")
        page.wait_for_timeout(3000)

        # 12A. Intento más robusto: por código 440
        try:
            seleccionar_fila_por_codigo_en_tablas(frame, "440")
        except Exception:
            seleccionar_fila_en_tablas_por_texto(frame, OBJETIVO_PLIEGO)

        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        print("[OK] Flujo completado hasta pliego 440")

        # 13. Botón OEI-PEI
        click_boton_oei_pei(frame)
        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        # 14. Esperar tabla de OEI
        esperar_selector(frame, "#tbl_data")
        page.wait_for_timeout(3000)

        # 15A. Intento por código OEI
        try:
            seleccionar_oei_440_por_codigo(frame, "440-OEI.01-11701")
        except Exception:
            seleccionar_oei_440_por_texto(frame, OBJETIVO_OEI)

        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        print("[OK] Flujo completado hasta OEI-PEI / OEI.01-440")

        # 16. Botón AEI-PEI
        click_boton_aei_pei(frame)
        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        # 17. Esperar tabla de AEI
        esperar_selector(frame, "#tbl_data")
        page.wait_for_timeout(3000)

        # 18A. Intento por código AEI
        try:
            seleccionar_aei_por_codigo(frame, "440-AEI.01.01-48435")
        except Exception:
            seleccionar_aei_por_texto(frame, OBJETIVO_AEI)

        page.wait_for_timeout(5000)
        frame = esperar_frame_principal(page)

        print("[OK] Flujo completado hasta AEI-PEI / AEI.01.01-440")

        input("Presiona Enter para cerrar...")
        browser.close()


if __name__ == "__main__":
    main()