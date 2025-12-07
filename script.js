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
    if (e.target.closest('a')) return;

    const total = pages.length;
    const clickedElement = e.target.closest('.journal-cover, .journal-page');
    
    // click on front cover when closed: flip forward
    if (clickedElement?.classList.contains('journal-cover--front') && 
        !frontCover.classList.contains('is-open') && 
        currentPage < total) {
        currentPage += 1;
        updateJournal();
    } 
    // click on a page that hasn't been flipped yet: flip forward
    else if (clickedElement?.classList.contains('journal-page') && 
             !clickedElement.classList.contains('is-flipped') && 
             currentPage < total) {
        currentPage += 1;
        updateJournal();
    }
    // click on a flipped page or back cover: flip backward
    else if (((clickedElement?.classList.contains('journal-page') && 
               clickedElement.classList.contains('is-flipped')) ||
              clickedElement?.classList.contains('journal-cover--back') ||
              (clickedElement?.classList.contains('journal-cover--front') && 
               frontCover.classList.contains('is-open'))) && 
             currentPage > 0) {
        currentPage -= 1;
        updateJournal();
    }
});

updateJournal();
