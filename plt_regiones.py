# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 19:12:53 2026

@author: Enzo
"""

from playwright.sync_api import sync_playwright

URL = "https://app.ceplan.gob.pe/ConsultaCEPLAN/consulta/Default.aspx"
ANIO = "2025"
MODULO = "Actividades/Proyectos"
OBJETIVO_NIVEL = "R: GOBIERNOS REGIONALES"


def obtener_frame_operativo(page):
    for frame in page.frames:
        try:
            if frame.locator("#ctl00_CPH1_DrpYear").count() > 0:
                return frame
        except Exception:
            pass
    return None


def esperar_frame_operativo(page, timeout_ms=20000):
    transcurrido = 0
    paso = 500

    while transcurrido < timeout_ms:
        frame = obtener_frame_operativo(page)
        if frame is not None:
            try:
                if frame.locator("#ctl00_CPH1_DrpYear").count() > 0:
                    return frame
            except Exception:
                pass

        page.wait_for_timeout(paso)
        transcurrido += paso

    raise RuntimeError("No se encontró el frame operativo dentro del tiempo esperado")


def elegir_fila_tabla(frame, patron_texto):
    print(f"[INFO] Buscando fila: {patron_texto}")

    tabla = frame.locator("table#tbl_data")
    if tabla.count() == 0:
        raise RuntimeError("No se encontró la tabla #tbl_data")

    filas = tabla.locator("tr")
    total = filas.count()

    if total == 0:
        raise RuntimeError("No se encontraron filas en la tabla #tbl_data")

    patron = patron_texto.upper()

    for i in range(total):
        try:
            fila = filas.nth(i)
            contenido = fila.inner_text().upper()

            if patron in contenido:
                print(f"[OK] Fila encontrada en índice {i}")
                fila.click()
                return
        except Exception:
            pass

    raise RuntimeError(f"No se encontró la fila: {patron_texto}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        print("[INFO] Abriendo portal...")
        page.goto(URL, wait_until="load", timeout=60000)
        page.wait_for_timeout(8000)

        print("[INFO] URL actual:", page.url)
        print("[INFO] Título:", page.title())

        # 1. Encontrar frame inicial
        frame = esperar_frame_operativo(page)
        print("[OK] Frame operativo inicial:", frame.url)

        # 2. Seleccionar año
        print(f"[INFO] Seleccionando año {ANIO}...")
        frame.locator("#ctl00_CPH1_DrpYear").select_option(label=ANIO)
        page.wait_for_timeout(5000)
        print("[OK] Año seleccionado")

        # 3. Volver a encontrar el frame, porque cambió
        frame = esperar_frame_operativo(page)
        print("[OK] Frame operativo después del año:", frame.url)

        # 4. Seleccionar módulo
        print(f"[INFO] Seleccionando módulo {MODULO}...")
        frame.locator("#ctl00_CPH1_DrpActProy").select_option(label=MODULO)
        page.wait_for_timeout(5000)
        print("[OK] Módulo seleccionado")

        # 5. Volver a encontrar el frame otra vez
        frame = esperar_frame_operativo(page)
        print("[OK] Frame operativo después del módulo:", frame.url)

        # 6. Seleccionar nivel de gobierno
        print("[INFO] Activando botón Nivel de Gobierno...")
        frame.locator("#ctl00_CPH1_BtnTipoGobierno").click()
        page.wait_for_timeout(5000)
        print("[OK] Botón Nivel de Gobierno activado")

        # 7. Reubicar frame después del click
        frame = esperar_frame_operativo(page)
        print("[OK] Frame operativo después de Nivel de Gobierno:", frame.url)

        # 8. Seleccionar la fila R: GOBIERNOS REGIONALES
        elegir_fila_tabla(frame, OBJETIVO_NIVEL)
        page.wait_for_timeout(5000)
        print(f"[OK] Fila seleccionada: {OBJETIVO_NIVEL}")

        # 9. Reubicar frame después de seleccionar la fila
        frame = esperar_frame_operativo(page)
        print("[OK] Frame operativo después de seleccionar R:", frame.url)
        
        
        input("Presiona Enter para cerrar...")
        browser.close()
        
    
if __name__ == "__main__":
    main()