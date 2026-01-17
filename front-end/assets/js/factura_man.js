const API_BASE = "http://127.0.0.1:8000";

//variables
let clienteSeleccionado = null;
let productosFactura = [];
let productoActual = null;

function openModal(id) {
    document.getElementById(id).style.display = "flex";
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
}

async function buscarCliente() {
    const documento = document.getElementById("documento").value.trim();
    const estado = document.getElementById("estadoCliente");

    if (!documento) {
        estado.innerText = "Ingrese un documento";
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/factura/busqueda-documento/${documento}`);
        const res = await response.json();

        if (res && res.success && res.data) {
            clienteSeleccionado = Array.isArray(res.data) ? res.data[0] : res.data;

            // se llenan los input, para guardar datos
            document.getElementById("nombre").value = clienteSeleccionado.nombre || "";
            document.getElementById("correo").value = clienteSeleccionado.correo || "";
            document.getElementById("telefono").value = clienteSeleccionado.telefono || "";
            document.getElementById("direccion").value = clienteSeleccionado.direccion || "";

            estado.innerText = "Cliente encontrado ✔";
            mostrarClienteResumen();
        } else {
            estado.innerText = "Cliente no encontrado";
            mostrarFormulario();
        }
    } catch (error) {
        estado.innerText = "Error en la búsqueda";
    }
}

async function guardarCliente() {
    const estado = document.getElementById("estadoCliente");
    
    // objeto que captura los datos del formulario
    const nuevoCliente = {
        documento: document.getElementById("documento").value.trim(),
        nombre: document.getElementById("nombre").value.trim(),
        correo: document.getElementById("correo").value.trim(),
        telefono: document.getElementById("telefono").value.trim(),
        direccion: document.getElementById("direccion").value.trim()
    };

    try {
        const response = await fetch(`${API_BASE}/factura/cliente/manual`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(nuevoCliente)
        });

        const res = await response.json();

        if (response.ok && res.success) {
            clienteSeleccionado = res.data; 

            estado.innerText = "Cliente creado correctamente ✔";
            mostrarClienteResumen();
            closeModal("clientModal");
        } else {
            alert(res.message || "No se pudo crear el cliente");
        }
    } catch (error) {
        console.error("Error al guardar:", error);
        alert("Error de conexión al intentar guardar");
    }
}

function mostrarClienteResumen() {
    const box = document.getElementById("displayClient");
    const summary = document.getElementById("clientDataSummary");

    if (!clienteSeleccionado) return;

    box.style.display = "block";
    summary.innerHTML = `
        <p><b>${clienteSeleccionado.nombre || 'Sin nombre'}</b></p>
        <p>Doc: ${clienteSeleccionado.documento || 'N/A'}</p>
        <p>Email: ${clienteSeleccionado.correo || 'N/A'}</p>
        <p>Dir: ${clienteSeleccionado.direccion || 'N/A'}</p>
    `;
}

//seccion de productos, descargar producto y ver en pantalla
function filtrarProductos() {
    const texto = document.getElementById("buscarProducto").value.toLowerCase();
    const lista = document.getElementById("listaProductos");

    if (texto.length < 2) {
        lista.innerHTML = "";
        return;
    }

    fetch(`${API_BASE}/producto`)
        .then(res => res.json())
        .then(res => {
            lista.innerHTML = "";
            res.data
                .filter(p => p.nombre.toLowerCase().includes(texto))
                .forEach(p => {
                    const li = document.createElement("li");
                    li.textContent = `${p.nombre} (Stock: ${p.stock_actual})`;
                    li.onclick = () => seleccionarProducto(p);
                    lista.appendChild(li);
                });
        });
}

function seleccionarProducto(p) {
    productoActual = p;
    document.getElementById("prodNombre").innerText = p.nombre;
    document.getElementById("prodStock").innerText = p.stock_actual;
    document.getElementById("detalleProducto").style.display = "block";
}

function agregarProducto() {
    const cantidad = parseInt(document.getElementById("cantidadProducto").value);

    if (!productoActual || cantidad <= 0) return;

    productosFactura.push({
        id_producto: productoActual.id_producto,
        nombre: productoActual.nombre,
        cantidad: cantidad,
        precio_unitario: productoActual.precio
    });

    actualizarTabla();
    closeModal("productModal");
}



//tabla de factura, se visualiza el nombre y cantida de prosucto
function actualizarTabla() {
    const tbody = document.querySelector("#invoiceTable tbody");
    tbody.innerHTML = "";

    let total = 0;

    productosFactura.forEach((p, index) => {
        const subtotal = p.cantidad * p.precio_unitario;
        total += subtotal;

        tbody.innerHTML += `
            <tr>
                <td>${p.nombre}</td>
                <td>${p.cantidad}</td>
                <td>$${p.precio_unitario}</td>
                <td>$${subtotal}</td>
                <td><button onclick="eliminarProducto(${index})">X</button></td>
            </tr>
        `;
    });

    document.getElementById("totalInvoice").innerText = total;
}

function eliminarProducto(index) {
    productosFactura.splice(index, 1);
    actualizarTabla();
}

//generar factura manual
function generateInvoice() {
    if (!clienteSeleccionado) {
        alert("Debe seleccionar un cliente primero");
        return;
    }

    if (productosFactura.length === 0) {
        alert("Debe agregar al menos un producto");
        return;
    }

    // datos del clinete aparecen en resumen de factura
    const datosCliente = clienteSeleccionado.data || clienteSeleccionado;

    const payload = {
        cliente: {
            documento: datosCliente.documento,
            nombre: datosCliente.nombre,
            correo: datosCliente.correo,
            telefono: datosCliente.telefono,
            direccion: datosCliente.direccion
        },
        //se visualizan los productos ordenados
        productos: productosFactura.map(p => ({
            id_producto: p.id_producto,
            cantidad: p.cantidad,
            precio_unitario: p.precio_unitario
        }))
    };

    // 3. Envío de datos al servidor
    fetch(`${API_BASE}/factura/manual`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(res => {
        if (res.success) {
            alert("Factura generada correctamente ✔");

            const display = document.getElementById("numeroFacturaDisplay");
            const modal = document.getElementById("modalConfirmacion");

            if (display && modal) {
                display.innerText = res.numero_factura;
                modal.style.display = "flex";
            }
        } else {
            console.error("Detalle del error:", res);
            alert("Error: " + (res.message || "Los datos no son válidos para el servidor"));
        }
    })
    .catch((err) => {
        console.error("Error de conexión:", err);
        alert("Error crítico de conexión con el servidor");
    });
}

function imprimirFactura() {
    window.print();
}

//Validacion de sesion empleado
const empleadoId = localStorage.getItem("empleadoId");
const empleadoNombre = localStorage.getItem("empleadoNombre");

if (!empleadoId) {
    window.location.href = "loginempleado.html";
}

//Mostrar nombre empleado
document.getElementById("user-name").textContent = empleadoNombre;


//Menu hamburguesa
const sidebar = document.getElementById("sidebar");
document.getElementById("menu-toggle").addEventListener("click", () => {
    sidebar.classList.toggle("open");
});


//Usuario-Dropdown
const userDropdown = document.getElementById("user-dropdown");
document.getElementById("user-icon").addEventListener("click", () => {
    userDropdown.classList.toggle("show");
});

//lagout

document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("empleadoId");
    localStorage.removeItem("empleadoNombre");
    localStorage.removeItem("empleadoRol");
    window.location.href = "loginempleado.html";
});
//Notificaciones-dropdown

const notifIcon = document.getElementById("notif-icon");
const notifDropdown = document.getElementById("notif-dropdown");

notifIcon.addEventListener("click", () => {
    notifDropdown.classList.toggle("show");
});

//Cargar notificaciones

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


// Navegacion por paginas del sidebar

document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", (e) => {
        e.preventDefault();

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
