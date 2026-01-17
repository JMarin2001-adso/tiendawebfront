
// Vista previa de imagen seleccionada

document.getElementById("imagenes").addEventListener("change", function () {
  const preview = document.getElementById("previewImages");
  preview.innerHTML = "";
  const files = this.files;

  if (files.length === 0) return;

  for (let i = 0; i < files.length; i++) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const img = document.createElement("img");
      img.src = e.target.result;
      img.style.width = "100px";
      img.style.margin = "5px";
      preview.appendChild(img);
    };
    reader.readAsDataURL(files[i]);
  }
});


// Enviar formulario a la base de datos

document.getElementById("productoForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData();
  formData.append("nombre", document.getElementById("nombre").value);
  formData.append("descripcion", document.getElementById("descripcion").value);
  formData.append("precio", document.getElementById("precio").value);

  // id_categoria y nombre de categoría
  const categoriaValor = document.getElementById("categoria").value;
  if (categoriaValor) {
    const [id_categoria, categoria] = categoriaValor.split("|");
    formData.append("id_categoria", id_categoria);
    formData.append("categoria", categoria);
  }


  const imagenInput = document.getElementById("imagenes");
  if (imagenInput.files.length > 0) {
    formData.append("imagen", imagenInput.files[0]);
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/producto/", {
      method: "POST",
      body: formData
    });

    // respuesta del servidor al cargar nuevos productos
    let resultText = await response.text();
    console.log("Respuesta bruta del servidor:", resultText);

    let result;
    try {
      result = JSON.parse(resultText);
    } catch {
      result = { mensaje: "Respuesta no JSON", raw: resultText };
    }

    // Mostrar resultado en la vista previa
    document.getElementById("previewContent").textContent = JSON.stringify(result, null, 2);

    if (response.ok) {
      alert("✅ Producto guardado correctamente");
      document.getElementById("productoForm").reset();
      document.getElementById("previewImages").innerHTML = "";
    } else {
      alert("⚠️ Error al guardar el producto: " + (result.detail || result.error));
    }

  } catch (error) {
    console.error("❌ Error general:", error);
    alert("⚠️ Error en la conexión o en la respuesta del servidor. Revisa la consola.");
  }
});



// Validar sesion de empleado
const empleadoId = localStorage.getItem("empleadoId");
const empleadoNombre = localStorage.getItem("empleadoNombre");

if (!empleadoId) {
    window.location.href = "loginempleado.html";
}

// mostrar nombre
document.getElementById("user-name").textContent = empleadoNombre;


// Menu hamburguesa
const sidebar = document.getElementById("sidebar");
document.getElementById("menu-toggle").addEventListener("click", () => {
    sidebar.classList.toggle("open");
});


// uduario-Dropdown
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

// notificacion
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


// navegacion en el sidebar

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
