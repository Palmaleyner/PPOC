function alerteliminar(Id){
    Swal.fire({
        title: "Eliminar registro",
        text: "¡Seguro que desea eliminar el registro!",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "#3085d6",
        cancelButtonColor: "#d33",
        confirmButtonText: "Eliminar"
      }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('eliminarGestor' + Id).submit();          
        }
      });
}

function alertsalir(){
    Swal.fire({
        title: "Cerrar sesión",
        text: "¿Está seguro que desea salir?",
        icon: "question"
      }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = '/exit';
        }
      });
}

function alertsalirparticipante(){
  Swal.fire({
      title: "Cerrar sesión",
      text: "¿Está seguro que desea salir?",
      icon: "question"
    }).then((result) => {
      if (result.isConfirmed) {
          window.location.href = '/exitparticipante';
      }
    });
}


function confirmarEliminarTodo() {
  Swal.fire({
      title: "Eliminar todos los registros",
      text: "¿Seguro que desea eliminar todos los registros?",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Eliminar"
  }).then((result) => {
      if (result.isConfirmed) {
          document.getElementById('form-eliminar-todo').submit();
      }
  });
}

function smsalerta(message) {
  Swal.fire({
    icon: "info",
    title: 'Acción Denegada',
    text: message
  });
}

