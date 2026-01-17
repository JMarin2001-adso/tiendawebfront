const API_BASE = "http://127.0.0.1:8000";
const params = new URLSearchParams(window.location.search);
const id_pedido = params.get("id");

async function cargarFactura() {
    try {
        //Obtener los detalles del pedido
        const res = await fetch(`${API_BASE}/pedido/detalle/${id_pedido}`);
        const data = await res.json();

        //Renderiza los datos
        document.getElementById("factura-pedido").textContent = data.id_pedido;
        document.getElementById("factura-fecha").textContent =
            new Date(data.fecha).toLocaleDateString();

        document.getElementById("cliente").textContent =
            `Nombre: ${data.nombre_cliente}`;
        document.getElementById("direccion").textContent =
            `Dirección: ${data.direccion}`;
        document.getElementById("correo").textContent =
            `Correo: ${data.correo}`;

        const tbody = document.getElementById("factura-productos");
        tbody.innerHTML = ""; //Limpiar tabla
        let totalAcumulado = 0;

        data.productos.forEach(p => {
            const subtotal = p.cantidad * p.precio_unitario;
            totalAcumulado += subtotal;

            tbody.innerHTML += `
                <tr>
                    <td>${p.nombre_producto}</td>
                    <td>${p.cantidad}</td>
                    <td>$${p.precio_unitario.toLocaleString()}</td>
                    <td>$${subtotal.toLocaleString()}</td>
                </tr>
            `;
        });

        document.getElementById("factura-total").textContent =
            totalAcumulado.toLocaleString();

        //ayuda a guardar la factura en la base de datos
        if (id_pedido) {
            await guardarFacturaEnBaseDeDatos(id_pedido, totalAcumulado);
        }

    } catch (error) {
        console.error("Error al cargar la factura:", error);
    }
}

async function guardarFacturaEnBaseDeDatos(id, total) {
    try {
        console.log("Intentando registrar factura electrónica...");
        
        const response = await fetch(`${API_BASE}/factura/online`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id_pedido: parseInt(id),
                total: parseFloat(total)
            })
        });

        const resultado = await response.json();

        if (resultado.success) {
            console.log("Factura guardada correctamente:", resultado.numero_factura);
            // alerta de factura emitita
        } else {
            console.error("Error del servidor al guardar:", resultado.message);
        }
    } catch (error) {
        console.error("Error de red al intentar guardar la factura:", error);
    }
}

//se ejecuta la factura.
cargarFactura();
