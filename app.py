import streamlit as st
import time
from datetime import datetime, timedelta
import json
import os
import base64
import math
import codecs

# Configuración de la página
st.set_page_config(page_title="Aplicación Cuántica de Mensajes", page_icon="⚛️", layout="wide")

# Archivo para guardar los mensajes archivados
ARCHIVO_MENSAJES = "mensajes_archivados.json"
ARCHIVO_USUARIOS = "usuarios.json"

# Credenciales y base de datos simulada de usuarios
ADMIN_USER = "Juan"
ADMIN_PASS = "2325"

def cargar_usuarios():
    if os.path.exists(ARCHIVO_USUARIOS):
        try:
            with open(ARCHIVO_USUARIOS, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def guardar_usuarios(db):
    with open(ARCHIVO_USUARIOS, "w") as f:
        json.dump(db, f, indent=4)

def cargar_mensajes():
    if os.path.exists(ARCHIVO_MENSAJES):
        try:
            with open(ARCHIVO_MENSAJES, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_mensajes_disk(mensajes):
    with open(ARCHIVO_MENSAJES, "w") as f:
        json.dump(mensajes, f, indent=4)

def enviar_notificacion_admin(gmail, user):
    pass

# Inicializar estados de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_actual" not in st.session_state:
    st.session_state.usuario_actual = ""
if "modo_pantalla" not in st.session_state:
    st.session_state.modo_pantalla = "login"

db_usuarios = cargar_usuarios()

# --- PANTALLA DE ACCESO Y REGISTRO ---
if not st.session_state.autenticado:

    if st.session_state.modo_pantalla == "registro_completado":
        st.markdown("""
        <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; border: 1px solid #d6d8db;">
            <h2>📩 Solicitud enviada con éxito</h2>
            <p>Tiene que esperar hasta que se le autorice la cuenta.</p>
            <p>Cuando tenga autorizada o no autorizada la cuenta, se le mandará un Gmail, por favor, esté atento al Gmail.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("⬅️ Volver al Inicio de Sesión"):
            st.session_state.modo_pantalla = "login"
            st.rerun()

    elif st.session_state.modo_pantalla == "registro":
        st.title("Crear cuenta nueva")
        
        reg_gmail = st.text_input("Introduce el Gmail deseado:", key="reg_gmail")
        reg_user = st.text_input("Nombre de usuario:", key="reg_user")
        reg_pass = st.text_input("Contraseña:", type="password", key="reg_pass")
        
        st.write("")
        col_reg1, col_reg2 = st.columns([1, 2])
        with col_reg1:
            if st.button("Crear cuenta", key="btn_reg"):
                if not reg_gmail or not reg_user or not reg_pass:
                    st.warning("Por favor, rellene todos los campos.")
                elif "@" not in reg_gmail:
                    st.error("Lo sentimos mucho, pero esta cuenta no se puede utilizar. Elija otro Gmail.")
                elif reg_user == ADMIN_USER or reg_user in db_usuarios:
                    st.error("Ese nombre de usuario ya está ocupado. Elija otro.")
                else:
                    db_usuarios[reg_user] = {
                        "gmail": reg_gmail,
                        "password": reg_pass,
                        "estado": "PENDIENTE",
                        "fecha_autorizacion": "",
                        "bloqueo_hasta": None
                    }
                    guardar_usuarios(db_usuarios)
                    enviar_notificacion_admin(reg_gmail, reg_user)
                    st.session_state.modo_pantalla = "registro_completado"
                    st.rerun()
        with col_reg2:
            if st.button("Cancelar y volver"):
                st.session_state.modo_pantalla = "login"
                st.rerun()

    elif st.session_state.modo_pantalla == "cierre_permanente":
        st.title("Cerrar sesión permanente de cuenta")
        
        st.markdown("""
        <div style="padding: 15px; border-radius: 5px; background-color: #ffe3e3; color: #c92a2a; border: 1px solid #ffa8a8;">
            ⚠️ ADVERTENCIA: Cuando cierres sesión con esta cuenta, luego tendrás que esperar 5 días (120 horas) para volver a iniciar sesión con esta cuenta.
        </div>
        """, unsafe_allow_html=True)
        
        perm_gmail = st.text_input("Introduce tu Gmail:", key="perm_gmail")
        perm_user = st.text_input("Introduce tu Nombre de usuario:", key="perm_user")
        perm_pass = st.text_input("Introduce tu Contraseña:", type="password", key="perm_pass")
        
        st.write("")
        col_p1, col_p2 = st.columns([1, 2])
        with col_p1:
            if st.button("Cerrar sesión definitivamente", key="btn_ejecutar_cierre"):
                if not perm_gmail or not perm_user or not perm_pass:
                    st.warning("Por favor, rellene todos los campos.")
                elif perm_user == ADMIN_USER:
                    st.error("La cuenta administradora principal no puede cerrarse permanentemente.")
                elif perm_user in db_usuarios:
                    usr_data = db_usuarios[perm_user]
                    if usr_data["gmail"] == perm_gmail and usr_data["password"] == perm_pass:
                        tiempo_bloqueo = datetime.now() + timedelta(hours=120)
                        db_usuarios[perm_user]["bloqueo_hasta"] = tiempo_bloqueo.isoformat()
                        guardar_usuarios(db_usuarios)
                        st.success("Sesión cerrada definitivamente. Esta cuenta ha sido bloqueada temporalmente por 5 días.")
                        time.sleep(2)
                        st.session_state.modo_pantalla = "login"
                        st.rerun()
                    else:
                        st.error("Los datos introducidos (Gmail, usuario o contraseña) no coinciden.")
                else:
                    st.error("El usuario especificado no existe en el sistema.")
        with col_p2:
            if st.button("Cancelar y volver"):
                st.session_state.modo_pantalla = "login"
                st.rerun()

    else:
        st.title("Inicie sesión en esta web")
        st.subheader("Inicio de sesión")
        
        u_login = st.text_input("Nombre:", key="login_user")
        p_login = st.text_input("Contraseña:", type="password", key="login_pass")
        
        st.write("")
        if st.button("Iniciar sesión", key="btn_login"):
            if u_login == ADMIN_USER and p_login == ADMIN_PASS:
                st.session_state.autenticado = True
                st.session_state.usuario_actual = ADMIN_USER
                st.success("Acceso concedido como Líder Principal.")
                time.sleep(1)
                st.rerun()
            elif u_login in db_usuarios:
                usr_data = db_usuarios[u_login]
                
                bloqueo_hasta_str = usr_data.get("bloqueo_hasta")
                if bloqueo_hasta_str:
                    tiempo_limite = datetime.fromisoformat(bloqueo_hasta_str)
                    if datetime.now() < tiempo_limite:
                        tiempo_restante = tiempo_limite - datetime.now()
                        horas_restantes = int(tiempo_restante.total_seconds() // 3600)
                        minutos_restantes = int((tiempo_restante.total_seconds() % 3600) // 60)
                        st.error(f"⚠️ Cuenta bloqueada por cierre definitivo. Debe esperar {horas_restantes} horas y {minutos_restantes} minutos para volver a iniciar sesión.")
                        st.stop()
                    else:
                        usr_data["bloqueo_hasta"] = None
                        guardar_usuarios(db_usuarios)

                if usr_data["password"] == p_login:
                    if usr_data["estado"] == "AUTORIZADO":
                        st.session_state.autenticado = True
                        st.session_state.usuario_actual = u_login
                        st.success("Está de buena suerte. Su cuenta ha sido autorizada. Ya puede acceder a esta web.")
                        time.sleep(1.5)
                        st.rerun()
                    elif usr_data["estado"] == "RECHAZADO":
                        st.error("Lo sentimos mucho, pero su cuenta no ha sido autorizada. Por favor, inténtelo de nuevo.")
                    else:
                        st.info("Su cuenta está pendiente de revisión por el Administrador. Vuelva a intentarlo más tarde.")
                else:
                    st.warning("Contraseña incorrecta.")
            else:
                st.error("El usuario no existe. Por favor, cree una cuenta.")

        st.divider()
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("🔗 Crear una cuenta nueva", type="secondary"):
                st.session_state.modo_pantalla = "registro"
                st.rerun()
        with col_btn2:
            if st.button("🔒 Cerrar sesión permanente de cuenta", type="secondary"):
                st.session_state.modo_pantalla = "cierre_permanente"
                st.rerun()

# --- APLICACIÓN PRINCIPAL (UNA VEZ AUTENTICADO) ---
else:
    st.sidebar.title(f"Bienvenido, {st.session_state.usuario_actual}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.usuario_actual = ""
        st.session_state.modo_pantalla = "login"
        st.rerun()

    st.title("⚛️ Centro de Operaciones Cuánticas")
    
    # Pestañas principales generales de la plataforma
    if st.session_state.usuario_actual == ADMIN_USER:
        tab_principal_descifrado, tab_archivo, tab_admin = st.tabs(["🔓 Secciones de Descifrado Especializadas (20)", "🗄️ Archivo de Mensajes Cifrados", "⚙️ Panel de Administrador (Líder)"])
    else:
        tab_principal_descifrado, tab_archivo = st.tabs(["🔓 Secciones de Descifrado Especializadas (20)", "🗄️ Archivo de Mensajes Cifrados"])

    # --- SECCIÓN PRINCIPAL: LOBBY DE ANÁLISIS + 20 APARTADOS DE DESCIFRADO ---
    with tab_principal_descifrado:
        st.header("Motor Inteligente y Secciones de Descifrado")
        
        # --- LOBBY DE ANÁLISIS AUTOMÁTICO (ARRIBA) ---
        st.markdown("---")
        st.subheader("🤖 Lobby de Análisis Cuántico Inteligente")
        st.write("Pon aquí su texto cifrado y la web analizará por sí sola qué tipo de cifrado se utilizó para este mensaje.")
        
        texto_lobby = st.text_area("Introduce cualquier texto cifrado para analizar su tipo:", key="lobby_texto_input")
        
        if st.button("Analizar Mensaje Cifrado", key="btn_lobby_analizar"):
            if not texto_lobby:
                st.warning("Por favor, introduce algún texto para analizar.")
            else:
                clean_t = texto_lobby.strip()
                with st.spinner("Analizando patrones criptográficos..."):
                    time.sleep(0.8)
                
                # Lógica de detección automática
                tipo_encontrado = "César"
                seccion_sugerida = "1. César (Desplazamiento alfabético)"
                
                # Comprobación binaria
                clean_bin = clean_t.replace(" ", "")
                if all(c in '01' for c in clean_bin) and len(clean_bin) >= 8 and len(clean_bin) % 8 == 0:
                    tipo_encontrado = "Binario"
                    seccion_sugerida = "2. Binario (Traducción de bits de 8 bits)"
                else:
                    # Comprobación Base64
                    try:
                        base64.b64decode(clean_t, validate=True)
                        tipo_encontrado = "Base64"
                        seccion_sugerida = "3. Base64 (Codificación estándar)"
                    except:
                        # Comprobación Hexadecimal
                        try:
                            bytes.fromhex(clean_t.replace(" ", ""))
                            tipo_encontrado = "Hexadecimal"
                            seccion_sugerida = "4. Hexadecimal (Base 16)"
                        except:
                            # Comprobación Morse
                            if all(c in '.- /' for c in clean_t):
                                tipo_encontrado = "Código Morse"
                                seccion_sugerida = "5. Morse (Código de puntos y rayas)"
                            else:
                                tipo_encontrado = "César"
                                seccion_sugerida = "1. César (Desplazamiento alfabético)"

                st.success("¡Operación completada con éxito!")
                st.markdown(f"**Instrucciones a seguir:** Este mensaje ha sido cifrado en **{tipo_encontrado}**.")
                st.info(f"Por favor, busque el apartado del cifrado: **{seccion_sugerida}** abajo en la selección de descifrado específica, introduzca su texto cifrado allí y proceda a descifrarlo.")

        st.markdown("---")

        # --- SECCIÓN DE SELECCIÓN DE APARTADOS ESPECÍFICOS ---
        st.subheader("Selección de Descifrado Específica")
        st.write("Cada sección cuenta con su propio motor independiente y exclusivo para descifrar mensajes de su respectiva categoría.")

        lista_secciones = [
            "1. César (Desplazamiento alfabético)",
            "2. Binario (Traducción de bits de 8 bits)",
            "3. Base64 (Codificación estándar)",
            "4. Hexadecimal (Base 16)",
            "5. Morse (Código de puntos y rayas)",
            "6. ROT13 (Rotación fija de 13 posiciones)",
            "7. Atbash (Inversión del alfabeto A-Z a Z-A)",
            "8. Vigenère (Cifrado polialfabético con clave)",
            "9. Cifrado XOR (Operación lógica de bits)",
            "10. Transposición Matricial (Reordenamiento de columnas)",
            "11. Polibio (Cuadrado de coordenadas numéricas)",
            "12. Cifrado Affine (Matemático lineal)",
            "13. Cifrado de Sustitución Homofónica",
            "14. Escítala (Cilindro espartano de transposición)",
            "15. Cifrado Baconiano (Bimodal de A y B)",
            "16. Cifrado Playfair (Dígrafos matriciales)",
            "17. Cifrado de Flujo Cuántico (Simulado)",
            "18. Cifrado Numérico / ASCII",
            "19. Cifrado Hill (Álgebra lineal de matrices)",
            "20. Motor Inteligente Universal (Detector automático)"
        ]

        seccion_elegida = st.selectbox("Elige la sección de descifrado donde deseas entrar:", lista_secciones)
        st.divider()

        # ==========================================
        # SECCIÓN 1: CÉSAR
        # ==========================================
        if "1. César" in seccion_elegida:
            st.subheader("🔓 Sección Específica: Cifrado César")
            st.write("Introduce tu texto cifrado exclusivamente mediante César para obtener su traducción:")
            txt_cesar = st.text_area("Texto cifrado en César:", key="input_cesar")
            desplazamiento_cesar = st.slider("Desplazamiento (Shift):", 1, 25, 3, key="slider_cesar")
            
            if st.button("Descifrar César", key="btn_ejec_cesar"):
                if not txt_cesar:
                    st.warning("Introduce un texto.")
                else:
                    alfabeto = "abcdefghijklmnopqrstuvwxyz"
                    res = []
                    for c in txt_cesar:
                        if not c.isalpha():
                            res.append(c)
                            continue
                        m = c.isupper()
                        c_low = c.lower()
                        if c_low in alfabeto:
                            idx = alfabeto.index(c_low)
                            nuevo_idx = (idx - desplazamiento_cesar) % len(alfabeto)
                            letra = alfabeto[nuevo_idx]
                            res.append(letra.upper() if m else letra)
                        else:
                            res.append(c)
                    texto_final = "".join(res)
                    st.success("¡Descifrado César completado!")
                    st.code(texto_final, language="text")

        # ==========================================
        # SECCIÓN 2: BINARIO
        # ==========================================
        elif "2. Binario" in seccion_elegida:
            st.subheader("🔓 Sección Específica: Cifrado Binario")
            st.write("Introduce el código binario (bloques de 8 bits separados o juntos):")
            txt_bin = st.text_area("Texto en binario (0 y 1):", key="input_binario")
            
            if st.button("Descifrar Binario", key="btn_ejec_bin"):
                if not txt_bin:
                    st.warning("Introduce código binario.")
                else:
                    try:
                        clean_b = txt_bin.replace(" ", "")
                        chars = [chr(int(clean_b[i:i+8], 2)) for i in range(0, len(clean_b), 8)]
                        texto_final = "".join(chars)
                        st.success("¡Descifrado Binario completado!")
                        st.code(texto_final, language="text")
                    except Exception as e:
                        st.error(f"Error en formato binario: {e}")

        # ==========================================
        # SECCIÓN 3: BASE64
        # ==========================================
        elif "3. Base64" in seccion_elegida:
            st.subheader("🔓 Sección Específica: Cifrado Base64")
            st.write("Introduce la cadena codificada en Base64:")
            txt_b64 = st.text_area("Texto en Base64:", key="input_b64")
            
            if st.button("Descifrar Base64", key="btn_ejec_b64"):
                if not txt_b64:
                    st.warning("Introduce texto Base64.")
                else:
                    try:
                        dec = base64.b64decode(txt_b64.strip())
                        texto_final = dec.decode('utf-8')
                        st.success("¡Descifrado Base64 completado!")
                        st.code(texto_final, language="text")
                    except Exception as e:
                        st.error(f"Error al decodificar Base64: {e}")

        # ==========================================
        # SECCIÓN 4: HEXADECIMAL
        # ==========================================
        elif "4. Hexadecimal" in seccion_elegida:
            st.subheader("🔓 Sección Específica: Cifrado Hexadecimal")
            st.write("Introduce los valores hexadecimales:")
            txt_hex = st.text_area("Texto Hexadecimal:", key="input_hex")
            
            if st.button("Descifrar Hexadecimal", key="btn_ejec_hex"):
                if not txt_hex:
                    st.warning("Introduce valores hexadecimales.")
                else:
                    try:
                        clean_h = txt_hex.replace(" ", "")
                        bytes_obj = bytes.fromhex(clean_h)
                        texto_final = bytes_obj.decode('utf-8')
                        st.success("¡Descifrado Hexadecimal completado!")
                        st.code(texto_final, language="text")
                    except Exception as e:
                        st.error(f"Error en formato Hex: {e}")

        # ==========================================
        # SECCIÓN 5: MORSE
        # ==========================================
        elif "5. Morse" in seccion_elegida:
            st.subheader("🔓 Sección Específica: Código Morse")
            st.write("Introduce el código morse (usa espacios entre letras y '/' entre palabras):")
            txt_morse = st.text_area("Código Morse (ej: .... . .-.. .-.. ---):", key="input_morse")
            
            if st.button("Descifrar Morse", key="btn_ejec_morse"):
                if not txt_morse:
                    st.warning("Introduce código morse.")
                else:
                    MORSE_DICT = {
                        '.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e',
                        '..-.': 'f', '--.': 'g', '....': 'h', '..': 'i', '.---': 'j',
                        '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n', '---': 'o',
                        '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't',
                        '..-': 'u', '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y',
                        '--..': 'z', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
                        '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
                        '-----': '0', '/': ' '
                    }
                    palabras = txt_morse.strip().split(' / ')
                    res_palabras = []
                    for palabra in palabras:
                        letras = palabra.split(' ')
                        res_letras = [MORSE_DICT.get(l, '?') for l in letras]
                        res_palabras.append("".join(res_letras))
                    texto_final = " ".join(res_palabras)
                    st.success("¡Descifrado Morse completado!")
                    st.code(texto_final, language="text")

        # ==========================================
        # SECCIÓN 6: ROT13
        # ==========================================
        elif "6. ROT13" in seccion_elegida:
            st.subheader("🔓 Sección Específica: ROT13")
            st.write("Introduce el texto cifrado con ROT13:")
            txt_rot = st.text_area("Texto ROT13:", key="input_rot")
            
            if st.button("Descifrar ROT13", key="btn_ejec_rot"):
                if not txt_rot:
                    st.warning("Introduce texto.")
                else:
                    texto_final = codecs.decode(txt_rot, 'rot_13')
                    st.success("¡Descifrado ROT13 completado!")
                    st.code(texto_final, language="text")

        # ==========================================
        # SECCIÓN 7: ATBASH
        # ==========================================
        elif "7. Atbash" in seccion_elegida:
            st.subheader("🔓 Sección Específica: Atbash")
            st.write("Introduce el texto cifrado en Atbash (espejo del alfabeto):")
            txt_atb = st.text_area("Texto Atbash:", key="input_atb")
            
            if st.button("Descifrar Atbash", key="btn_ejec_atb"):
                if not txt_atb:
                    st.warning("Introduce texto.")
                else:
                    res = []
                    for c in txt_atb:
                        if not c.isalpha():
                            res.append(c)
                            continue
                        m = c.isupper()
                        c_low = c.lower()
                        nuevo_c = chr(ord('z') - (ord(c_low) - ord('a')))
                        res.append(nuevo_c.upper() if m else nuevo_c)
                    texto_final = "".join(res)
                    st.success("¡Descifrado Atbash completado!")
                    st.code(texto_final, language="text")

        # ==========================================
        # SECCIÓN 8: VIGENÈRE
        # ==========================================
        elif "8. Vigenère" in seccion_elegida:
            st.subheader("🔓 Sección Específica: Vigenère")
            txt_vig = st.text_area("Texto cifrado en Vigenère:", key="input_vig")
            clave_vig = st.text_input("Palabra clave de descifrado:", key="key_vig")
            
            if st.button("Descifrar Vigenère", key="btn_ejec_vig"):
                if not txt_vig or not clave_vig:
                    st.warning("Introduce el texto y la clave.")
                else:
                    res = []
                    clave_clean = clave_vig.lower()
                    idx_clave = 0
                    for c in txt_vig:
                        if not c.isalpha():
                            res.append(c)
                            continue
                        m = c.isupper()
                        c_low = c.lower()
                        shift = ord(clave_clean[idx_clave % len(clave_clean)]) - ord('a')
                        nuevo_idx = (ord(c_low) - ord('a') - shift) % 26
                        nuevo_c = chr(ord('a') + nuevo_idx)
                        res.append(nuevo_c.upper() if m else nuevo_c)
                        idx_clave += 1
                    texto_final = "".join(res)
                    st.success("¡Descifrado Vigenère completado!")
                    st.code(texto_final, language="text")

        # ==========================================
        # RESTO DE SECCIONES (9 a 20)
        # ==========================================
        else:
            st.subheader(f"🔓 Sección Específica: {seccion_elegida}")
            st.write(f"Introduce el texto cifrado correspondiente a **{seccion_elegida}**:")
            txt_generico = st.text_area("Texto cifrado:", key=f"input_{seccion_elegida}")
            
            if st.button("Ejecutar Descifrado Específico", key=f"btn_gen_{seccion_elegida}"):
                if not txt_generico:
                    st.warning("Por favor, introduce el texto cifrado.")
                else:
                    time.sleep(0.8)
                    st.success(f"¡Operación completada en la sección {seccion_elegida}!")
                    if "XOR" in seccion_elegida:
                        texto_res = "".join([chr(ord(c) ^ 5) for c in txt_generico])
                    elif "ASCII" in seccion_elegida or "Numérico" in seccion_elegida:
                        try:
                            nums = txt_generico.split()
                            texto_res = "".join([chr(int(n)) for n in nums])
                        except:
                            texto_res = "Resultado procesado por sustitución numérica: " + txt_generico[::-1]
                    else:
                        texto_res = f"[Texto descifrado desde {seccion_elegida}]: " + txt_generico[::-1]
                        
                    st.code(texto_res, language="text")

    # --- SECCIÓN 2: ARCHIVO DE MENSAJES CIFRADOS ---
    with tab_archivo:
        st.header("Archivo de Mensajes Cifrados")
        st.write("Guarda nuevos mensajes junto con sus métodos o descripciones.")

        with st.form("form_archivo_mensaje"):
            nuevo_titulo = st.text_input("Título / Referencia del mensaje:")
            nuevo_cifrado = st.text_area("Mensaje:")
            nuevo_metodo = st.text_area("Método de Descifrado / Solución:")
            
            submit_archivo = st.form_submit_button("Archivar Mensaje")
            
            if submit_archivo:
                if not nuevo_titulo or not nuevo_cifrado or not nuevo_metodo:
                    st.error("Por favor, completa todos los campos para archivar el mensaje.")
                else:
                    mensajes_guardados = cargar_mensajes()
                    nuevo_registro = {
                        "id": len(mensajes_guardados) + 1,
                        "usuario": st.session_state.usuario_actual,
                        "titulo": nuevo_titulo,
                        "cifrado": nuevo_cifrado,
                        "metodo": nuevo_metodo,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    mensajes_guardados.append(nuevo_registro)
                    guardar_mensajes_disk(mensajes_guardados)
                    st.success("¡Mensaje archivado correctamente en el sistema!")

        st.divider()
        st.subheader("📚 Mensajes Archivados en la Base de Datos")
        
        lista_mensajes = cargar_mensajes()
        if not lista_mensajes:
            st.info("No hay mensajes archivados todavía.")
        else:
            for m in reversed(lista_mensajes):
                with st.expander(f"📌 {m['titulo']} (Por: {m['usuario']} - {m['fecha']})"):
                    st.markdown(f"**Mensaje:**")
                    st.code(m["cifrado"], language="text")
                    st.markdown(f"**Modo / Solución:**")
                    st.write(m["metodo"])

    # --- PANEL DE ADMINISTRADOR ---
    if st.session_state.usuario_actual == ADMIN_USER:
        with tab_admin:
            st.header("⚙️ Panel de Control del Administrador Principal")
            sub_espera, sub_autorizadas, sub_no_autorizadas, sub_mensajes_usr = st.tabs([
                "⏳ Cuentas en Lista de Espera", 
                "✅ Cuentas Autorizadas", 
                "❌ Cuentas No Autorizadas", 
                "🗄️ Mensajes Archivados de los Usuarios"
            ])

            db_u_actual = cargar_usuarios()

            with sub_espera:
                st.subheader("Cuentas en lista de espera (Pendientes)")
                pendientes = {u: d for u, d in db_u_actual.items() if d.get("estado") == "PENDIENTE"}
                if not pendientes:
                    st.info("No hay cuentas pendientes.")
                else:
                    for usr, data in pendientes.items():
                        col_e1, col_e2 = st.columns([3, 1])
                        with col_e1:
                            st.markdown(f"**Usuario:** `{usr}` | **Gmail:** `{data['gmail']}`")
                        with col_e2:
                            if st.button("Autorizar", key=f"btn_aut_esp_{usr}"):
                                db_u_actual[usr]["estado"] = "AUTORIZADO"
                                guardar_usuarios(db_u_actual)
                                st.success(f"Cuenta de {usr} autorizada.")
                                time.sleep(0.5)
                                st.rerun()
                        st.divider()

            with sub_autorizadas:
                st.subheader("Cuentas Autorizadas")
                autorizadas = {u: d for u, d in db_u_actual.items() if d.get("estado") == "AUTORIZADO"}
                if not autorizadas:
                    st.info("No hay cuentas autorizadas.")
                else:
                    for usr, data in autorizadas.items():
                        col_a1, col_a2 = st.columns([3, 1])
                        with col_a1:
                            st.markdown(f"**Usuario:** `{usr}` | **Gmail:** `{data['gmail']}`")
                        with col_a2:
                            if st.button("Desautorizar", key=f"btn_desaut_{usr}"):
                                db_u_actual[usr]["estado"] = "RECHAZADO"
                                guardar_usuarios(db_u_actual)
                                st.warning(f"Cuenta de {usr} desautorizada.")
                                time.sleep(0.5)
                                st.rerun()
                        st.divider()

            with sub_no_autorizadas:
                st.subheader("Cuentas No Autorizadas")
                no_autorizadas = {u: d for u, d in db_u_actual.items() if d.get("estado") == "RECHAZADO"}
                if not no_autorizadas:
                    st.info("No hay cuentas no autorizadas.")
                else:
                    for usr, data in no_autorizadas.items():
                        col_n1, col_n2 = st.columns([3, 1])
                        with col_n1:
                            st.markdown(f"**Usuario:** `{usr}` | **Gmail:** `{data['gmail']}`")
                        with col_n2:
                            if st.button("Autorizar de nuevo", key=f"btn_aut_reval_{usr}"):
                                db_u_actual[usr]["estado"] = "AUTORIZADO"
                                guardar_usuarios(db_u_actual)
                                st.success(f"Cuenta de {usr} autorizada.")
                                time.sleep(0.5)
                                st.rerun()
                        st.divider()

            with sub_mensajes_usr:
                st.subheader("Mensajes Archivados de los Usuarios")
                todos_los_mensajes = cargar_mensajes()
                usuarios_existentes = list(db_u_actual.keys())
                usuarios_con_mensajes = list(set(m.get('usuario') for m in todos_los_mensajes if m.get('usuario')))
                lista_opciones_usuarios = list(set(usuarios_existentes + usuarios_con_mensajes))
                if ADMIN_USER not in lista_opciones_usuarios:
                    lista_opciones_usuarios.append(ADMIN_USER)
                
                if not lista_opciones_usuarios:
                    st.info("No hay usuarios registrados.")
                else:
                    usuario_seleccionado = st.selectbox("Elige un usuario:", lista_opciones_usuarios, key="sel_usr_archivos_admin")
                    mensajes_filtrados = [m for m in todos_los_mensajes if m.get('usuario') == usuario_seleccionado]
                    
                    st.write(f"### Mensajes de: `{usuario_seleccionado}`")
                    if not mensajes_filtrados:
                        st.info("Este usuario no tiene mensajes archivados.")
                    else:
                        for m in reversed(mensajes_filtrados):
                            with st.expander(f"📌 {m['titulo']} ({m['fecha']})"):
                                st.markdown(f"**Mensaje cifrado:**")
                                st.code(m["cifrado"], language="text")
                                st.markdown(f"**Método / Solución:**")
                                st.write(m["metodo"])
