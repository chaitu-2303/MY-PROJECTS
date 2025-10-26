// Property Comparison Feature
document.addEventListener('DOMContentLoaded', function() {
    // Initialize comparison storage
    let comparisonList = JSON.parse(localStorage.getItem('propertyCompare')) || [];
    const maxCompare = 3; // Maximum properties to compare
    
    // Add compare buttons to property cards
    function addCompareButtons() {
        const propertyCards = document.querySelectorAll('.property__card');
        
        propertyCards.forEach(card => {
            // Check if button already exists
            if (card.querySelector('.compare-btn')) return;
            
            // Create compare button
            const compareBtn = document.createElement('button');
            compareBtn.className = 'compare-btn';
            compareBtn.innerHTML = '<i class="fas fa-exchange-alt"></i> Compare';
            compareBtn.style.position = 'absolute';
            compareBtn.style.bottom = '10px';
            compareBtn.style.right = '10px';
            compareBtn.style.backgroundColor = '#ff6d34';
            compareBtn.style.color = 'white';
            compareBtn.style.border = 'none';
            compareBtn.style.borderRadius = '4px';
            compareBtn.style.padding = '5px 10px';
            compareBtn.style.cursor = 'pointer';
            compareBtn.style.zIndex = '10';
            
            // Get property data
            const propertyId = card.getAttribute('data-id') || Math.random().toString(36).substr(2, 9);
            if (!card.getAttribute('data-id')) {
                card.setAttribute('data-id', propertyId);
            }
            
            const propertyTitle = card.querySelector('.property__card--title')?.textContent || 'Property';
            const propertyPrice = card.querySelector('.property__card--price')?.textContent || 'N/A';
            const propertyImg = card.querySelector('.property__card--thumbnail img')?.src || '';
            const propertyLocation = card.querySelector('.property__card--location')?.textContent || 'N/A';
            const propertyBeds = card.querySelector('.property__card--meta span:nth-child(1)')?.textContent || 'N/A';
            const propertyBaths = card.querySelector('.property__card--meta span:nth-child(2)')?.textContent || 'N/A';
            const propertySqft = card.querySelector('.property__card--meta span:nth-child(3)')?.textContent || 'N/A';
            
            // Check if property is already in comparison list
            const isInCompare = comparisonList.some(item => item.id === propertyId);
            if (isInCompare) {
                compareBtn.innerHTML = '<i class="fas fa-check"></i> Added to Compare';
                compareBtn.style.backgroundColor = '#28a745';
            }
            
            // Add click event
            compareBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const isAlreadyAdded = comparisonList.some(item => item.id === propertyId);
                
                if (isAlreadyAdded) {
                    // Remove from comparison
                    comparisonList = comparisonList.filter(item => item.id !== propertyId);
                    compareBtn.innerHTML = '<i class="fas fa-exchange-alt"></i> Compare';
                    compareBtn.style.backgroundColor = '#ff6d34';
                    showToast('Property removed from comparison');
                } else {
                    // Check if max properties reached
                    if (comparisonList.length >= maxCompare) {
                        showToast(`You can only compare up to ${maxCompare} properties. Please remove one first.`);
                        return;
                    }
                    
                    // Add to comparison
                    comparisonList.push({
                        id: propertyId,
                        title: propertyTitle,
                        price: propertyPrice,
                        image: propertyImg,
                        location: propertyLocation,
                        beds: propertyBeds,
                        baths: propertyBaths,
                        sqft: propertySqft
                    });
                    
                    compareBtn.innerHTML = '<i class="fas fa-check"></i> Added to Compare';
                    compareBtn.style.backgroundColor = '#28a745';
                    showToast('Property added to comparison');
                }
                
                // Save to localStorage
                localStorage.setItem('propertyCompare', JSON.stringify(comparisonList));
                
                // Update comparison counter
                updateCompareCounter();
                
                // Show comparison bar if items exist
                toggleComparisonBar();
            });
            
            // Add button to card
            card.style.position = 'relative';
            card.appendChild(compareBtn);
        });
    }
    
    // Create and show toast notification
    function showToast(message) {
        // Remove existing toast if any
        const existingToast = document.querySelector('.compare-toast');
        if (existingToast) {
            existingToast.remove();
        }
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = 'compare-toast';
        toast.textContent = message;
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.left = '50%';
        toast.style.transform = 'translateX(-50%)';
        toast.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
        toast.style.color = 'white';
        toast.style.padding = '10px 20px';
        toast.style.borderRadius = '4px';
        toast.style.zIndex = '1000';
        
        // Add to body
        document.body.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    // Update comparison counter
    function updateCompareCounter() {
        let compareCounter = document.querySelector('.compare-counter');
        
        if (!compareCounter) {
            // Create counter if it doesn't exist
            compareCounter = document.createElement('div');
            compareCounter.className = 'compare-counter';
            compareCounter.style.position = 'fixed';
            compareCounter.style.top = '100px';
            compareCounter.style.right = '20px';
            compareCounter.style.backgroundColor = '#ff6d34';
            compareCounter.style.color = 'white';
            compareCounter.style.borderRadius = '50%';
            compareCounter.style.width = '30px';
            compareCounter.style.height = '30px';
            compareCounter.style.display = 'flex';
            compareCounter.style.justifyContent = 'center';
            compareCounter.style.alignItems = 'center';
            compareCounter.style.fontWeight = 'bold';
            compareCounter.style.zIndex = '100';
            compareCounter.style.cursor = 'pointer';
            
            // Add click event to show comparison bar
            compareCounter.addEventListener('click', function() {
                toggleComparisonBar(true);
            });
            
            document.body.appendChild(compareCounter);
        }
        
        // Update counter text
        compareCounter.textContent = comparisonList.length;
        
        // Hide if empty
        if (comparisonList.length === 0) {
            compareCounter.style.display = 'none';
        } else {
            compareCounter.style.display = 'flex';
        }
    }
    
    // Toggle comparison bar
    function toggleComparisonBar(forceShow = false) {
        let comparisonBar = document.querySelector('.comparison-bar');
        
        if (comparisonList.length === 0 && !forceShow) {
            // Hide bar if no items and not forced to show
            if (comparisonBar) {
                comparisonBar.style.display = 'none';
            }
            return;
        }
        
        if (!comparisonBar) {
            // Create comparison bar
            comparisonBar = document.createElement('div');
            comparisonBar.className = 'comparison-bar';
            comparisonBar.style.position = 'fixed';
            comparisonBar.style.bottom = '0';
            comparisonBar.style.left = '0';
            comparisonBar.style.width = '100%';
            comparisonBar.style.backgroundColor = 'white';
            comparisonBar.style.boxShadow = '0 -2px 10px rgba(0, 0, 0, 0.1)';
            comparisonBar.style.padding = '15px';
            comparisonBar.style.zIndex = '999';
            comparisonBar.style.display = 'flex';
            comparisonBar.style.flexDirection = 'column';
            
            document.body.appendChild(comparisonBar);
        }
        
        // Show bar
        comparisonBar.style.display = 'flex';
        
        // Update bar content
        updateComparisonBar(comparisonBar);
    }
    
    // Update comparison bar content
    function updateComparisonBar(bar) {
        // Clear existing content
        bar.innerHTML = '';
        
        // Create header
        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.justifyContent = 'space-between';
        header.style.alignItems = 'center';
        header.style.marginBottom = '10px';
        
        const title = document.createElement('h3');
        title.textContent = 'Property Comparison';
        title.style.margin = '0';
        
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.style.background = 'none';
        closeBtn.style.border = 'none';
        closeBtn.style.fontSize = '24px';
        closeBtn.style.cursor = 'pointer';
        closeBtn.addEventListener('click', function() {
            bar.style.display = 'none';
        });
        
        header.appendChild(title);
        header.appendChild(closeBtn);
        bar.appendChild(header);
        
        // Create properties container
        const propertiesContainer = document.createElement('div');
        propertiesContainer.style.display = 'flex';
        propertiesContainer.style.overflowX = 'auto';
        propertiesContainer.style.gap = '15px';
        
        if (comparisonList.length === 0) {
            // Show empty message
            const emptyMsg = document.createElement('p');
            emptyMsg.textContent = 'No properties added for comparison yet.';
            emptyMsg.style.margin = '20px 0';
            propertiesContainer.appendChild(emptyMsg);
        } else {
            // Add properties
            comparisonList.forEach(property => {
                const propertyCard = document.createElement('div');
                propertyCard.style.minWidth = '250px';
                propertyCard.style.border = '1px solid #eee';
                propertyCard.style.borderRadius = '8px';
                propertyCard.style.overflow = 'hidden';
                
                // Property image
                const img = document.createElement('img');
                img.src = property.image || 'assets/img/property/property1.jpg';
                img.alt = property.title;
                img.style.width = '100%';
                img.style.height = '150px';
                img.style.objectFit = 'cover';
                
                // Property details
                const details = document.createElement('div');
                details.style.padding = '10px';
                
                const propertyTitle = document.createElement('h4');
                propertyTitle.textContent = property.title;
                propertyTitle.style.margin = '0 0 5px 0';
                
                const propertyPrice = document.createElement('p');
                propertyPrice.textContent = property.price;
                propertyPrice.style.fontWeight = 'bold';
                propertyPrice.style.color = '#ff6d34';
                propertyPrice.style.margin = '0 0 5px 0';
                
                const propertyLocation = document.createElement('p');
                propertyLocation.textContent = property.location;
                propertyLocation.style.margin = '0 0 5px 0';
                propertyLocation.style.fontSize = '14px';
                
                const propertyMeta = document.createElement('div');
                propertyMeta.style.display = 'flex';
                propertyMeta.style.justifyContent = 'space-between';
                propertyMeta.style.fontSize = '14px';
                propertyMeta.style.color = '#666';
                
                propertyMeta.innerHTML = `
                    <span>${property.beds}</span>
                    <span>${property.baths}</span>
                    <span>${property.sqft}</span>
                `;
                
                // Remove button
                const removeBtn = document.createElement('button');
                removeBtn.textContent = 'Remove';
                removeBtn.style.width = '100%';
                removeBtn.style.padding = '8px';
                removeBtn.style.backgroundColor = '#f44336';
                removeBtn.style.color = 'white';
                removeBtn.style.border = 'none';
                removeBtn.style.borderRadius = '4px';
                removeBtn.style.marginTop = '10px';
                removeBtn.style.cursor = 'pointer';
                
                removeBtn.addEventListener('click', function() {
                    // Remove from comparison list
                    comparisonList = comparisonList.filter(item => item.id !== property.id);
                    
                    // Save to localStorage
                    localStorage.setItem('propertyCompare', JSON.stringify(comparisonList));
                    
                    // Update UI
                    updateCompareCounter();
                    updateComparisonBar(bar);
                    
                    // Update compare buttons
                    const propertyCards = document.querySelectorAll('.property__card');
                    propertyCards.forEach(card => {
                        if (card.getAttribute('data-id') === property.id) {
                            const btn = card.querySelector('.compare-btn');
                            if (btn) {
                                btn.innerHTML = '<i class="fas fa-exchange-alt"></i> Compare';
                                btn.style.backgroundColor = '#ff6d34';
                            }
                        }
                    });
                    
                    showToast('Property removed from comparison');
                    
                    // Hide bar if empty
                    if (comparisonList.length === 0) {
                        bar.style.display = 'none';
                    }
                });
                
                // Append elements
                details.appendChild(propertyTitle);
                details.appendChild(propertyPrice);
                details.appendChild(propertyLocation);
                details.appendChild(propertyMeta);
                details.appendChild(removeBtn);
                
                propertyCard.appendChild(img);
                propertyCard.appendChild(details);
                
                propertiesContainer.appendChild(propertyCard);
            });
        }
        
        bar.appendChild(propertiesContainer);
        
        // Add compare button if there are properties
        if (comparisonList.length >= 2) {
            const compareBtn = document.createElement('button');
            compareBtn.textContent = 'Compare Properties';
            compareBtn.style.backgroundColor = '#ff6d34';
            compareBtn.style.color = 'white';
            compareBtn.style.border = 'none';
            compareBtn.style.borderRadius = '4px';
            compareBtn.style.padding = '10px 20px';
            compareBtn.style.marginTop = '15px';
            compareBtn.style.alignSelf = 'center';
            compareBtn.style.cursor = 'pointer';
            
            compareBtn.addEventListener('click', function() {
                // Create comparison page URL
                window.location.href = 'property-compare.html';
            });
            
            bar.appendChild(compareBtn);
        }
    }
    
    // Initialize feature
    function init() {
        addCompareButtons();
        updateCompareCounter();
        
        // Show comparison bar if there are items
        if (comparisonList.length > 0) {
            toggleComparisonBar();
        }
    }
    
    // Run initialization
    init();
    
    // Add to window object for access from other scripts
    window.propertyCompare = {
        addCompareButtons,
        updateCompareCounter,
        toggleComparisonBar
    };
});