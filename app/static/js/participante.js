document.addEventListener('DOMContentLoaded', function() {
    
    
   



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


});