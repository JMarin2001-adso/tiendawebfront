const API_BASE = "http://127.0.0.1:8000";

// Obtener ID del pedido desde la URL
const urlParams = new URLSearchParams(window.location.search);
const id_pedido = urlParams.get("id");

const pedidoInfo = document.getElementById("pedido-info");


// Cargar información del pedido

async function cargarPedido() {
    if (!id_pedido) {
        pedidoInfo.innerHTML = "<p>Error: No se recibió el ID del pedido.</p>";
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/pedido/detalle/${id_pedido}`);
        const data = await res.json();

        // pedido agregado, se vera detallado
        console.log("DATA PEDIDO:", data);

        if (!res.ok || data.status === "error") {
            pedidoInfo.innerHTML = `<p>No se pudo cargar la información del pedido.</p>`;
            return;
        }

        mostrarPedido(data);

    } catch (error) {
        pedidoInfo.innerHTML = "<p>Error al conectar con el servidor.</p>";
    }
}

function mostrarPedido(data) {

    //el pedido se mostrara cuando se agrege, junto con datos basicos de cliente
    const productos = Array.isArray(data.productos) ? data.productos : [];

    pedidoInfo.innerHTML = `
        <h3>Pedido #${data.id_pedido}</h3>

        <p><strong>Cliente:</strong> ${data.nombre_cliente}</p>
        <p><strong>Dirección:</strong> ${data.direccion}</p>
        <p><strong>Teléfono:</strong> ${data.telefono}</p>
        <p><strong>Correo:</strong> ${data.correo}</p>

        <p><strong>Estado actual:</strong> ${data.estado}</p>

        <h4>Productos solicitados:</h4>
        <table class="tabla-productos">
            <thead>
                <tr>
                    <th>Producto</th>
                    <th>Cantidad</th>
                    <th>Valor unitario</th>
                </tr>
            </thead>
            <tbody>
                ${
                    productos.length > 0
                    ? productos.map(i => `
                        <tr>
                            <td>${i.nombre_producto}</td>
                            <td>${i.cantidad}</td>
                            <td>$${Number(i.precio_unitario).toLocaleString()}</td>
                        </tr>
                    `).join("")
                    : `<tr><td colspan="3">No hay productos en este pedido</td></tr>`
                }
            </tbody>
        </table>

        ${data.estado === "pagado" ? `
            <div class="despacho-box">
            <h4>Pedido aprobado</h4>
            <p>Este pedido ya fue validado y está listo para despacho.</p>
            <button id="btnConfirmarDespacho" class="btn confirmar">
               Confirmar despacho
            </button>
            </div>
            ` : ""}
    `;

    if (data.estado === "pagado") {
        document
            .getElementById("btnConfirmarDespacho")
            .addEventListener("click", confirmarDespacho);
    }
}


// funciones de aprobar pedido

document.getElementById("btnAprobar").addEventListener("click", async () => {
    Swal.fire({
        title: "Procesando...",
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading()
    });

    const res = await fetch(`${API_BASE}/pedido/aprobar/${id_pedido}`, {
        method: "PUT"
    });

    const data = await res.json();

    Swal.close();

    if (res.ok) {
        Swal.fire("Pedido aprobado", "El pedido fue aprobado.", "success")
            .then(() => cargarPedido());
    } else {
        Swal.fire("Error", data.detalle ||"No se pudo aprobar el pedido.", "error");
    }
});

// funcion de rechazar pedido
document.getElementById("btnRechazar").addEventListener("click", async () => {

    const { value: motivo } = await Swal.fire({
        title: "Motivo de rechazo",
        input: "text",
        inputPlaceholder: "Ej: Pago inválido",
        showCancelButton: true
    });

    if (!motivo) return;

    const res = await fetch(`${API_BASE}/pedido/rechazar/${id_pedido}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ motivo })
    });

    const data = await res.json();

    if (res.ok) {
        Swal.fire("Rechazado", "El pedido fue rechazado.", "info")
            .then(() => window.location.href = "panelempleado.html");
    } else {
        Swal.fire("Error", "No se pudo rechazar el pedido.", "error");
    }
});

cargarPedido();

//se confirma despacho de envio, se manda notificacion 
async function confirmarDespacho() {
    Swal.fire({
        title: "Confirmar despacho",
        text: "¿Deseas marcar este pedido como despachado?",
        showCancelButton: true,
        confirmButtonText: "Sí, despachar"
    }).then(async (result) => {
        if (!result.isConfirmed) return;

        const res = await fetch(`${API_BASE}/pedido/despachar/${id_pedido}`, {
            method: "PUT"
        });

        const data = await res.json();

        if (res.ok) {
            Swal.fire(
                "Despachado",
                "El pedido fue marcado como despachado y el inventario actualizado.",
                "success"
            ). then(()=>{
                window.location.href =`factura_elec.html?id=${id_pedido}`
            })
        } else {
            Swal.fire("Error", "No se pudo despachar el pedido.", "error");
        }
    });
}

//validar sesion de empleado 
const empleadoId = localStorage.getItem("empleadoId");
const empleadoNombre = localStorage.getItem("empleadoNombre");

if (!empleadoId) {
    window.location.href = "loginempleado.html";
}

// Mostrar nombre
document.getElementById("user-name").textContent = empleadoNombre;


//menu hamburguesa 
const sidebar = document.getElementById("sidebar");
document.getElementById("menu-toggle").addEventListener("click", () => {
    sidebar.classList.toggle("open");
});


//usuario-dropdown

const userDropdown = document.getElementById("user-dropdown");
document.getElementById("user-icon").addEventListener("click", () => {
    userDropdown.classList.toggle("show");
});


// logout

document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("empleadoId");
    localStorage.removeItem("empleadoNombre");
    localStorage.removeItem("empleadoRol");
    window.location.href = "loginempleado.html";
});

//notificacion- dropdown 
const notifIcon = document.getElementById("notif-icon");
const notifDropdown = document.getElementById("notif-dropdown");

notifIcon.addEventListener("click", () => {
    notifDropdown.classList.toggle("show");
});

//cargar notificaciones 
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


//navegacion por pagina sidebar 

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
