function updatePreview(type, value) {
    const img = document.getElementById('preview-' + type);
    if (img) {
        const folder = type + 's'; // 'chair' -> 'chairs', 'plant' -> 'plants'
        img.src = `/static/images/furniture/${folder}/${value}.png`;
        img.style.display = 'block';
    }
}
