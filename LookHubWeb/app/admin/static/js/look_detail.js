const lookId = window.location.pathname.split('/').pop();
let isEditing = false;
let originalData = {};
const baseUrl = window.location.origin;
let deletedCategories = new Set();
let deletedClothes = new Set();

async function loadLookDetails() {
    try {
        const response = await fetch(`/api/looks/${lookId}`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const look = await response.json();
        originalData = { ...look };
        deletedCategories.clear();
        deletedClothes.clear();

        document.getElementById('look-id').textContent = look.id || 'N/A';
        document.getElementById('look-name').textContent = look.name || 'N/A';
        document.getElementById('edit-look-name').value = look.name || '';
        document.getElementById('look-gender').textContent = look.gender || 'N/A';
        document.getElementById('edit-look-gender').value = look.gender || 'унисекс';
        document.getElementById('look-description').textContent = look.description || 'N/A';
        document.getElementById('edit-look-description').value = look.description || '';

        const promptsContainer = document.getElementById('look-image-prompts');
        promptsContainer.innerHTML = '';
        const editPromptsContainer = document.getElementById('edit-look-image-prompts');
        editPromptsContainer.innerHTML = '';
        if (look.image_prompts?.length) {
            look.image_prompts.forEach(prompt => {
                promptsContainer.insertAdjacentHTML('beforeend', `<p>${prompt}</p>`);
                editPromptsContainer.insertAdjacentHTML('beforeend', `
                    <div class="prompt-item">
                        <input type="text" value="${prompt}" class="prompt-input">
                        <button class="remove-prompt-btn">Удалить</button>
                    </div>
                `);
            });
        } else {
            promptsContainer.textContent = 'N/A';
        }

        const imageContainer = document.getElementById('look-image-urls');
        imageContainer.innerHTML = '';
        const editImageContainer = document.getElementById('edit-look-image-urls');
        editImageContainer.innerHTML = '';
        if (look.image_urls?.length) {
            look.image_urls.forEach(url => {
                const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
                imageContainer.insertAdjacentHTML('beforeend', `<img src="${fullUrl}" alt="Image">`);
                editImageContainer.insertAdjacentHTML('beforeend', `
                    <div class="image-item">
                        <img src="${fullUrl}" alt="Image" data-original="${url}">
                        <button class="remove-image-btn" data-url="${url}">Удалить</button>
                    </div>
                `);
            });
        } else {
            imageContainer.textContent = 'Нет изображений';
        }

        document.getElementById('look-checked').textContent = look.checked ? 'Да' : 'Нет';
        document.getElementById('edit-look-checked').value = look.checked ? 'true' : 'false';
        document.getElementById('check-look-btn').style.display = look.checked ? 'none' : 'inline-block';
        document.getElementById('look-pushed').textContent = look.pushed ? 'Да' : 'Нет';
        document.getElementById('edit-look-pushed').value = look.pushed ? 'true' : 'false';

        const categoriesContainer = document.getElementById('look-clothes-categories');
        categoriesContainer.innerHTML = '';
        if (look.clothes_categories?.length) {
            look.clothes_categories.forEach(category => {
                const categoryItem = document.createElement('div');
                categoryItem.className = 'category-item';
                categoryItem.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>${category.name || 'N/A'}</h3>
                        <button class="delete-category-btn edit-field" data-category-id="${category.id}" style="display: none;">Удалить категорию</button>
                    </div>
                `;
                const clothesList = document.createElement('div');
                if (category.clothes?.length) {
                    category.clothes.forEach(cloth => {
                        const clothImageUrl = cloth.image_url ? (cloth.image_url.startsWith('http') ? cloth.image_url : `${baseUrl}${cloth.image_url}`) : '';
                        clothesList.insertAdjacentHTML('beforeend', `
                            <div class="clothes-item">
                                <img src="${clothImageUrl}" alt="${cloth.name || 'N/A'}">
                                <div class="clothes-item-info">
                                    <p><strong>Название:</strong> <a href="/admin/clothes/${cloth.id}">${cloth.name || 'N/A'}</a></p>
                                    <p><strong>Пол:</strong> ${cloth.gender || 'N/A'}</p>
                                    <p><strong>Ссылка:</strong> <a href="${cloth.link || '#'}" target="_blank">${cloth.link || 'N/A'}</a></p>
                                </div>
                                <button class="remove-clothes-btn edit-field" data-category-id="${category.id}" data-clothes-id="${cloth.id}" style="display: none;">Удалить</button>
                            </div>
                        `);
                    });
                } else {
                    clothesList.textContent = 'Нет одежды';
                }
                categoryItem.appendChild(clothesList);
                categoriesContainer.appendChild(categoryItem);
            });
        } else {
            categoriesContainer.textContent = 'Нет категорий';
        }

        document.querySelector('h2').textContent = `Детали лука: ${look.name || 'N/A'}`;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('look-details').innerHTML = `<p>Ошибка: ${error.message}</p>`;
    }
}

function toggleEditMode() {
    isEditing = !isEditing;
    const editableFields = document.querySelectorAll('[data-editable]');
    const editFields = document.querySelectorAll('.edit-field');
    const editBtn = document.getElementById('edit-btn');
    const saveBtn = document.getElementById('save-btn');
    const cancelBtn = document.getElementById('cancel-btn');

    if (isEditing) {
        editableFields.forEach(field => field.style.display = 'none');
        editFields.forEach(field => field.style.display = 'block');
        editBtn.style.display = 'none';
        saveBtn.style.display = 'inline-block';
        cancelBtn.style.display = 'inline-block';
    } else {
        editableFields.forEach(field => field.style.display = 'block');
        editFields.forEach(field => field.style.display = 'none');
        editBtn.style.display = 'inline-block';
        saveBtn.style.display = 'none';
        cancelBtn.style.display = 'none';
    }
}

function cancelEdit() {
    // Восстанавливаем оригинальные значения
    document.getElementById('edit-look-name').value = originalData.name || '';
    document.getElementById('edit-look-gender').value = originalData.gender || 'унисекс';
    document.getElementById('edit-look-description').value = originalData.description || '';
    document.getElementById('edit-look-checked').value = originalData.checked ? 'true' : 'false';
    document.getElementById('edit-look-pushed').value = originalData.pushed ? 'true' : 'false';

    // Восстанавливаем промпты
    const editPromptsContainer = document.getElementById('edit-look-image-prompts');
    editPromptsContainer.innerHTML = '';
    if (originalData.image_prompts?.length) {
        originalData.image_prompts.forEach(prompt => {
            editPromptsContainer.insertAdjacentHTML('beforeend', `
                <div class="prompt-item">
                    <input type="text" value="${prompt}" class="prompt-input">
                    <button class="remove-prompt-btn">Удалить</button>
                </div>
            `);
        });
    }

    // Восстанавливаем изображения
    const editImageContainer = document.getElementById('edit-look-image-urls');
    editImageContainer.innerHTML = '';
    if (originalData.image_urls?.length) {
        originalData.image_urls.forEach(url => {
            const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`;
            editImageContainer.insertAdjacentHTML('beforeend', `
                <div class="image-item">
                    <img src="${fullUrl}" alt="Image" data-original="${url}">
                    <button class="remove-image-btn" data-url="${url}">Удалить</button>
                </div>
            `);
        });
    }

    // Показываем все скрытые элементы
    document.querySelectorAll('.category-item').forEach(item => {
        item.style.display = 'block';
    });
    document.querySelectorAll('.clothes-item').forEach(item => {
        item.style.display = 'flex';
    });

    // Очищаем списки удаленных элементов
    deletedCategories.clear();
    deletedClothes.clear();

    toggleEditMode();
}

async function saveChanges() {
    const currentData = {
        name: document.getElementById('edit-look-name').value,
        gender: document.getElementById('edit-look-gender').value,
        description: document.getElementById('edit-look-description').value,
        image_prompts: Array.from(document.querySelectorAll('.prompt-input')).map(input => input.value).filter(Boolean),
        image_urls: Array.from(document.querySelectorAll('.image-item img')).map(img => img.dataset.original),
        checked: document.getElementById('edit-look-checked').value === 'true',
        pushed: document.getElementById('edit-look-pushed').value === 'true'
    };

    const updatedData = {};
    if (currentData.name !== originalData.name) updatedData.name = currentData.name;
    if (currentData.gender !== originalData.gender) updatedData.gender = currentData.gender;
    if (currentData.description !== originalData.description) updatedData.description = currentData.description;
    if (JSON.stringify(currentData.image_prompts) !== JSON.stringify(originalData.image_prompts || [])) {
        updatedData.image_prompts = currentData.image_prompts;
    }
    if (JSON.stringify(currentData.image_urls) !== JSON.stringify(originalData.image_urls || [])) {
        updatedData.image_urls = currentData.image_urls;
    }
    if (currentData.checked !== originalData.checked) updatedData.checked = currentData.checked;
    if (currentData.pushed !== originalData.pushed) updatedData.pushed = currentData.pushed;

    try {
        // Сначала применяем изменения к основным данным
        if (Object.keys(updatedData).length > 0) {
            const response = await fetch(`/api/looks/${lookId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': 'Bearer ' + getApiToken()
                },
                body: JSON.stringify(updatedData)
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Затем удаляем категории
        for (const categoryId of deletedCategories) {
            const response = await fetch(`/api/looks/${lookId}/categories/${categoryId}`, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': 'Bearer ' + getApiToken()
                }
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Затем удаляем одежду из категорий
        for (const [categoryId, clothesId] of deletedClothes) {
            const response = await fetch(`/api/looks/${lookId}/categories/${categoryId}/clothes/${clothesId}`, {
                method: 'DELETE',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': 'Bearer ' + getApiToken()
                }
            });
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        }

        toggleEditMode();
        await loadLookDetails();
    } catch (error) {
        console.error('Error saving changes:', error);
        alert('Ошибка при сохранении: ' + error.message);
    }
}

async function publishLookToSocialMedia() {
    try {
        const response = await fetch(`/api/looks/${lookId}/publish`, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + getApiToken()
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
        }
        
        const result = await response.json();
        alert(`Лук успешно отправлен в социальные сети!\nTask ID: ${result.task_id}`);
        
        // Обновляем данные лука
        await loadLookDetails();
    } catch (error) {
        console.error('Error publishing look:', error);
        alert('Ошибка при публикации: ' + error.message);
    }
}

function addPromptField() {
    const editPromptsContainer = document.getElementById('edit-look-image-prompts');
    editPromptsContainer.insertAdjacentHTML('beforeend', `
        <div class="prompt-item">
            <input type="text" class="prompt-input" placeholder="Новый промпт">
            <button class="remove-prompt-btn">Удалить</button>
        </div>
    `);
}

async function deleteLook() {
    if (!confirm('Вы уверены, что хотите удалить этот лук? Это действие нельзя отменить.')) {
        return;
    }

    try {
        const response = await fetch(`/api/looks/${lookId}`, {
            method: 'DELETE',
            headers: {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + getApiToken()
            }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        window.location.href = '/admin/looks/';
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка при удалении: ' + error.message);
    }
}

async function checkLook() {
    try {
        const response = await fetch(`/api/looks/${lookId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + getApiToken()
            },
            body: JSON.stringify({ checked: true })
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        await loadLookDetails();
    } catch (error) {
        console.error('Error:', error);
        alert('Ошибка при обновлении статуса: ' + error.message);
    }
}

let currentCategoryId = null;

async function removeClothesFromCategory(categoryId, clothesId) {
    if (!confirm('Вы уверены, что хотите удалить эту вещь из категории?')) return;

    // Добавляем в список удаленных
    deletedClothes.add([categoryId, clothesId]);

    // Скрываем элемент из интерфейса
    const clothesItem = document.querySelector(`.remove-clothes-btn[data-category-id="${categoryId}"][data-clothes-id="${clothesId}"]`).closest('.clothes-item');
    clothesItem.style.display = 'none';
}

async function deleteCategory(categoryId) {
    if (!confirm('Вы уверены, что хотите удалить эту категорию?')) return;

    // Добавляем в список удаленных
    deletedCategories.add(categoryId);

    // Скрываем элемент из интерфейса
    const categoryItem = document.querySelector(`.delete-category-btn[data-category-id="${categoryId}"]`).closest('.category-item');
    categoryItem.style.display = 'none';
}

document.getElementById('edit-btn').addEventListener('click', toggleEditMode);
document.getElementById('save-btn').addEventListener('click', saveChanges);
document.getElementById('cancel-btn').addEventListener('click', cancelEdit);
document.getElementById('add-prompt-btn').addEventListener('click', addPromptField);
document.getElementById('delete-btn').addEventListener('click', deleteLook);
document.getElementById('check-look-btn').addEventListener('click', checkLook);
document.getElementById('publish-btn').addEventListener('click', publishLookToSocialMedia);

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-prompt-btn')) {
        e.target.parentElement.remove();
    }
    if (e.target.classList.contains('remove-image-btn')) {
        const imageItem = e.target.closest('.image-item');
        const originalUrl = imageItem.querySelector('img').dataset.original;
        imageItem.remove();
    }
    if (e.target.classList.contains('remove-clothes-btn')) {
        removeClothesFromCategory(e.target.dataset.categoryId, e.target.dataset.clothesId);
    }
    if (e.target.classList.contains('delete-category-btn')) {
        deleteCategory(e.target.dataset.categoryId);
    }
    if (e.target.id === 'close-modal-btn') {
        document.getElementById('add-clothes-modal').style.display = 'none';
    }
});

loadLookDetails();

// Получение токена из localStorage
function getApiToken() {
    return localStorage.getItem('api_token');
}