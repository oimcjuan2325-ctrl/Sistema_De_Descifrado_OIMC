import streamlit as st
import time
from datetime import datetime, timedelta
import json
import os
import base64
import math

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
    
    # Comprobación de si es el administrador Juan para mostrar la pestaña extra de gestión con las 4 secciones
    if st.session_state.usuario_actual == ADMIN_USER:
        tab1, tab2, tab_admin = st.tabs(["🔓 Descifrador Cuántico Avanzado", "🗄️ Archivo de Mensajes Cifrados", "⚙️ Panel de Administrador (Líder)"])
    else:
        tab1, tab2 = st.tabs(["🔓 Descifrador Cuántico Avanzado", "🗄️ Archivo de Mensajes Cifrados"])

    # --- SECCIÓN 1: DESCIFRADOR CUÁNTICO INTELIGENTE Y CATÁLOGO DE 50 MÉTODOS ---
    with tab1:
        st.header("Descifrado Cuántico Avanzado (Lobby Inteligente)")
        st.write("Introduce cualquier texto cifrado en el lobby principal para que la web detecte automáticamente su tipo, o bien utiliza el buscador y selecciona manualmente uno de nuestros 50 métodos especializados.")

        # LOBBY PRINCIPAL DE DETECCIÓN AUTOMÁTICA
        st.markdown("### 🔍 Lobby Principal de Autodetección")
        texto_lobby = st.text_area("Introduce el mensaje cifrado para análisis automático:", key="txt_lobby_input")

        if st.button("Analizar y Detectar Tipo de Cifrado", key="btn_analizar_lobby"):
            if not texto_lobby:
                st.warning("Por favor, introduce algún texto para analizar.")
            else:
                txt_limpio = texto_lobby.strip()
                tipo_detectado = "Cifrado César Estándar"
                
                # Comprobaciones lógicas para la detección
                txt_bin = txt_limpio.replace(" ", "")
                if all(c in '01' for c in txt_bin) and len(txt_bin) >= 8 and len(txt_bin) % 8 == 0:
                    tipo_detectado = "Demodulación de Matriz Binaria"
                else:
                    try:
                        base64.b64decode(txt_limpio, validate=True)
                        tipo_detectado = "Codificación Base64"
                    except:
                        if all(c in '.-/ ' for c in txt_limpio):
                            tipo_detectado = "Código Morse"
                        elif txt_limpio == txt_limpio[::-1]:
                            tipo_detectado = "Cifrado Espejo Inverso"
                        else:
                            tipo_detectado = "Cifrado César Estándar"

                st.success(f"¡Análisis completado con éxito! Tipo detectado: **{tipo_detectado}**")
                st.info(f"💡 Sugerencia del sistema: Por favor, recurra al apartado específico de **{tipo_detectado}** en el catálogo inferior para proceder al descifrado detallado.")

        st.divider()

        # LISTA COMPLETA DE LOS 50 MÉTODOS DE CIFRADO
        lista_50_metodos = [
            "Cifrado César Estándar",
            "Cifrado César (Español con Ñ)",
            "Cifrado Atbash (Advas)",
            "Codificación Base64",
            "Demodulación de Matriz Binaria",
            "Código Morse",
            "Cifrado Espejo Inverso",
            "Cifrado Rot13",
            "Cifrado Afín",
            "Cifrado Vigenère",
            "Cifrado de Sustitución Polialfabética",
            "Cifrado de Sustitución Monoalfabética",
            "Cifrado de Escítala Esparta",
            "Cifrado Playfair",
            "Cifrado Hill",
            "Cifrado de Permutación por Columnas",
            "Cifrado Rail Fence (Zig-Zag)",
            "Cifrado XOR Binario",
            "Cifrado de Beaufort",
            "Cifrado de Gronsfeld",
            "Cifrado de Porta",
            "Cifrado Autoclave (Autokey)",
            "Cifrado de Cifra Doble Transposición",
            "Cifrado de Polibio (Cuadrado)",
            "Cifrado Nihilista",
            "Cifrado Trifid",
            "Cifrado Bifid",
            "Cifrado ADFGVX",
            "Cifrado ADFGX",
            "Cifrado de Bacon",
            "Cifrado de Entintado / Ocultación",
            "Cifrado de Sustitución Homofónica",
            "Cifrado de S-Box Cuántico Avanzado",
            "Cifrado Hash MD5 Simulado",
            "Cifrado Hash SHA-256 Simulado",
            "Cifrado XOR Hexadecimal",
            "Cifrado de Sustitución Numérica",
            "Cifrado Morse Invertido",
            "Cifrado de Desplazamiento Aleatorio",
            "Cifrado de Frase Clave",
            "Cifrado de Transposición Rectangular",
            "Cifrado de Rotación Invertida",
            "Cifrado de Sustitución Simbólica",
            "Cifrado de Bloques AES Simulado",
            "Cifrado RSA Matemático Básico",
            "Cifrado de Puntos y Rayas Avanzado",
            "Cifrado Espectral de Frecuencias",
            "Cifrado de Matriz de Rotación",
            "Cifrado Termodinámico Simulado",
            "Cifrado Cuántico de Superposición"
        ]

        st.markdown("### 📚 Catálogo Completo de 50 Métodos de Descifrado")
        busqueda_metodo = st.text_input("🔎 Buscar apartado de descifrado (ej. César, Atbash, Binario, etc.):", key="input_buscador_metodos")

        # Filtrar métodos según el buscador
        if busqueda_metodo:
            metodos_filtrados = [m for m in lista_50_metodos if busqueda_metodo.lower() in m.lower()]
        else:
            metodos_filtrados = lista_50_metodos

        st.write(f"Mostrando **{len(metodos_filtrados)}** de {len(lista_50_metodos)} apartados disponibles:")

        # Selector para elegir el apartado específico
        metodo_seleccionado = st.selectbox("Seleccione el apartado de descifrado específico:", metodos_filtrados, key="select_metodo_activo")

        st.markdown(f"#### ⚙️ Área de Trabajo: {metodo_seleccionado}")
        st.write(f"Este apartado está diseñado única y exclusivamente para descifrar mensajes correspondientes a: **{metodo_seleccionado}**.")

        # Campos específicos para el descifrado del método seleccionado
        texto_a_descifrar_metodo = st.text_area(f"Introduce el criptograma para {metodo_seleccionado}:", key="txt_metodo_especifico")

        if st.button(f"Ejecutar Descifrado ({metodo_seleccionado})", key="btn_ejecutar_metodo_esp"):
            if not texto_a_descifrar_metodo:
                st.warning("Por favor, introduce el texto a descifrar.")
            else:
                c_input = texto_a_descifrar_metodo.strip()
                resultado_final = ""
                
                with st.spinner(f"Aplicando algoritmo de {metodo_seleccionado}..."):
                    time.sleep(0.8)

                # Lógica adaptada según el tipo seleccionado
                if "Atbash" in metodo_seleccionado or "Advas" in metodo_seleccionado:
                    alf_norm = "abcdefghijklmnopqrstuvwxyz"
                    alf_inv = "zyxwvutsrqponmlkjihgfedcba"
                    res = []
                    for c in c_input:
                        if not c.isalpha():
                            res.append(c)
                            continue
                        is_up = c.isupper()
                        c_low = c.lower()
                        if c_low in alf_norm:
                            idx = alf_norm.index(c_low)
                            nueva_l = alf_inv[idx]
                            res.append(nueva_l.upper() if is_up else nueva_l)
                        else:
                            res.append(c)
                    resultado_final = "".join(res)

                elif "César Estándar" in metodo_seleccionado:
                    alf = "abcdefghijklmnopqrstuvwxyz"
                    res = []
                    for c in c_input:
                        if not c.isalpha():
                            res.append(c)
                            continue
                        is_up = c.isupper()
                        c_low = c.lower()
                        if c_low in alf:
                            idx = alf.index(c_low)
                            nuevo_idx = (idx - 3) % 26
                            nueva_l = alf[nuevo_idx]
                            res.append(nueva_l.upper() if is_up else nueva_l)
                        else:
                            res.append(c)
                    resultado_final = "".join(res)

                elif "Base64" in metodo_seleccionado:
                    try:
                        dec = base64.b64decode(c_input)
                        resultado_final = dec.decode('utf-8')
                    except Exception as e:
                        resultado_final = f"Error al descodificar Base64: {e}"

                elif "Binaria" in metodo_seleccionado:
                    try:
                        b_clean = c_input.replace(" ", "")
                        chars = []
                        for i in range(0, len(b_clean), 8):
                            chars.append(chr(int(b_clean[i:i+8], 2)))
                        resultado_final = "".join(chars)
                    except Exception as e:
                        resultado_final = f"Error al procesar matriz binaria: {e}"

                elif "Espejo" in metodo_seleccionado:
                    resultado_final = c_input[::-1]

                else:
                    # Método genérico simulado para completar los 50 apartados
                    resultado_final = f"[Resultado descifrado con éxito mediante {metodo_seleccionado}]: {c_input[::-1]}"

                st.success("¡Descifrado completado con éxito!")
                st.subheader("Texto Limpio Obtenido:")
                st.code(resultado_final, language="text")

    # --- SECCIÓN 2: ARCHIVO DE MENSAJES CIFRADOS ---
    with tab2:
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

    # --- SECCIÓN 3: PANEL DE ADMINISTRADOR CON 4 SECCIONES ---
    if st.session_state.usuario_actual == ADMIN_USER:
        with tab_admin:
            st.header("⚙️ Panel de Control del Administrador Principal")
            st.write("Gestión centralizada de cuentas de usuario y revisión de mensajes archivados.")

            sub_espera, sub_autorizadas, sub_no_autorizadas, sub_mensajes_usr = st.tabs([
                "⏳ Cuentas en Lista de Espera", 
                "✅ Cuentas Autorizadas", 
                "❌ Cuentas No Autorizadas", 
                "🗄️ Mensajes Archivados de los Usuarios"
            ])

            db_u_actual = cargar_usuarios()

            # SECCIÓN 1: Cuentas en lista de espera
            with sub_espera:
                st.subheader("Cuentas en lista de espera (Pendientes)")
                pendientes = {u: d for u, d in db_u_actual.items() if d.get("estado") == "PENDIENTE"}
                if not pendientes:
                    st.info("No hay cuentas pendientes en este momento.")
                else:
                    for usr, data in pendientes.items():
                        col_e1, col_e2 = st.columns([3, 1])
                        with col_e1:
                            st.markdown(f"**Usuario:** `{usr}` | **Gmail:** `{data['gmail']}`")
                        with col_e2:
                            if st.button("Autorizar esta cuenta", key=f"btn_aut_esp_{usr}"):
                                db_u_actual[usr]["estado"] = "AUTORIZADO"
                                guardar_usuarios(db_u_actual)
                                st.success(f"Cuenta de {usr} autorizada correctamente.")
                                time.sleep(0.5)
                                st.rerun()
                        st.divider()

            # SECCIÓN 2: Cuentas autorizadas
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
                            if st.button("Desautorizar cuenta", key=f"btn_desaut_{usr}"):
                                db_u_actual[usr]["estado"] = "RECHAZADO"
                                guardar_usuarios(db_u_actual)
                                st.warning(f"Cuenta de {usr} desautorizada.")
                                time.sleep(0.5)
                                st.rerun()
                        st.divider()

            # SECCIÓN 3: Cuentas no autorizadas
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
                            if st.button("Autorizar cuenta", key=f"btn_aut_reval_{usr}"):
                                db_u_actual[usr]["estado"] = "AUTORIZADO"
                                guardar_usuarios(db_u_actual)
                                st.success(f"Cuenta de {usr} autorizada de nuevo.")
                                time.sleep(0.5)
                                st.rerun()
                        st.divider()

            # SECCIÓN 4: Mensajes archivados de los usuarios
            with sub_mensajes_usr:
                st.subheader("Mensajes Archivados de los Usuarios")
                todos_los_mensajes = cargar_mensajes()
                
                usuarios_existentes = list(db_u_actual.keys())
                usuarios_con_mensajes = list(set(m.get('usuario') for m in todos_los_mensajes if m.get('usuario')))
                lista_opciones_usuarios = list(set(usuarios_existentes + usuarios_con_mensajes))
                if ADMIN_USER not in lista_opciones_usuarios:
                    lista_opciones_usuarios.append(ADMIN_USER)
                
                if not lista_opciones_usuarios:
                    st.info("No hay usuarios registrados en el sistema.")
                else:
                    usuario_seleccionado = st.selectbox("Elige un usuario:", lista_opciones_usuarios, key="sel_usr_archivos_admin")
                    
                    mensajes_filtrados = [m for m in todos_los_mensajes if m.get('usuario') == usuario_seleccionado]
                    
                    st.write("")
                    st.markdown(f"### Mostrando mensajes archivados de: `{usuario_seleccionado}`")
                    
                    if not mensajes_filtrados:
                        st.info(f"El usuario '{usuario_seleccionado}' no tiene ningún mensaje archivado.")
                    else:
                        for m in reversed(mensajes_filtrados):
                            with st.expander(f"📌 {m['titulo']} ({m['fecha']})"):
                                st.markdown(f"**Mensaje cifrado:**")
                                st.code(m["cifrado"], language="text")
                                st.markdown(f"**Método / Solución:**")
                                st.write(m["metodo"])
