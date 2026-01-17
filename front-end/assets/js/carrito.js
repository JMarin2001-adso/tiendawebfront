function cargarCarrito() {
  const carrito = JSON.parse(localStorage.getItem("carrito")) || []; 
  const container = document.getElementById("carrito-container");
  const totalElemento = document.getElementById("total");

  container.innerHTML = "";
  let total = 0;

  if (carrito.length === 0) {
    container.innerHTML = "<p>Tu carrito está vacío 🛒</p>";
    totalElemento.textContent = "Total: $0";
    return;
  }

  carrito.forEach((p, index) => {
    const item = document.createElement("div");
    item.classList.add("item-carrito");
    item.innerHTML = `
      <img src="${p.imagen}" alt="${p.nombre}">
      <div class="info">
        <h3>${p.nombre}</h3>
        <p>$${Number(p.precio).toLocaleString('es-CO')}</p>
      </div>
      <div class="controles">
        <button class="btn-cantidad" onclick="cambiarCantidad(${index}, -1)">-</button>
        <span>${p.cantidad}</span>
        <button class="btn-cantidad" onclick="cambiarCantidad(${index}, 1)">+</button>
      </div>
    `;
    container.appendChild(item);
    total += p.precio * p.cantidad;
  });

  totalElemento.textContent = `Total: $${total.toLocaleString('es-CO')}`;
}

function cambiarCantidad(index, cambio) {
  let carrito = JSON.parse(localStorage.getItem("carrito")) || [];
  carrito[index].cantidad += cambio;

  if (carrito[index].cantidad <= 0) carrito.splice(index, 1);

  localStorage.setItem("carrito", JSON.stringify(carrito));
  cargarCarrito();
}

function limpiarCarrito() {
  localStorage.removeItem("carrito");
  cargarCarrito();
  window.dispatchEvent(new Event("carritoActualizado"));
}

function finalizarCompra() {
  const carrito = JSON.parse(localStorage.getItem("carrito")) || [];

  if (carrito.length === 0) {
    Swal.fire("Carrito vacío", "Agrega productos antes de finalizar la compra", "info");
    return;
  }

  window.location.href = "compra.html";
}


document.addEventListener("DOMContentLoaded", cargarCarrito);

// Si el carrito cambia desde otra página, recargarlo automáticamente
window.addEventListener("carritoActualizado", cargarCarrito);
