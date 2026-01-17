const API_BASE = "http://127.0.0.1:8000";

//Validacion de inicio de sesion
const empleadoId = localStorage.getItem("empleadoId");
const empleadoNombre = localStorage.getItem("empleadoNombre");

if (!empleadoId) {
    window.location.href = "loginempleado.html";
}

//mostrar nombre empelado
document.getElementById("user-name").textContent = empleadoNombre;


//manejo de menu hamburguesa
const sidebar = document.getElementById("sidebar");
document.getElementById("menu-toggle").addEventListener("click", () => {
    sidebar.classList.toggle("open");
});


// Usuario-dropdown
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

// Notificaciones-Dropdown
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


// Navegacion entre paginas de sidebar

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

//Cargar producto con mas rotacion

async function cargarGraficaRotacion() {
    try {
        const hoy = new Date().toISOString().split("T")[0];

        const res = await fetch(
            `${API_BASE}/producto/productos-mayor-rotacion?fecha_inicio=${hoy}&fecha_fin=${hoy}`
        );

        const result = await res.json();

        if (!result.success || result.data.length === 0) {
            console.warn("Sin datos de rotación");
            return;
        }

        const labels = result.data.map(p => p.nombre);
        const valores = result.data.map(p => p.total_vendido);

        const ctx = document.getElementById("chart-ventas").getContext("2d");

        new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: "Unidades vendidas",
                    data: valores
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });

    } catch (error) {
        console.error("Error gráfica rotación:", error);
    }
}

//Cargar productos con stock bajo

async function cargarGraficaStockBajo() {
    try {
        const res = await fetch(`${API_BASE}/producto/productos-bajo-stock`);
        const result = await res.json();
        console.log("RESPUESTA STOCK BAJO:", result);

        if (!result.success || result.data.length === 0) {
            console.warn("Sin productos con stock bajo");
            return;
        }

        const labels = result.data.map(p => p.nombre);
        const valores = result.data.map(p => Number(p.stock_actual));

        const ctx = document.getElementById("chart-stock").getContext("2d");

        new Chart(ctx, {
            type: "bar",
            data: {
                labels,
                datasets: [{
                    label: "Stock disponible",
                    data: valores}]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0,
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: { display: false }
                    }
                }
            });

    } catch (error) {
        console.error("Error gráfica stock:", error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cargarGraficaRotacion();
    cargarGraficaStockBajo();
});






