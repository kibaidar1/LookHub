const PAGE_SIZE = 25;
let currentPage = 1;
let totalPages = 1;
let currentOrderBy = null;
let currentDescOrder = true;

function updateSortButtons() {
    document.querySelectorAll('.sort-btn').forEach(btn => {
        const field = btn.dataset.field;
        const isActive = field === currentOrderBy;

        // Сбрасываем стиль всех кнопок
        btn.style.backgroundColor = '';
        btn.style.color = '';

        if (isActive) {
            // Подсвечиваем активную кнопку
            btn.style.backgroundColor = '#4CAF50';
            btn.style.color = 'white';
            // Обновляем стрелку направления в соответствии с текущей сортировкой
            btn.textContent = `${btn.textContent.split(' ')[0]} ${currentDescOrder ? '↓' : '↑'}`;
            btn.dataset.direction = currentDescOrder ? 'desc' : 'asc';
        } else {
            // Сбрасываем кнопку в исходное состояние
            btn.textContent = `${btn.textContent.split(' ')[0]} ↓`;
            btn.dataset.direction = 'desc';
        }
    });
}

async function loadLooks(page = 1, orderBy = null, descOrder = true, append = false) {
    try {
        let url = `/api/looks/?page=${page}&page_size=${PAGE_SIZE}`;
        if (orderBy) {
            url += `&order_by=${orderBy}&desc_order=${descOrder}`;
        }
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();

        const looks = data.results;
        const totalCount = data.count;
        totalPages = Math.ceil(totalCount / PAGE_SIZE);
        currentPage = page;
        currentOrderBy = orderBy;
        currentDescOrder = descOrder;

        updateSortButtons();

        const looksList = document.getElementById('looks-list');
        if (!append) looksList.innerHTML = ''; // Очищаем, если не подгрузка
        if (looks.length === 0 && !append) {
            looksList.innerHTML = '<p>Список луков пуст</p>';
        } else {
            looks.forEach(look => {
                const lookItem = document.createElement('div');
                lookItem.className = 'look-item';
                lookItem.innerHTML = `
                    <h3><a href="/admin/looks/${look.id}">${look.name || 'Без названия'}</a></h3>
                    <p><strong>ID:</strong> ${look.id}</p>
                    <p><strong>Пол:</strong> ${look.gender || 'N/A'}</p>
                    <p><strong>Проверено:</strong> ${look.checked ? 'Да' : 'Нет'}</p>
                    <p><strong>Опубликовано:</strong> ${look.pushed ? 'Да' : 'Нет'}</p>
                    <button class="delete-btn" data-id="${look.id}">Удалить</button>
                    <hr>
                `;
                looksList.appendChild(lookItem);
            });
        }

        updatePaginationControls();
        if (!append) window.scrollTo({ top: 0, behavior: 'smooth' }); // Прокрутка вверх только при полной загрузке
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('looks-list').innerHTML = `<p>Ошибка: ${error.message}</p>`;
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

async function createLookWithAI() {
    const description = document.getElementById('ai-description').value.trim();
    const gender = document.getElementById('ai-gender').value;
    if (!description) {
        alert('Введите описание для генерации лука');
        return;
    }

    try {
        const response = await fetch('/api/looks/ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                look_description: description,
                genders: [gender] // Передаем gender как список
            })
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const newLook = await response.json();
        document.getElementById('ai-description').value = '';
        await loadLooks(1, currentOrderBy, currentDescOrder); // Сбрасываем на первую страницу
        alert(`Лук "${newLook.name || 'Без названия'}" успешно создан!`);
    } catch (error) {
        console.error('Error creating look with AI:', error);
        alert('Ошибка при создании лука: ' + error.message);
    }
}

async function deleteLook(lookId) {
    if (!confirm('Вы уверены, что хотите удалить этот лук?')) return;

    try {
        const response = await fetch(`/api/looks/${lookId}`, {
            method: 'DELETE',
            headers: { 'Accept': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        await loadLooks(currentPage, currentOrderBy, currentDescOrder);
    } catch (error) {
        console.error('Error deleting look:', error);
        alert('Ошибка при удалении: ' + error.message);
    }
}

document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const field = btn.dataset.field;

        if (field === currentOrderBy) {
            // Если нажали на активную кнопку, меняем направление
            currentDescOrder = !currentDescOrder;
            loadLooks(1, field, currentDescOrder);
        } else {
            // Если нажали на новую кнопку, сбрасываем все остальные и устанавливаем сортировку по убыванию
            currentOrderBy = field;
            currentDescOrder = true;
            loadLooks(1, field, true);
        }
    });
});

document.getElementById('create-ai-look-btn').addEventListener('click', createLookWithAI);
document.getElementById('prev-page-btn').addEventListener('click', () => {
    if (currentPage > 1) loadLooks(currentPage - 1, currentOrderBy, currentDescOrder);
});
document.getElementById('next-page-btn').addEventListener('click', () => {
    if (currentPage < totalPages) loadLooks(currentPage + 1, currentOrderBy, currentDescOrder);
});
document.getElementById('load-more-btn').addEventListener('click', () => {
    if (currentPage < totalPages) loadLooks(currentPage + 1, currentOrderBy, currentDescOrder, true);
});
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('delete-btn')) {
        const lookId = e.target.getAttribute('data-id');
        deleteLook(lookId);
    }
});

loadLooks();