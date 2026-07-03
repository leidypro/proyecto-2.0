
function obtenerCSRFToken() {

    let cookieValue = null;

    const name = 'csrftoken';

    if (document.cookie && document.cookie !== '') {

        const cookies = document.cookie.split(';');

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + '=')) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}
let miModalInstancia = null;
let campoActivo = null; // 👈 Variable para saber qué select actualizar

function abrirModalCreacionDesdeCampo(fieldId) {
	const select = document.getElementById(fieldId);

	if (!select) {
		console.error('Select no encontrado:', fieldId);
		return;
	}

	const url = select.dataset.crearUrl; // data-crear-url
	const fieldName = select.name;

	if (!url) {
		console.error('El select no tiene data-crear-url');
		return;
	}

	abrirModalCreacion(url, fieldName);
}

function MostrarMensaje(Texto) {
	Swal.fire({
		icon: 'success',
		title: 'Registro creado',
		text: Texto,
		showConfirmButton: false,
		timer: 2000,
		timerProgressBar: true
	})
}

function abrirModalCreacion(url, fieldName) {
	const modalElement = document.getElementById('modalGeneral');
	const contenedor = document.getElementById('contenedorModal');

	campoActivo = fieldName;

	fetch(url)
		.then(response => response.text())
		.then(html => {
			contenedor.innerHTML = "";
			contenedor.innerHTML = html;

			if (miModalInstancia) { miModalInstancia.dispose(); }

			miModalInstancia = new bootstrap.Modal(modalElement);
			miModalInstancia.show();
			const guardar = document.getElementById('Guardar')
			console.log(guardar)
			const nombre = contenedor.querySelector('#id_nombre');
			const error = document.getElementById("error_nombre")
			nombre.addEventListener('input', function(){
				error.innerHTML = ""
				let errores = []
				let valor = nombre.value
					if (/[0-9]/.test(valor))
						{ errores.push("No debe contener numeros") }
					if(fieldName === "unidadMedidaId" && valor.length > 4){
						errores.push("No debe contener mas de 4 digitos")
					}
					if (/[#$@+\-]/.test(valor)) 
						{ errores.push("No debe tener caracteres especiales"); }
					if(valor.length === 0){
						guardar.disabled = true
						error.classList.remove("error-box", "active" , "pass-box"); return; } 
					if (errores.length > 0){ 
						guardar.disabled = true
						errores.forEach(err => { 
							error.classList.add("error-box", "active"); 
							error.classList.remove("pass-box"); 
							console.log(err) 
							const div = document.createElement("div") 
							div.textContent = err; div.classList.add("error-item"); 
							error.appendChild(div); });} 
					else{
						guardar.disabled = false
						error.classList.add("pass-box", "active"); 
						error.classList.remove("error-box"); 
						const div = document.createElement("div") 
						div.textContent = "No se encontraron errores"; 
						div.classList.add("error-item"); 
						error.appendChild(div); }
			})
			// Configurar botones de cerrar
			const btnCerrar = contenedor.querySelectorAll('[data-bs-dismiss="modal"]');
			btnCerrar.forEach(boton => {
				boton.onclick = () => miModalInstancia.hide();
			});

			const form = contenedor.querySelector('#formGenericoModal');
			form.addEventListener('submit', function (e) {
				e.preventDefault();
				const formData = new FormData(this);
				limpiarErrores(form);

				fetch(this.action, {
					method: 'POST',
					body: formData,
					headers: { 'X-Requested-With': 'XMLHttpRequest' }
				})
					.then(res => res.json())
					.then(data => {
						if (data.success) {
							miModalInstancia.hide();
							if (data.message) {
								MostrarMensaje(data.message)
							}
							actualizarSelectDinamico(data.id, data.nombre);
						} else {
							mostrarErrores(form, data.errors);
						}
					})
					.catch(error => console.error('Error:', error));
			});
		});
}

// Reemplaza tu 'actualizarSelectTipo' por esta función genérica
function actualizarSelectDinamico(id, nombre) {
	if (campoActivo) {
		// Busca el select por el nombre que guardamos al abrir el modal
		const select = document.querySelector(`select[name="${campoActivo}"]`);
		if (select) {
			const nuevaOpcion = new Option(nombre, id, true, true);
			select.add(nuevaOpcion);
			// Disparamos el evento change por si tienes otras dependencias
			select.dispatchEvent(new Event('change'));
		}
	}
}

function mostrarErrores(form, errores) {
	for (let campo in errores) {
		const input = form.querySelector(`[name="${campo}"]`);
		if (input) {
			input.classList.add('is-invalid');
			const errorDiv = document.getElementById(`error_${campo}`);
			if (errorDiv) {
				errorDiv.innerText = errores[campo].join(' ');
			}
		}
	}
}

function limpiarErrores(form) {
	form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
	form.querySelectorAll('.invalid-feedback').forEach(el => el.innerText = '');
}

function abrirPerfil() {
	const modalElement = document.getElementById('modalGeneral');
	const contenedor = document.getElementById('contenedorModal');
	const nombre = document.getElementById('name')
	const img = document.getElementById('img')

	fetch("/colegio/usuario/perfil/", {
		headers: { 'X-Requested-With': 'XMLHttpRequest' }
	})
		.then(res => res.json().catch(() => null)) // intenta parsear JSON
		.then(data => {
			if (data && data.redirect) {
				window.location.href = data.redirect; // usuario no logueado
				return;
			}

			// si no es JSON, asumimos HTML (usuario logueado)
			return fetch("/colegio/usuario/perfil/")
		})
		.then(response => response.text())
		.then(html => {
			contenedor.innerHTML = html;


			if (miModalInstancia) { miModalInstancia.dispose(); }
			miModalInstancia = new bootstrap.Modal(modalElement);
			miModalInstancia.show();
			const contraseña = document.getElementById("password")
			const error = document.getElementById("error")
			const tieneMin = /[a-z]/.test(contraseña)
			const errorBox = document.getElementById("errorBox");

			contraseña.addEventListener("input", () => {

				const valor = contraseña.value;
				errorBox.innerHTML = "";

				let errores = [];
				if (valor.length < 5) {
					errores.push("Mínimo 5 caracteres");
				}

				if (!/[A-Z]/.test(valor)) {
					errores.push("Debe tener una mayúscula");
				}

				if (!/[0-9]/.test(valor)) {
					errores.push("Debe tener un número");
				}

				if (!/[#$@+\-]/.test(valor)) {
					errores.push("Debe tener un símbolo especial");
				}

				if (valor.length === 0) {
					errorBox.classList.remove("active", "error-box", "pass-box");
					return;
				}

				// ❌ HAY ERRORES
				if (errores.length > 0) {

					errorBox.classList.add("error-box", "active");
					errorBox.classList.remove("pass-box");

					errores.forEach(err => {
						const div = document.createElement("div");
						div.textContent = err;
						div.classList.add("error-item");
						errorBox.appendChild(div);
					});

				}
				else {

					errorBox.classList.add("pass-box", "active");
					errorBox.classList.remove("error-box");

					const div = document.createElement("div");
					div.textContent = "Contraseña segura";
					div.classList.add("error-item");
					errorBox.appendChild(div);
				}

			});

			const btnCerrar = contenedor.querySelectorAll('[data-bs-dismiss="modal"]');
			btnCerrar.forEach(boton => {
				boton.onclick = () => miModalInstancia.hide();
			});

			const form = contenedor.querySelector('#formPerfil');
			if (form) {
				form.addEventListener('submit', function (e) {
					e.preventDefault();
					const formData = new FormData(this);
					const mensaje = document.getElementById('mensajePerfil');

					fetch(this.action, {
						method: 'POST',
						body: formData,
						headers: { 'X-Requested-With': 'XMLHttpRequest' }
					})
						.then(res => res.json())
						.then(data => {
							if (data.success) {
								miModalInstancia.hide();
								if (data.message) { MostrarMensaje(data.message); }
								if (nombre && data.nombre) {
									nombre.innerText = data.nombre
								}
							} else {
								mensaje.innerHTML = `<div class="alert alert-danger p-2">${data.message || 'Error al actualizar.'}</div>`;
							}
						})
						.catch(error => console.error('Error:', error));
				});
			}
		})
		.catch(err => console.error("Error al cargar perfil:", err));
}

async function abrirNotificacion() {
    const modalElement = document.getElementById('modalGeneral');
    const contenedor = document.getElementById('contenedorModal');

    // Loader adaptado a tu paleta (Azul oscuro institucional)
    contenedor.innerHTML = `
        <div class="text-center p-5">
            <div class="spinner-border" style="color: #1d3557;" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-3 mb-0 text-secondary fw-medium">Cargando notificaciones...</p>
        </div>
    `;

    try {
        const response = await fetch("/colegio/mis_notificaciones/", {
            headers: { "X-Requested-With": "XMLHttpRequest" }
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const html = await response.text();
        contenedor.innerHTML = html;

        // Cerrar modal anterior si existe
        if (miModalInstancia) {
            miModalInstancia.hide();
            miModalInstancia.dispose?.();
        }

        // Crear e inicializar modal nuevo
        miModalInstancia = new bootstrap.Modal(modalElement);
        miModalInstancia.show();

        // ===================================
        // ACCIÓN: MARCAR COMO LEÍDA
        // ===================================
        const botones = contenedor.querySelectorAll(".btn-marcar-leida");

        botones.forEach(boton => {
            boton.addEventListener("click", async function () {
                const item = this.closest("[data-notificacion-id]");
                const id = item.dataset.notificacionId;

                try {
                    const response = await fetch(`/colegio/mis_notificaciones/${id}/leer/`, {
                        method: "POST",
                        headers: {
                            "X-Requested-With": "XMLHttpRequest",
                            "X-CSRFToken": obtenerCSRFToken()
                        }
                    });

                    const data = await response.json();

                    if (data.success) {
                        // 1. Actualizar el contenedor padre (Cambiar fondo a blanco y borde a gris)
                        item.style.setProperty("border-left", "5px solid #6c757d", "important");
                        item.style.backgroundColor = "#ffffff";

                        // 2. Cambiar dinámicamente el Icono del sobre (De cerrado-rojo a abierto-gris)
                        const iconoContenedor = item.querySelector(".fa-envelope");
                        if (iconoContenedor) {
                            iconoContenedor.classList.remove("fa-envelope", "text-danger");
                            iconoContenedor.classList.add("fa-envelope-open", "text-muted");
                            iconoContenedor.parentElement.style.backgroundColor = "#e9ecef";
                        }

                        // 3. Cambiar el Badge de estado de "Nuevo" a "Leído"
                        const badge = item.querySelector(".badge");
                        if (badge) {
                            badge.textContent = "Leído";
                            badge.style.backgroundColor = "#6c757d";
                        }

                        // 4. Reemplazar el botón dinámicamente para mantener la simetría estática
                        const contenedorBoton = this.parentElement;
                        contenedorBoton.innerHTML = `
                            <button class="btn btn-sm px-3 rounded-pill btn-outline-secondary border-0" 
                                    style="font-size: 0.8rem; white-space: nowrap;" disabled>
                                <i class="fa-solid fa-check-double me-1"></i> Ya revisado
                            </button>
                        `;
                    }

                } catch (err) {
                    console.error("Error marcando leída:", err);
                }
            });
        });

        // ===================================
        // CONTROL: BOTONES CERRAR MODAL
        // ===================================
        // Selector corregido en una sola cadena de texto
        const btnCerrar = contenedor.querySelectorAll('[data-bs-dismiss="modal"], #btnCerrarNoti2');
        
        btnCerrar.forEach(boton => {
            boton.onclick = () => miModalInstancia.hide();
        });

        // ===================================
        // LIMPIEZA AL CERRAR
        // ===================================
        modalElement.addEventListener("hidden.bs.modal", () => {
            contenedor.innerHTML = "";
        }, { once: true });

    } catch (error) {
        console.error("Error al cargar notificaciones:", error);
        contenedor.innerHTML = `
            <div class="alert alert-danger m-3 border-0 rounded-3 shadow-sm text-center">
                <i class="fa-solid fa-triangle-exclamation me-2"></i>
                No se pudieron cargar las notificaciones en este momento.
            </div>
        `;
    }
}
// ------------------------------
// ELEMENTOS DEL DOM
// ------------------------------
const chatBox = document.getElementById('chatBox');
const input = document.getElementById('inputMensaje');
const boton = document.getElementById('btnEnviar');

const btnChat = document.getElementById("btnChat");
const chatContainer = document.getElementById("chatContainer");
const cerrar = document.getElementById("cerrarChat");

// ------------------------------
// FUNCIONES DE CONTROL DEL CHAT
// ------------------------------

// 🔥 Abrir chat
function abrirChat() {
  chatContainer.classList.add("chat-activo");
  btnChat.classList.add("oculto");
  const accessBtn = document.getElementById('btnAccessibility');
  if (accessBtn) accessBtn.classList.add('oculto');
}

// 🔥 Cerrar chat
function cerrarChat() {
  chatContainer.classList.remove("chat-activo");
  btnChat.classList.remove("oculto");
  const accessBtn = document.getElementById('btnAccessibility');
  if (accessBtn) accessBtn.classList.remove('oculto');
}

// Eventos abrir/cerrar
btnChat.addEventListener("click", abrirChat);
cerrar.addEventListener("click", cerrarChat);

// 🔥 Cerrar al hacer clic fuera
document.addEventListener("click", function (e) {
  const clickDentroChat = chatContainer.contains(e.target);
  const clickBoton = btnChat.contains(e.target);

  if (!clickDentroChat && !clickBoton) {
    cerrarChat();
  }
});

// ------------------------------
// FUNCIONES DEL CHAT
// ------------------------------

// 💬 Agregar mensaje
function agregarMensaje(texto, tipo) {
  const mensaje = document.createElement('div');
  mensaje.classList.add('mensaje', tipo);

  // Etiqueta bonita (Tú / Bot)
  const autor = tipo === 'usuario' ? 'Tú' : 'Bot';

  mensaje.innerHTML = `<strong>${autor}:</strong> ${texto}`;

  chatBox.appendChild(mensaje);

  // Scroll automático
  chatBox.scrollTop = chatBox.scrollHeight;
}

// ⏳ Mostrar "escribiendo..."
function mostrarEscribiendo() {
  const mensaje = document.createElement('div');
  mensaje.classList.add('mensaje', 'bot');
  mensaje.id = "escribiendo";

  mensaje.innerHTML = "Bot está escribiendo...";

  chatBox.appendChild(mensaje);
  chatBox.scrollTop = chatBox.scrollHeight;
}

// ❌ Quitar "escribiendo..."
function quitarEscribiendo() {
  const escribiendo = document.getElementById("escribiendo");
  if (escribiendo) escribiendo.remove();
}

// 📤 Enviar mensaje
function enviarMensaje() {
  const texto = input.value.trim();

  if (texto === '') return;

  // Mostrar mensaje usuario
  agregarMensaje(texto, 'usuario');

  // Limpiar input
  input.value = '';

  // Mostrar "escribiendo..."
  mostrarEscribiendo();

  // Petición al backend
  fetch('/colegio/preguntas1/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ mensaje: texto }),
  })
    .then((res) => res.json())
    .then((data) => {
      quitarEscribiendo();
	  console.log(data.rutas_links)
      agregarMensaje(data.respuesta, 'bot');
    })
    .catch(() => {
      quitarEscribiendo();
      agregarMensaje('Error al conectar con el servidor', 'bot');
    });
}

// ------------------------------
// EVENTOS
// ------------------------------

// Botón enviar
boton.addEventListener('click', enviarMensaje);

// Enter para enviar
input.addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    enviarMensaje();
  }
});

