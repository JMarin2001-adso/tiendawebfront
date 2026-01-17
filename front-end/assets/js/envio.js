const API_BASE = "http://127.0.0.1:8000";

//Tabla de envios
const tablaEnvios = document.getElementById("tablaEnvios");
const inputBuscar = document.getElementById("buscar");

let enviosCache = [];


//Cargar envios desde el backend
async function cargarEnvios() {
    try {
        const res = await fetch(`${API_BASE}/envio/listar`);
        const data = await res.json();

        enviosCache = data;
        renderTabla(data);

    } catch (error) {
        console.error("Error cargando envíos:", error);
    }
}


//Render tabla

function renderTabla(envios) {
    tablaEnvios.innerHTML = "";

    if (envios.length === 0) {
        tablaEnvios.innerHTML = `
            <tr>
                <td colspan="5" style="text-align:center;">
                    No hay envíos registrados
                </td>
            </tr>
        `;
        return;
    }

    envios.forEach(e => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${e.id_envio}</td>
            <td>${e.tracking}</td>
            <td>${e.cliente}</td>
            <td>${e.ciudad ?? "-"}</td>
            <td>
                <span class="estado ${estadoClase(e.estado)}">
                    ${e.estado}
                </span>
                ${botonesEstado(e)}
            </td>
        `;

        tablaEnvios.appendChild(tr);
    });
}


//Botones segun estado

function botonesEstado(envio) {
    if (envio.estado === "Pendiente") {
        return `
            <br>
            <button class="btn-accion"
                onclick="marcarTransito(${envio.id_envio})">
                🚚 En tránsito
            </button>
        `;
    }

    if (envio.estado === "En tránsito") {
        return `
            <br>
            <button class="btn-accion success"
                onclick="confirmarEntrega(${envio.id_envio})">
                ✅ Entregar
            </button>
        `;
    }

    return "";
}


//Clase css por estado

function estadoClase(estado) {
    if (estado === "Pendiente") return "pendiente";
    if (estado === "En tránsito") return "transito";
    if (estado === "Entregado") return "entregado";
    return "";
}

//Buscador

inputBuscar.addEventListener("input", e => {
    const q = e.target.value.toLowerCase();
    const filtrados = enviosCache.filter(envio =>
        envio.tracking.toLowerCase().includes(q)
    );
    renderTabla(filtrados);
});

//Cambio de estado a En transito
async function marcarTransito(id_envio) {
    try {
        const res = await fetch(`${API_BASE}/envio/transito/${id_envio}`, {
            method: "PUT"
        });
        const data = await res.json();

        if (data.status === "ok") {
            alert(data.mensaje);
            cargarEnvios();
        } else {
            alert(data.detalle);
        }

    } catch (error) {
        alert("Error de conexión");
    }
}

//Confirmar entrega

async function confirmarEntrega(id_envio) {
    try {
        const res = await fetch(`${API_BASE}/envio/entregar/${id_envio}`, {
            method: "PUT"
        });
        const data = await res.json();

        if (data.status === "ok") {
            alert(data.mensaje);
            cargarEnvios();
        } else {
            alert(data.detalle);
        }

    } catch (error) {
        alert("Error de conexión");
    }
}

//Inicio

document.addEventListener("DOMContentLoaded", () => {
    cargarEnvios();
});

//Validar sesion de empleado.
const empleadoId = localStorage.getItem("empleadoId");
const empleadoNombre = localStorage.getItem("empleadoNombre");

if (!empleadoId) {
    window.location.href = "loginempleado.html";
}

//Mostrar nombre en tobar
document.getElementById("user-name").textContent = empleadoNombre;


// Manejo menu hamburguesa
const sidebar = document.getElementById("sidebar");
document.getElementById("menu-toggle").addEventListener("click", () => {
    sidebar.classList.toggle("open");
});


// Usuario-Dropdwon
const userDropdown = document.getElementById("user-dropdown");
document.getElementById("user-icon").addEventListener("click", () => {
    userDropdown.classList.toggle("show");
});


// Logout
document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("empleadoId");
    localStorage.removeItem("empleadoNombre");
    localStorage.removeItem("empleadoRol");
    window.location.href = "loginempleado.html";
});

//Notificacione-Dropdown
const notifIcon = document.getElementById("notif-icon");
const notifDropdown = document.getElementById("notif-dropdown");

notifIcon.addEventListener("click", () => {
    notifDropdown.classList.toggle("show");
});

//Cargar notificaciones de compra
async function cargarNotificaciones() {
    try {
        const res = await fetch(`${API_BASE}/pedido/pendientes`);
        const pedidos = await res.json();

        // Cantidad
        document.getElementById("notif-count").textContent = pedidos.length;

        // Lista
        const notifList = document.getElementById("notif-list");
        notifList.innerHTML = "";

        pedidos.forEach(p => {
            let li = document.createElement("li");
            li.textContent = `Pedido #${p.id_pedido} en revisión`;
            
            li.addEventListener("click", () => {
                window.location.href = `revision_pedido.html?id=${p.id_pedido}`;
            });
            
            notifList.appendChild(li);
        });


    } catch (error) {
        console.error("Error cargando notificaciones:", error);
    }
}

// Ejecutar al cargar el panel
cargarNotificaciones();

// Consultar cada 8 segundos
setInterval(cargarNotificaciones, 8000);


//Navegacion por paginas del Sidebar

document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", (e) => {
        e.preventDefault(); // evitar salto arriba

        const destino = item.getAttribute("data-page");

        if (destino) {
            window.location.href = destino;
        }
    });
});

// Mostrar / ocultar submenú de Transacciones
document.getElementById("btn-transacciones").addEventListener("click", () => {
    const submenu = document.getElementById("submenu-transacciones");
    submenu.style.display =
        submenu.style.display === "block" ? "none" : "block";
});

// Navegación de submenú
document.querySelectorAll(".nav-subitem").forEach(item => {
    item.addEventListener("click", () => {
        const page = item.getAttribute("data-page");
        window.location.href = page;
    });
});