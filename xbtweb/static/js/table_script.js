// THIS FILE IS USED TO MANAGE PAGINATION FOR THE PROFILES TABLE

// script.js
document.addEventListener('DOMContentLoaded', () => {
    const profilesTableBody = document.getElementById('profilesTableBody');
    const backButton = document.getElementById('backButton');
    const nextButton = document.getElementById('nextButton');
    const pageInfo = document.getElementById('pageInfo');
    const rows = Array.from(profilesTableBody.getElementsByTagName('tr'));
    const rowsPerPage = 100; // Number of rows to show per page
    let currentPage = 1;
    const totalPages = Math.ceil(rows.length / rowsPerPage);

    function displayTable() {
        const startIndex = (currentPage - 1) * rowsPerPage;
        const endIndex = startIndex + rowsPerPage;

        rows.forEach((row, index) => {
            if (index >= startIndex && index < endIndex) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        });

        pageInfo.textContent = `Page ${currentPage} / ${totalPages}`;
        backButton.disabled = currentPage === 1;
        nextButton.disabled = currentPage === totalPages;
    }

    function nextPage() {
        if (currentPage < totalPages) {
            currentPage++;
            displayTable();
        }
    }

    function backPage() {
        if (currentPage > 1) {
            currentPage--;
            displayTable();
        }
    }

    nextButton.addEventListener('click', nextPage);
    backButton.addEventListener('click', backPage);

    // Initial display
    displayTable();
});
