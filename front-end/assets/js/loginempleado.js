const API_BASE = "http://127.0.0.1:8000";

document.getElementById('loginForm').addEventListener('submit', async e => {
  e.preventDefault();

  const usuario = document.getElementById('username').value.trim();
  const contrasena = document.getElementById('password').value.trim();

  try {
    const resp = await fetch("http://127.0.0.1:8000/user/login-empleado/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        usuario: usuario,
        contrasena: contrasena
      })
    });

    if (!resp.ok) throw new Error("Usuario o contraseña incorrectos");

    const data = await resp.json();

    console.log("RESPUESTA LOGIN EMPLEADO:", data);

    //Guardar datos del usuario
    localStorage.setItem("empleadoId", data.usuario.id_usuario);
    localStorage.setItem("empleadoNombre", data.usuario.nombre);
    localStorage.setItem("empleadoCorreo", data.usuario.correo);
    localStorage.setItem("empleadoTelefono", data.usuario.telefono);
    localStorage.setItem("empleadoRol", data.usuario.rol);

    window.location.href = "panelempleado.html";

  } catch (err) {
    document.getElementById('error').textContent = err.message;
  }
});
