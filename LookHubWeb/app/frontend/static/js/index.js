let currentPage = 1;
let isLoading = false;
let hasMore = true;

async function loadLooks(page = 1) {
    try {
        const response = await fetch(`/api/looks?checked=true&page=${page}&page_size=12`);
        if (!response.ok) throw new Error('Failed to load looks');
        return await response.json();
    } catch (error) {
        console.error('Error loading looks:', error);
        return null;
    }
}

function createLookCard(look) {
    // Берём первое изображение из массива
    const previewImg = Array.isArray(look.image_urls) && look.image_urls.length > 0 ? look.image_urls[0] : '';
    // Обрезаем описание до первого предложения
    let description = look.description || '';
    const firstDotIdx = description.indexOf('.') !== -1 ? description.indexOf('.') + 1 : description.length;
    description = description.slice(0, firstDotIdx).trim();
    const card = document.createElement('li');
    card.innerHTML = `
        <div class="card" data-aos="zoom-in-up">
            <a href="/looks/${look.id}"><img src="${previewImg}" alt="Image"></a>
            <div class="card__info">
                <a class="link" href="/looks/${look.id}"><h3 class="card__title">${look.name || ''}</h3></a>
                <p class="card__description">${description}</p>
            </div>
        </div>
    `;
    return card;
}

async function appendLooks(looks) {
    const container = document.getElementById('looks-list');
    looks.forEach(look => {
        const lookCard = createLookCard(look);
        container.appendChild(lookCard);
    });
}

async function loadMoreLooks() {
    if (isLoading || !hasMore) return;
    isLoading = true;
    currentPage++;
    const data = await loadLooks(currentPage);
    if (data && data.results.length > 0) {
        await appendLooks(data.results);
        hasMore = data.results.length === 12;
    } else {
        hasMore = false;
    }
    isLoading = false;
}

window.addEventListener('scroll', () => {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    if (scrollTop + clientHeight >= scrollHeight - 5) {
        loadMoreLooks();
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    const data = await loadLooks(1);
    if (data && data.results.length > 0) {
        await appendLooks(data.results);
        hasMore = data.results.length === 12;
    }
}); 