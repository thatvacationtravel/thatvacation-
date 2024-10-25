document.addEventListener('DOMContentLoaded', function() {
    const categoryDescElements = document.querySelectorAll('.category-desc');
    categoryDescElements.forEach(function(categoryDescElement) {
        if (categoryDescElement) {
            let categoryDesc = categoryDescElement.getAttribute('data-category-desc');
            categoryDesc = categoryDesc.replace(/\\u002D/g, '-').replace(/\\u0020/g, ' ');
            let result;
            if (categoryDesc.trim() === "Interior Bella" || categoryDesc.trim() === "Ocean View Bella" || categoryDesc.trim() === "Balcony  Bella") {
                result = {
                    name: categoryDesc.trim(),
                    size: null,
                    decks: null
                };
            } else if (categoryDesc.includes("Obstructed view")) {
                result = parseObstructedView(categoryDesc);
            } else {
                result = parseCategoryDesc(categoryDesc);

                if (!result) {
                    result = parseSpecialCase(categoryDesc);
                }
            }

            if (result) {
                const parentElement = categoryDescElement.parentElement;
                parentElement.querySelector(".category-name").innerHTML = '<i class="fas fa-info-circle custom-icon"></i> ' + result.name;

                if (result.size) {
                    parentElement.querySelector(".category-size").innerHTML = '<i class="fa fa-ruler-combined custom-icon"></i> ' + result.size;
                } else {
                    parentElement.querySelector(".category-size").innerHTML = '';
                }

                if (result.decks) {
                    parentElement.querySelector(".category-decks").innerHTML = '<i class="fas fa-layer-group custom-icon"></i> ' + result.decks;
                } else {
                    parentElement.querySelector(".category-decks").innerHTML = '';
                }
            } else {

            }
        }
    });

    function parseCategoryDesc(text) {

        const regex = /^(.*?)\s*\(\s*(?:Partial view\s*-\s*)?Module\s*(\d+\s*sqm|\d+\s*-\s*\d+\s*sqm)(?:\s*-\s*Balcony\s*(\d+\s*sqm|\d+\s*-\s*\d+\s*sqm))?\s*-\s*Decks\s*([\d\s-]+)\s*(.*?)\s*\)$/i;
        const matches = text.match(regex);

        if (matches) {
            return {
                name: matches[1].trim(),
                size: matches[2].trim() + (matches[3] ? ' + Balcony ' + matches[3].trim() : ''),
                decks: 'Decks ' + matches[4].trim() + (matches[5] ? ' ' + matches[5].trim() : '')
            };
        }

        return null;
    }

    function parseSpecialCase(text) {
        const specialCaseRegex = /^(.*?)\s*\(Module\s*(\d+\s*-\s*\d+\s*sqm)Balcony\s*(\d+\s*-\s*\d+\s*sqm)Decks\s*([\d\s-]+)\)$/i;
        const matches = text.match(specialCaseRegex);

        if (matches) {
            return {
                name: matches[1].trim(),
                size: matches[2].trim() + ' + Balcony ' + matches[3].trim(),
                decks: 'Decks ' + matches[4].trim()
            };
        }

        return null;
    }

    function parseObstructedView(text) {
        const obstructedViewRegex = /^(.*?)\s*\(\s*Obstructed view\s*-\s*Module\s*(\d+\s*sqm)\s*-\s*Decks\s*([\d\s-]+)\s*\)$/i;
        const matches = text.match(obstructedViewRegex);

        if (matches) {
            return {
                name: matches[1].trim(),
                size: matches[2].trim(),
                decks: 'Decks ' + matches[3].trim()
            };
        }

        return null;
    }
});
