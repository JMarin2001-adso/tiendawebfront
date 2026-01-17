const API_BASE = "http://127.0.0.1:8000";

//Validacion de loguin del cliente
const usuario = {
    id_usuario: localStorage.getItem("userId"),
    nombre: localStorage.getItem("nombreUsuario")
};

if (!usuario.id_usuario) {
    Swal.fire({
        icon: "warning",
        title: "Inicia sesión",
        text: "Debes iniciar sesión para continuar.",
    }).then(() => {
        window.location.href = "index.html";
    });
}

//Resumen de carrito
function cargarResumen() {
    const carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    const lista = document.getElementById("listaResumen");
    const totalHTML = document.getElementById("totalPagar");

    lista.innerHTML = "";
    let total = 0;

    carrito.forEach(p => {
        const li = document.createElement("li");
        li.textContent = `${p.nombre} x${p.cantidad} - $${(p.precio * p.cantidad).toLocaleString("es-CO")}`;
        lista.appendChild(li);
        total += p.precio * p.cantidad;
    });

    totalHTML.textContent = "$" + total.toLocaleString("es-CO");
}

document.addEventListener("DOMContentLoaded", cargarResumen);

//Formulario dinamico
const metodoRadios = document.getElementsByName("metodoPago");
const contenedor = document.getElementById("formularioPago");

metodoRadios.forEach(r => {
    r.addEventListener("change", function () {

        //Limpiar formulario
        contenedor.innerHTML = "";

        //Pago con tarjeta(generico)
        if (this.value === "Tarjeta") {
            contenedor.innerHTML = `
                <div class="formulario-dinamico">
                    <label>Nombre en la tarjeta</label>
                    <input id="nombreTarjeta" type="text">

                    <label>Número de tarjeta</label>
                    <input id="numeroTarjeta" maxlength="19" placeholder="XXXX XXXX XXXX XXXX">

                    <label>Fecha expiración</label>
                    <input id="expTarjeta" maxlength="5" placeholder="MM/AA">

                    <label>CVV</label>
                    <input id="cvvTarjeta" maxlength="3" type="password">
                </div>
            `;

            // Formatear número de tarjeta
            const inputTarjeta = document.getElementById("numeroTarjeta");
            inputTarjeta.addEventListener("input", function () {
                let value = this.value.replace(/\D/g, "");
                value = value.slice(0, 16);
                this.value = value.replace(/(.{4})/g, "$1 ").trim();
            });

        
            document.getElementById("expTarjeta").addEventListener("input", function () {
                let v = this.value.replace(/\D/g, "");
                
                if (v.length >= 3) {
                    v = v.slice(0, 4);       
                    this.value = v.slice(0, 2) + "/" + v.slice(2);
                } else {
                    this.value = v;
                }
            });

        }

        //pago por nequi(generico)
        if (this.value === "Nequi") {
            contenedor.innerHTML = `
                <div class="formulario-dinamico">
                    <label>Número Nequi</label>
                    <input id="nequiNumero" maxlength="10" placeholder="Ej: 3001234567">

                    <label>Contraseña (4 dígitos)</label>
                    <input id="nequiPass" type="password" maxlength="4" placeholder="****">
                </div>
            `;

            document.getElementById("nequiNumero").addEventListener("input", function () {
                this.value = this.value.replace(/\D/g, "").slice(0, 10);
            });

            document.getElementById("nequiPass").addEventListener("input", function () {
                this.value = this.value.replace(/\D/g, "").slice(0, 4);
            });
        }
    });
});

//confirmacion de pago
document.getElementById("btnPagar").addEventListener("click", async () => {

    const carrito = JSON.parse(localStorage.getItem("carrito")) || [];
    if (carrito.length === 0) {
        Swal.fire("Carrito vacío", "No hay productos para pagar.", "error");
        return;
    }

    const metodo = Array.from(metodoRadios).find(r => r.checked);
    if (!metodo) {
        Swal.fire("Método de pago", "Debes elegir un método de pago.", "warning");
        return;
    }

    //validaciones de datos de tarjeta-nequi(generico)
    if (metodo.value === "Tarjeta") {
        const numero = document.getElementById("numeroTarjeta").value.replace(/\s/g, "");
        const nombre = document.getElementById("nombreTarjeta").value.trim();
        const exp = document.getElementById("expTarjeta").value.trim();
        const cvv = document.getElementById("cvvTarjeta").value.trim();

        if (!nombre || !exp || !cvv || numero.length !== 16) {
            Swal.fire("Error", "Completa correctamente los datos de la tarjeta.", "error");
            return;
        }
    }

    if (metodo.value === "Nequi") {
        const numero = document.getElementById("nequiNumero").value;
        const pass = document.getElementById("nequiPass").value;

        if (numero.length !== 10 || pass.length !== 4) {
            Swal.fire("Error", "Datos de Nequi incorrectos.", "error");
            return;
        }
    }

    //confimacion de pedido realizado
    const pedido = {
        id_usuario: usuario.id_usuario,
        productos: carrito.map(p => ({
            id_producto: p.id,
            cantidad: p.cantidad,
            precio_unitario: p.precio
        }))
    };

    Swal.fire({
        title: "Procesando pago...",
        text: "Espera un momento",
        allowOutsideClick: false,
        didOpen: () => Swal.showLoading()
    });

    try {
        const res = await fetch(`${API_BASE}/pedido/nuevo`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(pedido),
        });

        const data = await res.json();

        if (!res.ok || data.status === "error") {
            Swal.fire("Error", "No se pudo crear el pedido.", "error");
            return;
        }

        Swal.fire({
            icon: "success",
            title: "Pago exitoso ",
            text: "Tu pedido fue enviado a revisión.",
        }).then(() => {
            localStorage.removeItem("carrito");
            window.location.href = "index.html";
        });

    } catch (err) {
        Swal.fire("Error", "Ocurrió un problema inesperado.", "error");
        console.error(err);
    }
});
