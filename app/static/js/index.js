document.addEventListener('DOMContentLoaded', function() {

    const selectPdf = document.getElementById('tipoPdf');
    

    const toggleThemeBtn = document.getElementById('toggle-theme-btn');
        const body = document.body;

        toggleThemeBtn.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            fetch('/toggle-theme', { method: 'POST' });
        });

    
    selectPdf.addEventListener('change', function() {
        const selectedOption = selectPdf.options[selectPdf.selectedIndex].value;
        
        if (selectedOption === 'general') {
            window.location.href = '/descargarPDFGene';
        } else if (selectedOption === 'lista') {

            

            let table = document.getElementById('tabla-participantes');
            let data = [];
            
            for (let i = 1; i < table.rows.length; i++) {
                let row = table.rows[i];
                let rowData = [];
                for (let j = 0; j < row.cells.length; j++) {
                    rowData.push(row.cells[j].innerText);
                }
                data.push(rowData);
            }
        
            // Convertir a JSON
            let jsonData = JSON.stringify(data);
        
            // Enviar los datos al servidor para generar el PDF
            fetch('/descargarPDFlista', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: jsonData
            })
            .then(response => response.blob())
            .then(blob => {
                // Crear un enlace para descargar el PDF
                const url = window.URL.createObjectURL(new Blob([blob]));
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'participantes.pdf';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => console.error('Error al generar el PDF:', error));

            
        }
    });


    $(document).ready(function() {
        $('#tabla-participantes').DataTable({
            "order": [
                [1, "asc"], // Ordenar por la columna de Fecha de manera ascendente por defecto
                [4, "asc"]  // Ordenar por la columna de Disponibilidad de manera ascendente por defecto
            ],
            "paging": true,       // Habilitar paginación
            "searching": true,    // Habilitar búsqueda
            "columnDefs": [
                { "orderable": true, "targets": [0, 1, 2, 3, 4] }, // Hacer todas las columnas ordenables
                { "searchable": true, "targets": [0, 1, 2, 3, 4] } // Hacer todas las columnas buscables
            ],
            "language": {
                "sProcessing":     "Procesando...",
                "sLengthMenu":     "Mostrar _MENU_ registros",
                "sZeroRecords":    "No se encontraron resultados",
                "sEmptyTable":     "Ningún dato disponible en esta tabla",
                "sInfo":           "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
                "sInfoEmpty":      "Mostrando registros del 0 al 0 de un total de 0 registros",
                "sInfoFiltered":   "(filtrado de un total de _MAX_ registros)",
                "sInfoPostFix":    "",
                "sSearch":         "Buscar:",
                "sUrl":            "",
                "sInfoThousands":  ",",
                "sLoadingRecords": "Cargando...",
                "oPaginate": {
                    "sFirst":    "Primero",
                    "sLast":     "Último",
                    "sNext":     "Siguiente",
                    "sPrevious": "Anterior"
                },
                "oAria": {
                    "sSortAscending":  ": Activar para ordenar la columna de manera ascendente",
                    "sSortDescending": ": Activar para ordenar la columna de manera descendente"
                }
            }
        });
    });


    document.getElementById('form-guardar-registro').onsubmit = function(event) {
        let table = document.getElementById('tabla-participantes');
        let rows = table.getElementsByTagName('tr');
        let data = [];

        for (let i = 1; i < rows.length; i++) {  // start at 1 to skip header row
            let cells = rows[i].getElementsByTagName('td');
            let row_data = {
                turno: cells[0].innerText,
                fecha: cells[1].innerText,
                nombre: cells[2].innerText,
                genero: cells[3].innerText,
                disponibilidad: cells[4].innerText
            };
            data.push(row_data);
        }

        document.getElementById('participantemes-data').value = JSON.stringify(data);
    };

//////////////////////////////////
    // Obtener todos los selectores de letras
    
    var selects = document.querySelectorAll('.letras-select');

    // Iterar sobre cada select
    selects.forEach(function(select) {
        select.addEventListener('change', function() {
            var letraSeleccionada = this.value;
            var letraOriginal = this.dataset.letra;

            // Enviar una solicitud AJAX para validar la selección
            if (letraSeleccionada !== '') {
                validarSeleccion(letraSeleccionada, letraOriginal, function(response) {
                    if (response.success) {
                        // Actualizar el valor de data-letra con la nueva selección
                        select.dataset.letra = letraSeleccionada;
                    } else {
                        
                        smsalerta(response.message);




                        // Revertir la selección al valor original
                        select.value = letraOriginal;
                    }
                });
            }
        });
    });

    function validarSeleccion(letraSeleccionada, letraOriginal, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/seleccionar_letra', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    callback(response);
                } else {
                    console.error('Error al realizar la solicitud.');
                }
            }
        };
        xhr.send('letra=' + encodeURIComponent(letraSeleccionada) + '&original=' + encodeURIComponent(letraOriginal));
    }
 
    

});

function guardarRegistro() {
    document.getElementById('form-guardar-registro').submit();
}

    





