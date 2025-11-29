// Property filtering and interactive features
document.addEventListener('DOMContentLoaded', function() {
    // Add property card class to all property items for hover effects
    const propertyItems = document.querySelectorAll('.property__card');
    propertyItems.forEach(item => {
        item.classList.add('property-card');
    });

    // Create quick filter buttons container
    const createFilterButtons = () => {
        const propertySection = document.querySelector('.property__section');
        if (!propertySection) return;

        const filterContainer = document.createElement('div');
        filterContainer.className = 'container';
        filterContainer.innerHTML = `
            <div class="row">
                <div class="col-12">
                    <div id="quickFilterButtons" class="text-center">
                        <h4 class="mb-3">Quick Filters</h4>
                        <button data-filter="all" class="filter-active">All Properties</button>
                        <button data-filter="apartment">Apartments</button>
                        <button data-filter="house">Houses</button>
                        <button data-filter="villa">Villas</button>
                        <button data-filter="price-low">Price: Low to High</button>
                        <button data-filter="price-high">Price: High to Low</button>
                    </div>
                </div>
            </div>
        `;
        
        // Insert after the section opening but before other content
        const firstChild = propertySection.firstChild;
        propertySection.insertBefore(filterContainer, firstChild);
        
        // Add event listeners to filter buttons
        setupFilterButtons();
    };

    // Setup filter button functionality
    const setupFilterButtons = () => {
        const filterButtons = document.querySelectorAll('#quickFilterButtons button');
        if (!filterButtons.length) return;
        
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('filter-active'));
                
                // Add active class to clicked button
                this.classList.add('filter-active');
                
                const filterValue = this.getAttribute('data-filter');
                filterProperties(filterValue);
            });
        });
    };

    // Filter properties based on selected filter
    const filterProperties = (filter) => {
        const properties = document.querySelectorAll('.property-card');
        
        properties.forEach(property => {
            // Show all properties if "all" filter is selected
            if (filter === 'all') {
                property.style.display = 'block';
                return;
            }
            
            // Get property type and price from data attributes or content
            const propertyType = property.getAttribute('data-property-type') || 
                                property.textContent.toLowerCase();
            
            const priceElement = property.querySelector('.property__card--price');
            let price = 0;
            
            if (priceElement) {
                // Extract numeric price value
                const priceText = priceElement.textContent;
                const priceMatch = priceText.match(/[\d,]+/);
                if (priceMatch) {
                    price = parseInt(priceMatch[0].replace(/,/g, ''));
                }
            }
            
            // Apply filters
            switch(filter) {
                case 'apartment':
                    property.style.display = propertyType.includes('apartment') ? 'block' : 'none';
                    break;
                case 'house':
                    property.style.display = propertyType.includes('house') ? 'block' : 'none';
                    break;
                case 'villa':
                    property.style.display = propertyType.includes('villa') ? 'block' : 'none';
                    break;
                case 'price-low':
                    // Show all but sort by price
                    property.style.display = 'block';
                    sortPropertiesByPrice(true);
                    break;
                case 'price-high':
                    // Show all but sort by price
                    property.style.display = 'block';
                    sortPropertiesByPrice(false);
                    break;
                default:
                    property.style.display = 'block';
            }
        });
    };

    // Sort properties by price
    const sortPropertiesByPrice = (ascending) => {
        const propertyContainer = document.querySelector('.property__items');
        if (!propertyContainer) return;
        
        const properties = Array.from(propertyContainer.querySelectorAll('.property-card'));
        
        properties.sort((a, b) => {
            const priceA = extractPrice(a);
            const priceB = extractPrice(b);
            
            return ascending ? priceA - priceB : priceB - priceA;
        });
        
        // Remove all properties and re-append in sorted order
        properties.forEach(property => {
            propertyContainer.appendChild(property);
        });
    };

    // Helper function to extract price from property card
    const extractPrice = (propertyCard) => {
        const priceElement = propertyCard.querySelector('.property__card--price');
        if (!priceElement) return 0;
        
        const priceText = priceElement.textContent;
        const priceMatch = priceText.match(/[\d,]+/);
        
        return priceMatch ? parseInt(priceMatch[0].replace(/,/g, '')) : 0;
    };

    // Add data attributes to property cards for filtering
    const addPropertyTypeAttributes = () => {
        const properties = document.querySelectorAll('.property-card');
        
        properties.forEach(property => {
            const titleElement = property.querySelector('.property__card--title');
            if (!titleElement) return;
            
            const title = titleElement.textContent.toLowerCase();
            
            // Set property type based on title content
            if (title.includes('apartment')) {
                property.setAttribute('data-property-type', 'apartment');
            } else if (title.includes('house')) {
                property.setAttribute('data-property-type', 'house');
            } else if (title.includes('villa')) {
                property.setAttribute('data-property-type', 'villa');
            } else {
                // Default to house if not specified
                property.setAttribute('data-property-type', 'house');
            }
        });
    };

    // Initialize all interactive features
    createFilterButtons();
    addPropertyTypeAttributes();
});