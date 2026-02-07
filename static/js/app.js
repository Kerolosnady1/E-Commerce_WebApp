const yearTargets = document.querySelectorAll("[data-current-year]");
const currentYear = new Date().getFullYear();
yearTargets.forEach((target) => {
    target.textContent = currentYear;
});

const searchInput = document.querySelector("[data-search-input]");
const cards = Array.from(document.querySelectorAll("[data-search-card]"));
const countTarget = document.querySelector("[data-search-count]");

if (searchInput) {
    searchInput.addEventListener("input", (event) => {
        const query = event.target.value.trim().toLowerCase();
        let visible = 0;
        cards.forEach((card) => {
            const text = card.textContent.toLowerCase();
            const match = text.includes(query);
            card.style.display = match ? "flex" : "none";
            if (match) {
                visible += 1;
            }
        });
        if (countTarget) {
            countTarget.textContent = `${visible} صفحات متاحة`;
        }
    });
}
