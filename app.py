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

    # --- SECCIÓN 1: DESCIFRADOR CUÁNTICO ACADÉMICO ---
    with tab1:
        st.header("Descifrado Cuántico Avanzado (Motor Inteligente)")
        st.write("Introduce cualquier texto cifrado (letras, sustituciones, binario o Base64) para traducirlo y obtener el mensaje limpio y legible en español.")

        # Selector de alfabeto real y funcional
        tipo_alfabeto_sel = st.radio(
            "Selecciona el tipo de alfabeto para el cifrado César:",
            ["Estándar (26 letras - Sin Ñ)", "Español Completo (27 letras - Con Ñ)"],
            horizontal=True
        )

        texto_cifrado_input = st.text_area("Introduce el mensaje cifrado (letras o números):", key="txt_cifrar_input_acad")

        if st.button("Ejecutar Descifrado Académico", key="btn_descifrar_acad"):
            if not texto_cifrado_input:
                st.warning("Por favor, introduce algún texto.")
            else:
                input_clean = texto_cifrado_input.strip()
                
                with st.spinner("Procesando superposición de estados y descifrado de caracteres..."):
                    time.sleep(1.0)
                
                texto_descifrado = ""
                metodo_usado = ""
                explicacion_pasos = ""
                
                # 1. Intentar decodificar como Binario
                input_bin_clean = input_clean.replace(" ", "")
                es_binario = all(c in '01' for c in input_bin_clean) and len(input_bin_clean) >= 8 and len(input_bin_clean) % 8 == 0
                
                if es_binario:
                    try:
                        chars = []
                        for i in range(0, len(input_bin_clean), 8):
                            byte_str = input_bin_clean[i:i+8]
                            chars.append(chr(int(byte_str, 2)))
                        texto_descifrado = "".join(chars)
                        metodo_usado = "Demodulación de Matriz Binaria a Texto Plano"
                        explicacion_pasos = f"1. **Conversión de Bits:** Traducción directa de bloques de 8 bits a caracteres ASCII.\n2. **Resultado en español:** `{texto_descifrado}`"
                    except Exception:
                        es_binario = False

                # 2. Intentar Base64 si no es binario
                if not es_binario:
                    es_b64 = False
                    try:
                        dec = base64.b64decode(input_clean, validate=True)
                        texto_descifrado = dec.decode('utf-8')
                        es_b64 = True
                    except Exception:
                        pass

                    if es_b64:
                        metodo_usado = "Decodificación de Bloques Base64"
                        explicacion_pasos = f"1. **Bloques Base64 detectados:** Descodificación completada con éxito.\n2. **Texto en español:** `{texto_descifrado}`"
                    else:
                        # 3. Motor de descifrado alfabético con el alfabeto seleccionado (26 o 27 letras real)
                        desplazamiento = 3
                        
                        alfabeto_26 = "abcdefghijklmnopqrstuvwxyz"
                        alfabeto_27 = "abcdefghijklmnñopqrstuvwxyz"
                        
                        if "26" in tipo_alfabeto_sel:
                            alfabeto_activo = alfabeto_26
                            nombre_alfabeto = "Z_26 (Sin Ñ)"
                        else:
                            alfabeto_activo = alfabeto_27
                            nombre_alfabeto = "Z_27 (Con Ñ)"
                        
                        def descifrar_cesar(texto, alfabeto, desp):
                            resultado = []
                            for c in texto:
                                if not c.isalpha():
                                    resultado.append(c)
                                    continue
                            
                                es_mayus = c.isupper()
                                c_min = c.lower()
                                
                                if c_min in alfabeto:
                                    idx = alfabeto.index(c_min)
                                    nuevo_idx = (idx - desp) % len(alfabeto)
                                    letra_res = alfabeto[nuevo_idx]
                                    resultado.append(letra_res.upper() if es_mayus else letra_res)
                                else:
                                    resultado.append(c)
                            return "".join(resultado)

                        texto_descifrado = descifrar_cesar(input_clean, alfabeto_activo, desplazamiento)

                        metodo_usado = f"Cifrado César Inverso con Alfabeto {nombre_alfabeto}"
                        explicacion_pasos = (
                            f"1. **Análisis de caracteres alfabéticos:** Procesamiento del criptograma basado en letras ('{input_clean}').\n"
                            f"2. **Alineación de frecuencias:** Aplicación de desplazamiento inverso en base al abecedario estricto de {len(alfabeto_activo)} caracteres.\n"
                            f"3. **Texto limpio obtenido:** `{texto_descifrado}`"
                        )
                
                st.success("¡Operación completada con éxito!")
                st.subheader("Texto Legible en Español:")
                st.code(texto_descifrado, language="text")

                st.markdown("### 🎓 Solución y Demostración Académica:")
                st.info(
                    f"**Método Teórico Aplicado:** {metodo_usado}\n\n"
                    f"{explicacion_pasos}"
                )

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

            # SECCIÓN 1: Cuentas en lista de espera para autorizarse
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

            # SECCIÓN 4: Mensajes archivados de los usuarios (con selector de usuario)
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
