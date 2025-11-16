const pages = [...document.querySelectorAll(".journal-page")];
const journal = document.querySelector(".journal");
const frontCover = document.querySelector(".journal-cover--front");

let currentPage = 0;

const updateJournal = () => {
    pages.forEach((page, index) => {
        page.classList.toggle("is-flipped", index < currentPage);
    });

    frontCover.classList.toggle("is-open", currentPage > 0);

    const total = pages.length;
};

journal.addEventListener("click", (e) => {
    const rect = journal.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const midpoint = rect.width / 2;
    const total = pages.length;
    
    if (clickX > midpoint && currentPage < total) {
        // Click on right side - flip forward
        currentPage += 1;
        updateJournal();
    } else if (clickX <= midpoint && currentPage > 0) {
        // Click on left side - flip backward
        currentPage -= 1;
        updateJournal();
    }
});

updateJournal();
