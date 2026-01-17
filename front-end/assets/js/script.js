const API_BASE = "http://127.0.0.1:8000";

//funciones de modales
window.openRegisterModal = () => document.getElementById("modal").style.display = "block";
window.closeModal = () => document.getElementById("modal").style.display = "none";
window.openLoginModal = () => document.getElementById("loginModal").style.display = "block";
window.closeLoginModal = () => document.getElementById("loginModal").style.display = "none";

//categorias
window.toggleCategorias = () => {
    const cat = document.querySelector('.categoria');
    cat.style.display = cat.style.display === 'block' ? 'none' : 'block';
};

// cargue de eventos principales
document.addEventListener("DOMContentLoaded", () => {
    cargarProductos();
    mostrarUsuario();
    actualizarContadorCarrito();
    cargarNotificaciones();

    // Manejo del Dropdown de Notificaciones
    const btnNotif = document.getElementById("btn-notificaciones");
    const dropNotif = document.getElementById("notif-dropdown");

    if (btnNotif && dropNotif) {
        btnNotif.addEventListener("click", (e) => {
            e.stopPropagation();
            dropNotif.classList.toggle("show");
        });
    }

    // Manejo del Formulario de Registro
    const clienteForm = document.getElementById("clienteForm");
    if (clienteForm) {
        clienteForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            await createUser();
        });
    }

    // Manejo del Formulario de Login
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            await loginUser();
        });
    }

    //Cierre de menús al hacer clic fuera
    document.addEventListener("click", (e) => {
        if (dropNotif && !btnNotif.contains(e.target)) dropNotif.classList.remove("show");
        
        const catMenu = document.querySelector('.categoria');
        if (catMenu && catMenu.style.display === 'block' && !catMenu.contains(e.target)) {
            catMenu.style.display = 'none';
        }
    });
});

// creacion de clinete(registro)
async function createUser() {
    const user = {
        nombre: document.getElementById("nombre").value,
        correo: document.getElementById("correo").value,
        telefono: document.getElementById("telefono").value,
        contrasena: document.getElementById("contrasena").value
    };

    try {
        const res = await fetch(`${API_BASE}/user/clientes/registrar/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(user)
        });

        if (res.ok) {
            await Swal.fire({
                title: "¡Registro Exitoso!",
                text: "Tu cuenta ha sido creada correctamente. Ahora puedes iniciar sesión.",
                icon: "success",
                confirmButtonColor: "rgb(47, 235, 119)"
            });
            closeModal();
            // Limpiar formulario opcionalmente
            document.getElementById("clienteForm").reset();
        } else {
            const err = await res.json();
            Swal.fire("Error", err.detail || "No se pudo crear el registro", "error");
        }
    } catch (error) {
        console.error(error);
        Swal.fire("Error", "Error de conexión con el servidor", "error");
    }
}

//Loguin inicio de sesion
async function loginUser() {
    const correo = document.getElementById("correoLogin").value;
    const contrasena = document.getElementById("contrasenaLogin").value;

    try {
        const res = await fetch(`${API_BASE}/user/login/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ correo, contrasena })
        });

        if (res.ok) {
            const data = await res.json();
            
           
            localStorage.setItem("userId", data.usuario.id_usuario);
            localStorage.setItem("nombreUsuario", data.usuario.nombre);

           
            await Swal.fire({
                title: "¡Bienvenido de nuevo!",
                text: `Hola ${data.usuario.nombre}, has iniciado sesión correctamente.`,
                icon: "success",
                confirmButtonText: "Entrar",
                confirmButtonColor: "rgb(47, 235, 119)"
            });

            
            window.location.reload(); 
            
        } else {
            Swal.fire("Error", "Correo o contraseña incorrectos", "error");
        }
    } catch (error) {
        console.error(error);
        Swal.fire("Error", "Error al conectar con la base de datos", "error");
    }
}

//se cargan los producto dentro en el carrito
async function cargarProductos() {
    try {
        const res = await fetch(`${API_BASE}/producto/`);
        const response = await res.json();
        let productos = response.data || [];
        const container = document.getElementById("productos-container");
        if (!container) return;
        container.innerHTML = "";

        productos.forEach(p => {
            const card = document.createElement("div");
            card.classList.add("card");
            const img = p.imagen || "assets/img/default.jpg";
            card.innerHTML = `
                <img src="${img}" alt="${p.nombre}">
                <h3>${p.nombre}</h3>
                <p class="precio">$${Number(p.precio).toLocaleString('es-CO')}</p>
                <button class="btn-comprar" onclick="agregarAlCarrito(${p.id_producto}, '${p.nombre}', ${p.precio}, '${img}')">
                    🛒 Añadir al carrito
                </button>`;
            container.appendChild(card);
        });
    } catch (e) { console.error("Error productos:", e); }
}

window.agregarAlCarrito = (id, nombre, precio, imagen) => {
    let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    const existe = carrito.find(item => item.id === id);

    if (existe) {
        existe.cantidad += 1;
    } else {
        carrito.push({ id, nombre, precio, imagen, cantidad: 1 });
    }

    localStorage.setItem("carrito", JSON.stringify(carrito));
    actualizarContadorCarrito();

    
    Swal.fire({
        title: "¡Agregado!",
        text: `${nombre} ya está en tu carrito`,
        icon: "success",
        timer: 1500,
        showConfirmButton: false,
        toast: true,
        position: 'top-end'
    });
};

function actualizarContadorCarrito() {
    const carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    const total = carrito.reduce((sum, p) => sum + p.cantidad, 0);
    const cont = document.getElementById("contador-carrito");
    if (cont) cont.textContent = total;
}

// Interfaz de usuario
function mostrarUsuario() {
    const nombre = localStorage.getItem("nombreUsuario");
    const navLeft = document.getElementById("nav-left");
    if (!navLeft) return;

    if (nombre) {
        navLeft.innerHTML = `
            <div class="user-menu" id="userMenu">
                <span onclick="document.getElementById('userDropdown').classList.toggle('show')">
                    <i class="fa-solid fa-user"></i> ${nombre} <i class="fa-solid fa-caret-down"></i>
                </span>
                <div class="user-dropdown" id="userDropdown">
                    <a href="perfil.html">Mi perfil</a>
                    <a href="#" onclick="cerrarSesion()">Cerrar sesión</a>
                </div>
            </div>`;
    } else {
        navLeft.innerHTML = `
            <span onclick="openRegisterModal()">Registrarse</span>
            <span onclick="openLoginModal()">Iniciar Sesión</span>`;
    }
}

window.cerrarSesion = () => {
    localStorage.clear();
    location.reload();
};

async function cargarNotificaciones() {
    const id = localStorage.getItem("userId");
    if (!id) return;
    try {
        const res = await fetch(`${API_BASE}/envio/notificaciones/${id}`);
        const data = await res.json();
        const cont = document.getElementById("notificacion-mensaje");
        if (cont) {
            const n = data.filter(x => x.leida === 0).length;
            cont.textContent = n;
            cont.style.display = n > 0 ? "block" : "none";
        }
    } catch (e) { console.error(e); }
}












