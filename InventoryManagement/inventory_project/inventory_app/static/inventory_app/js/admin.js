document.addEventListener('DOMContentLoaded', () => {
    // Toggle forms visibility
    const formToggle = document.getElementById('formToggle');
    const updateForm = document.getElementById('updateForm');
    const addForm = document.getElementById('addForm');
    
    formToggle.addEventListener('change', () => {
        if (formToggle.checked) {
            updateForm.style.display = 'none';
            addForm.style.display = 'block';
        } else {
            updateForm.style.display = 'block';
            addForm.style.display = 'none';
        }
    });

    // Download report button
    const downloadReportBtn = document.getElementById('downloadReportBtn');
    downloadReportBtn.addEventListener('click', () => {
        window.open(window.urls.downloadStockReportUrl, '_blank').focus();
    });


    // Stock table search functionality
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function () {
        console.log("Search value:", this.value);
        const filter = this.value.toUpperCase();
        const table = document.getElementById('stock_table');
        const tr = table.getElementsByTagName('tr');

        for (let i = 0; i < tr.length; i++) {
        let td = tr[i].getElementsByTagName('td')[1]; // Assumes the 'Item' column is the second one
        if (td) {
            const txtValue = td.textContent || td.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
            tr[i].style.display = '';
            } else {
            tr[i].style.display = 'none';
            }
        }
        }
  });


});




function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
