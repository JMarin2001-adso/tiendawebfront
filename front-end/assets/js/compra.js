const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  cargarResumen();
  cargarPedido();
  autocompletarCliente();
});

// 🧾 Autocompletar datos del cliente
function autocompletarCliente() {
  const nombre = localStorage.getItem("nombreUsuario") || "";
  const correo = localStorage.getItem("correoUsuario") || "";
  const telefono = localStorage.getItem("telefonoUsuario") || "";
  const direccion = localStorage.getItem("direccionUsuario") || "";
  const ciudad = localStorage.getItem("ciudadUsuario") || "";
  const postal = localStorage.getItem("postalUsuario") || "";

  if (nombre) document.getElementById("nombre").value = nombre;
  if (correo) document.getElementById("correo").value = correo;
  if (telefono) document.getElementById("telefono").value = telefono;
  if (direccion) document.getElementById("direccion").value = direccion;
  if (ciudad) document.getElementById("ciudad").value = ciudad;
  if (postal) document.getElementById("postal").value = postal;
}

// Mostrar resumen del carrito
function cargarResumen() {
  const carrito = JSON.parse(localStorage.getItem("carrito")) || [];
  const lista = document.getElementById("lista-pedido");
  const totalElem = document.getElementById("total-pedido");

  lista.innerHTML = "";
  let total = 0;

  if (carrito.length === 0) {
    lista.innerHTML = "<p>No hay productos en el carrito.</p>";
    document.querySelector(".btn-finalizar").disabled = true;
    return;
  }

  carrito.forEach(p => {
    const subtotal = p.precio * p.cantidad;
    total += subtotal;
    const item = document.createElement("div");
    item.classList.add("producto-item");
    item.innerHTML = `
      <span>${p.nombre} x${p.cantidad}</span>
      <span>$${subtotal.toLocaleString("es-CO")}</span>
    `;
    lista.appendChild(item);
  });

  totalElem.textContent = `$${total.toLocaleString("es-CO")}`;
}

// Guardar datos y redirigir al pago
document.getElementById("checkoutForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const idUsuario = localStorage.getItem("userId");
  if (!idUsuario) {
    Swal.fire("Error", "No se encontró el ID del usuario en el sistema.", "error");
    return;
  }

  // Capturar datos
  const nombre = document.getElementById("nombre").value.trim();
  const correo = document.getElementById("correo").value.trim();
  const telefono = document.getElementById("telefono").value.trim();
  const direccion = document.getElementById("direccion").value.trim();
  const ciudad = document.getElementById("ciudad").value.trim();
  const postal = document.getElementById("postal").value.trim();

  // Validar campos
  if (!nombre || !correo || !telefono || !direccion || !ciudad || !postal) {
    Swal.fire({
      icon: "error",
      title: "Campos incompletos",
      text: "Por favor, completa todos los datos antes de continuar.",
    });
    return;
  }

  // Guardar datos en el backend
  const user = { direccion, ciudad, postal };

  try {
    const res = await fetch(`${API_BASE}/user/usuario/${idUsuario}/direccion`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(user),
    });

    const data = await res.json();
    if (!res.ok) {
      Swal.fire("Error", data.message || "No se pudo actualizar la dirección.", "error");
      return;
    }

    console.log("Dirección guardada:", data);
  } catch (err) {
    console.error("Error al actualizar dirección:", err);
    Swal.fire("Error", "No se pudo conectar con el servidor", "error");
    return;
  }

  //Redirigir al pago unificado
  Swal.fire({
    icon: "info",
    title: "Continuar al pago",
    text: "Usted sera direccionado a la plataforma de pagos.",
    confirmButtonText: "Ir al pago",
  }).then(() => {
    window.location.href = "pagopasarela.html";
  });
});

// Cargar productos visualmente
function cargarPedido() {
  const carrito = JSON.parse(localStorage.getItem("carrito")) || [];
  const contenedor = document.getElementById("lista-pedido");
  const totalPedido = document.getElementById("total-pedido");

  contenedor.innerHTML = "";
  let total = 0;

  carrito.forEach(item => {
    const linea = document.createElement("div");
    linea.classList.add("producto-item");
    linea.innerHTML = `
      <span>${item.nombre} (x${item.cantidad})</span>
      <span>$${(item.precio * item.cantidad).toLocaleString('es-CO')}</span>
    `;
    contenedor.appendChild(linea);
    total += item.precio * item.cantidad;
  });

  totalPedido.textContent = `$${total.toLocaleString('es-CO')}`;
}
