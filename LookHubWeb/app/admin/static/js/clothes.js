 const PAGE_SIZE = 25;
let currentPage = 1;
let totalPages = 1;

async function loadClothes(page = 1, append = false) {
    try {
        const url = `/api/clothes/?page=${page}&page_size=${PAGE_SIZE}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();

        const clothes = data.results;
        const totalCount = data.count;
        totalPages = Math.ceil(totalCount / PAGE_SIZE);
        currentPage = page;

        const tbody = document.getElementById('clothes-tbody');
        if (!append) tbody.innerHTML = ''; // Очищаем, если не подгрузка
        if (clothes.length === 0 && !append) {
            tbody.innerHTML = '<tr><td colspan="5">Список одежды пуст</td></tr>';
        } else {
            clothes.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${item.id}</td>
                    <td><a href="/admin/clothes/${item.id}">${item.name || 'Без названия'}</a></td>
                    <td>${item.gender || 'N/A'}</td>
                    <td>${item.image_url ? `<img src="${item.image_url}" alt="${item.name || 'N/A'}" style="max-width: 100px;">` : 'N/A'}</td>
                    <td><button class="delete-btn" data-id="${item.id}">Удалить</button></td>
                `;
                tbody.appendChild(tr);
            });
        }

        updatePaginationControls();
        if (!append) window.scrollTo({ top: 0, behavior: 'smooth' }); // Прокрутка вверх только при полной загрузке
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('clothes-tbody').innerHTML = `<tr><td colspan="5">Ошибка: ${error.message}</td></tr>`;
    }
}

function updatePaginationControls() {
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');
    const loadMoreBtn = document.getElementById('load-more-btn');
    const pageInfo = document.getElementById('page-info');

    pageInfo.textContent = `Страница ${currentPage} из ${totalPages}`;
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
    loadMoreBtn.disabled = currentPage === totalPages || totalPages === 0;
}

async function createClothesWithAI() {
    const link = document.getElementById('ai-link').value.trim();
    if (!link) {
        alert('Введите ссылку на одежду');
        return;
    }

    try {
        const response = await fetch('/api/clothes/ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ link })
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const newClothes = await response.json();
        document.getElementById('ai-link').value = '';
        await loadClothes(1); // Сбрасываем на первую страницу
        alert(`Одежда "${newClothes.name || 'Без названия'}" успешно добавлена!`);
    } catch (error) {
        console.error('Error creating clothes with AI:', error);
        alert('Ошибка при добавлении одежды: ' + error.message);
    }
}

async function deleteClothes(clothesId) {
    if (!confirm('Вы уверены, что хотите удалить эту одежду?')) return;

    try {
        const response = await fetch(`/clothes/${clothesId}`, {
            method: 'DELETE',
            headers: { 'Accept': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        await loadClothes(currentPage);
    } catch (error) {
        console.error('Error deleting clothes:', error);
        alert('Ошибка при удалении: ' + error.message);
    }
}

document.getElementById('create-ai-clothes-btn').addEventListener('click', createClothesWithAI);
document.getElementById('prev-page-btn').addEventListener('click', () => {
    if (currentPage > 1) loadClothes(currentPage - 1);
});
document.getElementById('next-page-btn').addEventListener('click', () => {
    if (currentPage < totalPages) loadClothes(currentPage + 1);
});
document.getElementById('load-more-btn').addEventListener('click', () => {
    if (currentPage < totalPages) loadClothes(currentPage + 1, true);
});
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('delete-btn')) {
        const clothesId = e.target.getAttribute('data-id');
        deleteClothes(clothesId);
    }
});

loadClothes();