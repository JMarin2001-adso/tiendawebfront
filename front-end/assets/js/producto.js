// Configuracion
const API_URL = "http://127.0.0.1:8000/producto";
const STORAGE_KEY = "erp_product_edits_v1";

let productosGlobal = [];
let currentEditId = null;

/**
 * 1. CARGA INICIAL
 */
async function reloadPanel() {
    try {
        const res = await fetch(`${API_URL}/`);
        const data = await res.json();
        productosGlobal = data.data || data || [];
        renderizarLista();
    } catch (e) {
        console.error("Error cargando productos:", e);
        Swal.fire('Error', 'No se pudo conectar con el servidor', 'error');
    }
}

//Previsualización de productos 

function renderizarLista() {
    const container = document.getElementById("productos-container");
    container.innerHTML = "";
    
    const overrides = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");

    productosGlobal.forEach(p => {
        const id = String(p.id_producto);
        const ov = overrides[id] || {};
        
        const nombre = ov.nombre || p.nombre;
        const precio = ov.precio || p.precio;
        const imagen = (ov.images && ov.images[0]) || p.imagen || "assets/img/default.jpg";

        const card = document.createElement("div");
        card.className = "card-employee";
        card.innerHTML = `
            <img src="${imagen}" alt="${nombre}">
            <h4>${nombre}</h4>
            <p class="precio">$ ${Number(precio).toLocaleString("es-CO")}</p>
            <div class="card-actions">
                <button class="btn-edit" onclick="openModal('${id}')">Editar</button>
            </div>
        `;
        container.appendChild(card);
    });
}

//control de modal
window.openModal = function(id) {
    const p = productosGlobal.find(x => String(x.id_producto) === String(id));
    if (!p) return;

    currentEditId = id;
    const overrides = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}")[id] || {};

    document.getElementById("edit-title").textContent = `Editando: ${p.nombre}`;
    document.getElementById("edit-nombre").value = overrides.nombre || p.nombre;
    document.getElementById("edit-precio").value = overrides.precio || p.precio;

    document.getElementById("editModal").style.display = "flex";
};

window.closeModal = function() {
    document.getElementById("editModal").style.display = "none";
    currentEditId = null;
};

window.guardarProductoGlobal = async function() {
    if (!currentEditId) return;

    // Obtener precios de los productos
    const nuevoNombre = document.getElementById("edit-nombre").value;
    const nuevoPrecio = parseFloat(document.getElementById("edit-precio").value);

    if (!nuevoNombre || isNaN(nuevoPrecio)) {
        Swal.fire('Atención', 'Nombre y precio son obligatorios', 'warning');
        return;
    }

    // Mostrar estado de carga
    Swal.fire({
        title: 'Guardando...',
        text: 'Actualizando',
        allowOutsideClick: false,
        didOpen: () => { Swal.showLoading(); }
    });

    //se mandan los datos al backend
    const payload = {
        id_producto: parseInt(currentEditId),
        nombre: nuevoNombre,
        precio: nuevoPrecio
    };

    try {
        const res = await fetch(`${API_URL}/actualizar-precio`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok && data.success) {
            
            const overrides = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
            delete overrides[currentEditId];
            localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides));

        
            await Swal.fire({
                icon: 'success',
                title: '¡Actualizado!',
                text: 'El producto se guardó correctamente en la base de datos.',
                timer: 2000,
                showConfirmButton: false
            });

            
            closeModal();
            await reloadPanel(); 
        } else {
            throw new Error(data.message || "Error al actualizar");
        }

    } catch (err) {
        console.error("Error:", err);
        Swal.fire('Error de Sincronización', 'No se pudo guardar en MySQL. Verifica tu conexión.', 'error');
    }
};

// Inicializar al cargar la página
document.addEventListener("DOMContentLoaded", reloadPanel);

//Validar sesion de empleado
const empleadoId = localStorage.getItem("empleadoId");
const empleadoNombre = localStorage.getItem("empleadoNombre");

if (!empleadoId) {
    window.location.href = "loginempleado.html";
}

//mostrar nombre 
document.getElementById("user-name").textContent = empleadoNombre;


//manejo de menu hamburgues 
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

// notificacion-Dropdown 
const notifIcon = document.getElementById("notif-icon");
const notifDropdown = document.getElementById("notif-dropdown");

notifIcon.addEventListener("click", () => {
    notifDropdown.classList.toggle("show");
});

// Cargar notificaciones

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


// navegacion entre paginas del sidebar

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
