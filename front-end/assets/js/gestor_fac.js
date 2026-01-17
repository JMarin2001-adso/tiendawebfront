const API_BASE = "http://127.0.0.1:8000";

function buscarFactura() {
    const inputDocumento = document.getElementById("documento").value.trim();
    const inputFactura = document.getElementById("factura").value.trim();
    const tabla = document.getElementById("tablaFacturas");

    tabla.innerHTML = "";

    // Validador de facturas
    if (!inputDocumento && !inputFactura) {
        tabla.innerHTML = `
            <tr>
                <td colspan="8">Ingrese número de documento o número de factura</td>
            </tr>`;
        return;
    }

    if (inputDocumento && inputFactura) {
        tabla.innerHTML = `
            <tr>
                <td colspan="8">Use solo un campo de búsqueda</td>
            </tr>`;
        return;
    }

    let url = "";

    if (inputDocumento) {
        url = `${API_BASE}/factura/buscar-por-documento/${inputDocumento}`;
    } else {
        url = `${API_BASE}/factura/buscar-por-factura/${inputFactura}`;
    }

    fetch(url)
        .then(res => res.json())
        .then(response => {

            if (!response.success || response.data.length === 0) {
                tabla.innerHTML = `
                    <tr>
                        <td colspan="8">No se encontraron resultados</td>
                    </tr>`;
                return;
            }
            //tabla donde se valida los datos del cliente.
            response.data.forEach(f => {
                tabla.innerHTML += `
                    <tr>
                        <td>${f.numero_factura}</td>
                        <td>${f.nombre_cliente}</td>
                        <td>${f.documento_cliente}</td>
                        <td>${new Date(f.fecha).toLocaleDateString()}</td>
                        <td>$${Number(f.total).toLocaleString()}</td>
                        <td class="estado ${f.estado.toLowerCase()}">${f.estado}</td>
                        <td>${f.metodo_pago || '-'}</td>
                        <td>
                            <button class="btn-ver" onclick="verFactura(${f.id_factura})">
                                Ver
                            </button>
                        </td>
                    </tr>
                `;
            });
        })
        .catch(error => {
            tabla.innerHTML = `
                <tr>
                    <td colspan="8">Error al consultar facturas</td>
                </tr>`;
            console.error(error);
        });
}
//previsualizacion de factura
function verFactura(idFactura) {
    fetch(`${API_BASE}/factura/detalle/${idFactura}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert(data.message);
                return;
            }

            const f = data.factura;

            // Datos principales
            document.getElementById("m-numero").innerText = f.numero_factura;
            document.getElementById("m-cliente").innerText = f.cliente;
            document.getElementById("m-documento").innerText = f.documento ?? "N/A";
            document.getElementById("m-estado").innerText = f.estado;
            document.getElementById("m-total").innerText =
                Number(f.total).toLocaleString();

            // Productos
            const tbody = document.getElementById("m-productos");
            tbody.innerHTML = "";

            if (f.productos.length === 0) {
                tbody.innerHTML = `
                  <tr><td colspan="4">Sin productos</td></tr>
                `;
            } else {
                f.productos.forEach(p => {
                    tbody.innerHTML += `
                        <tr>
                          <td>${p.nombre}</td>
                          <td>${p.cantidad}</td>
                          <td>$${Number(p.precio_unitario).toLocaleString()}</td>
                          <td>$${Number(p.subtotal).toLocaleString()}</td>
                        </tr>
                    `;
                });
            }

            // Mostrar modal
            document.getElementById("modalFactura").style.display = "block";
        })
        .catch(err => {
            alert("Error al cargar la factura");
            console.error(err);
        });
}

function cerrarModal() {
    document.getElementById("modalFactura").style.display = "none";
}

//Validacion de usuario
const empleadoId = localStorage.getItem("empleadoId");
const empleadoNombre = localStorage.getItem("empleadoNombre");

if (!empleadoId) {
    window.location.href = "loginempleado.html";
}

//Mostrar nombre usuario
document.getElementById("user-name").textContent = empleadoNombre;


//Menu Hamburguesa
const sidebar = document.getElementById("sidebar");
document.getElementById("menu-toggle").addEventListener("click", () => {
    sidebar.classList.toggle("open");
});


//Usuario-Dropdown
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

//Notificaciones-Dropdown
const notifIcon = document.getElementById("notif-icon");
const notifDropdown = document.getElementById("notif-dropdown");

notifIcon.addEventListener("click", () => {
    notifDropdown.classList.toggle("show");
});

//Cargar notificiaciones
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


//Navegacion entre paginas del sidebar

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