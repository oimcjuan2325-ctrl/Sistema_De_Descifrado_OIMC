import streamlit as st
import time
from datetime import datetime, timedelta
import json
import os

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
    # Función simulada de notificación
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

    # 1. MODO: MENSAJE DE ESPERA POST-REGISTRO
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

    # 2. MODO: CREAR CUENTA NUEVA
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

    # 3. MODO: CERRAR SESIÓN PERMANENTE
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

    # 4. MODO: INICIO DE SESIÓN (POR DEFECTO)
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
    
    # PESTAÑAS DE LA APLICACIÓN
    tab1, tab2 = st.tabs(["🔓 Descifrador Cuántico de Mensajes", "🗄️ Archivo de Mensajes Cifrados"])

    # --- SECCIÓN 1: DESCIFRADOR CUÁNTICO ---
    with tab1:
        st.header("Descifrado basado en Comportamiento de Qubits")
        st.write("Introduce tu texto cifrado para simular la superposición y colapso de qubits que permita revelar el mensaje original.")

        texto_cifrado_input = st.text_area("Introduce el mensaje cifrado:", key="txt_cifrar_input")

        if st.button("Ejecutar Descifrado Cuántico", key="btn_descifrar_q"):
            if not texto_cifrado_input:
                st.warning("Por favor, introduce un texto para descifrar.")
            else:
                with st.spinner("Inicializando registro de qubits y aplicando compuertas lógicas..."):
                    time.sleep(1.5)
                
                # Simulación matemática de comportamiento de qubits (ej: inversión de estados / desplazamiento cuántico)
                texto_descifrado = "".join([chr(ord(c) - 3) if c.isalnum() else c for c in texto_cifrado_input])
                
                st.success("¡Colapso de función de onda completado con éxito!")
                
                # Resultado descifrado
                st.subheader("Resultado Descifrado:")
                st.code(texto_descifrado, language="text")

                # Solución del proceso de descifrado paso a paso
                st.markdown("### 🧠 Solución del Proceso de Descifrado:")
                st.info(
                    f"1. **Superposición inicial:** Se mapeó el texto cifrado (`{texto_cifrado_input}`) en un vector de estados de 8 qubits.\n"
                    f"2. **Entrelazamiento:** Se aplicaron puertas de interferencia (tipo Hadamard simulada) para aislar el ruido de encriptación.\n"
                    f"3. **Colapso:** Se redujo la matriz de probabilidad obteniendo el texto plano resultante: `{texto_descifrado}` aplicando un desplazamiento ASCII inverso de -3."
                )

    # --- SECCIÓN 2: ARCHIVO DE MENSAJES CIFRADOS ---
    with tab2:
        st.header("Archivo de Mensajes Cifrados")
        st.write("Guarda nuevos mensajes cifrados junto con sus métodos o descripciones de descifrado.")

        with st.form("form_archivo_mensaje"):
            nuevo_titulo = st.text_input("Título / Referencia del mensaje:")
            nuevo_cifrado = st.text_area("Mensaje Cifrado:")
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
                    st.markdown(f"**Mensaje Cifrado:**")
                    st.code(m["cifrado"], language="text")
                    st.markdown(f"**Modo / Solución de Descifrado:**")
                    st.write(m["metodo"])
