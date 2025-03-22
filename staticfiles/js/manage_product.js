function searchProducts() {
    const input = document.getElementById('searchInput').value.toLowerCase();
    const table = document.getElementById('productTable');
    const rows = table.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let match = false;

        for (let j = 0; j < cells.length; j++) {
            if (cells[j].textContent.toLowerCase().indexOf(input) > -1) {
                match = true;
                break;
            }
        }

        rows[i].style.display = match ? '' : 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    searchProducts(); 
});
