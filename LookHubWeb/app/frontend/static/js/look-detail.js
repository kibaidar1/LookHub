async function loadLookDetail() {
    const lookId = window.location.pathname.split('/').pop();
    try {
        const response = await fetch(`/api/looks/${lookId}`);
        if (!response.ok) throw new Error('Failed to load look');
        const look = await response.json();
        console.log('Received look data:', look);
        renderLookDetail(look);
    } catch (error) {
        console.error('Error loading look:', error);
        document.getElementById('look-info').innerHTML = '<p>Ошибка загрузки образа.</p>';
    }
}

function renderLookDetail(look) {
    // Рендерим все изображения
    const imagesList = document.getElementById('look-images-list');
    imagesList.innerHTML = '';
    if (Array.isArray(look.image_urls)) {
        look.image_urls.forEach((url, index) => {
            const li = document.createElement('li');
            li.className = 'image__item';
            li.setAttribute('data-aos', 'fade-up');
            li.setAttribute('data-aos-delay', `${index * 100}`); // Каждое следующее изображение появляется с задержкой 100мс
            li.innerHTML = `<img src="${url}" alt="Look image">`;
            imagesList.appendChild(li);
        });
    }
    // Информация о луке
    const info = document.getElementById('look-info');
    info.innerHTML = `
        <div class="look-info" data-aos="fade-up">
            <h2 class="look-name" data-aos="zoom-in-up">${look.name || ''}</h2>
            <p class="look-description" data-aos="zoom-in-up">${look.description || ''}</p>
        </div>
    `;
    // Одежда
    const clothes = document.getElementById('look-clothes');
    if (Array.isArray(look.clothes_categories) && look.clothes_categories.length > 0) {
        clothes.innerHTML = `
            <div class="look-clothes">
                <h2 class="visually-hidden">Look clothes</h2>
                <ul class="clothes-categories__list">
                    ${look.clothes_categories.map((cat, catIndex) => `
                        <li class="clothes-categories__item" data-aos="fade-right">
                            <h3 class="clothes-category__name">${cat.name || ''}</h3>
                            <ul class="links__list">
                                ${(cat.clothes || []).map((item, itemIndex) => `
                                    <li class="links__item" data-aos="fade-up" data-aos-delay="${(catIndex * 200) + (itemIndex * 100)}">
                                        ${item.link ? `<a href="${item.link}" target="_blank" rel="noopener noreferrer" class="clothes-item__link">` : ''}
                                            <div class="clothes-item__image">
                                                ${item.image_url ? `<img src="${item.image_url}" alt="${item.name || ''}">` : ''}
                                            </div>
                                            <div class="clothes-item__info">
                                                <h4 class="clothes-item__name">${item.name || ''}</h4>
                                            </div>
                                        ${item.link ? `</a>` : ''}
                                    </li>
                                `).join('')}
                            </ul>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    } else {
        clothes.innerHTML = '';
    }
}

document.addEventListener('DOMContentLoaded', loadLookDetail); 