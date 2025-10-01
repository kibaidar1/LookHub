const clothesId = window.location.pathname.split('/').pop();
let isEditing = false;
let originalData = {};
const baseUrl = window.location.origin;

const colourMap = {
    'белый': 'белый',
    'бежевый': 'бежевый',
    'серый': 'серый',
    'красный': 'красный',
    'розовый': 'розовый',
    'оранжевый': 'оранжевый',
    'желтый': 'желтый',
    'зеленый': 'зеленый',
    'голубой': 'голубой',
    'синий': 'синий',
    'фиолетовый': 'фиолетовый',
    'коричневый': 'коричневый',
    'черный': 'черный'
};
const validColours = Object.keys(colourMap);

async function loadClothesDetails() {
    try {
        const response = await fetch(`/api/clothes/${clothesId}`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const clothes = await response.json();
        originalData = { ...clothes };

        document.getElementById('clothes-id').textContent = clothes.id || 'N/A';
        document.getElementById('clothes-name').textContent = clothes.name || 'N/A';
        document.getElementById('edit-clothes-name').value = clothes.name || '';
        document.getElementById('clothes-description').textContent = clothes.description || 'Нет описания';
        document.getElementById('edit-clothes-description').value = clothes.description || '';

        // Отображение цветов в режиме просмотра
        const coloursContainer = document.getElementById('clothes-colours');
        coloursContainer.innerHTML = '';
        if (clothes.colours?.length) {
            coloursContainer.textContent = clothes.colours.map(c => colourMap[c] || c).join(', ');
        } else {
            coloursContainer.textContent = 'N/A';
        }

        // Создание полей для цветов в режиме редактирования
        const colourInputsContainer = document.getElementById('colour-inputs');
        colourInputsContainer.innerHTML = '';
        if (clothes.colours?.length) {
            clothes.colours.forEach((colour, index) => {
                colourInputsContainer.insertAdjacentHTML('beforeend', `
                    <div class="colour-item">
                        <input type="text" class="colour-input" value="${colour}" list="colour-list" data-index="${index}">
                        <button class="remove-colour-btn">Удалить</button>
                    </div>
                `);
            });
        }

        document.getElementById('clothes-gender').textContent = clothes.gender || 'N/A';
        document.getElementById('edit-clothes-gender').value = clothes.gender || 'унисекс';
        document.getElementById('clothes-link').innerHTML = clothes.link ? `<a href="${clothes.link}" target="_blank">${clothes.link}</a>` : 'N/A';
        document.getElementById('edit-clothes-link').value = clothes.link || '';
        const imageUrl = clothes.image_url ? (clothes.image_url.startsWith('http') ? clothes.image_url : `${baseUrl}${clothes.image_url}`) : '';
        document.getElementById('clothes-image-url').innerHTML = clothes.image_url ? `<img src="${imageUrl}" alt="${clothes.name || 'N/A'}">` : 'N/A';
        document.getElementById('edit-clothes-image-url').value = clothes.image_url || '';

        document.querySelector('h2').textContent = `Детали одежды: ${clothes.name || 'N/A'}`;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('clothes-details').innerHTML = `<p>Ошибка: ${error.message}</p>`;
    }
}

function toggleEditMode() {
    isEditing = !isEditing;
    const editableFields = document.querySelectorAll('[data-editable]');
    const editFields = document.querySelectorAll('.edit-field');
    const editBtn = document.getElementById('edit-btn');
    const saveBtn = document.getElementById('save-btn');

    if (isEditing) {
        editableFields.forEach(field => field.style.display = 'none');
        editFields.forEach(field => field.style.display = 'block');
        editBtn.style.display = 'none';
        saveBtn.style.display = 'inline-block';
    } else {
        editableFields.forEach(field => field.style.display = 'block');
        editFields.forEach(field => field.style.display = 'none');
        editBtn.style.display = 'inline-block';
        saveBtn.style.display = 'none';
    }
}

function addColourField() {
    const colourInputsContainer = document.getElementById('colour-inputs');
    const index = colourInputsContainer.children.length;
    colourInputsContainer.insertAdjacentHTML('beforeend', `
        <div class="colour-item">
            <input type="text" class="colour-input" value="" list="colour-list" data-index="${index}">
            <button class="remove-colour-btn">Удалить</button>
        </div>
    `);
}

// Получение токена из localStorage
function getApiToken() {
    return localStorage.getItem('api_token');
}

async function saveChanges() {
    const colourInputs = document.querySelectorAll('#colour-inputs .colour-input');
    console.log('Colour inputs found:', colourInputs.length); // Отладка: сколько полей найдено
    const currentColours = Array.from(colourInputs)
        .map(input => {
            const value = input.value.trim();
            console.log('Input value:', value); // Отладка: значение каждого поля
            return value;
        })
        .filter(colour => colour && validColours.includes(colour));
    console.log('Filtered colours:', currentColours); // Отладка: отфильтрованные цвета

    const currentData = {
        name: document.getElementById('edit-clothes-name').value,
        description: document.getElementById('edit-clothes-description').value,
        colours: currentColours,
        gender: document.getElementById('edit-clothes-gender').value,
        link: document.getElementById('edit-clothes-link').value,
        image_url: document.getElementById('edit-clothes-image-url').value
    };

    const updatedData = {};
    if (currentData.name !== originalData.name) updatedData.name = currentData.name;
    if (currentData.description !== originalData.description) updatedData.description = currentData.description;
    if (JSON.stringify(currentData.colours) !== JSON.stringify(originalData.colours || [])) {
        updatedData.colours = currentData.colours;
    }
    if (currentData.gender !== originalData.gender) updatedData.gender = currentData.gender;
    if (currentData.link !== originalData.link) updatedData.link = currentData.link;
    if (currentData.image_url !== originalData.image_url) updatedData.image_url = currentData.image_url;

    console.log('Updated data:', updatedData); // Отладка: что отправляется в API

    if (Object.keys(updatedData).length === 0) {
        toggleEditMode();
        return;
    }

    try {
        const response = await fetch(`/api/clothes/${clothesId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + getApiToken()
            },
            body: JSON.stringify(updatedData)
        });
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        toggleEditMode();
        await loadClothesDetails();
    } catch (error) {
        console.error('Error saving changes:', error);
        alert('Ошибка при сохранении: ' + error.message);
    }
}

document.getElementById('edit-btn').addEventListener('click', toggleEditMode);
document.getElementById('save-btn').addEventListener('click', saveChanges);
document.getElementById('add-colour-btn').addEventListener('click', addColourField);

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-colour-btn')) {
        e.target.parentElement.remove();
    }
});

loadClothesDetails();