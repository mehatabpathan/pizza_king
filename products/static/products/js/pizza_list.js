document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.pizza-filter');
    checkboxes.forEach(function(checkbox) {
      checkbox.addEventListener('change', function() {
        document.getElementById('pizza-filter-form').submit();
      });
    });
  });
  
  const sizeInputs = document.querySelectorAll('.pizza-size-input');
  sizeInputs.forEach(input => {
    input.addEventListener('change', function() {
      const selectedSize = this.value;
      const card = this.closest('.card');
      const basePrice = parseFloat(card.querySelector('.price').getAttribute('data-base-price'));
      let adjustedPrice = basePrice;
  
      if (selectedSize === '35') {
        adjustedPrice *= 1.1;
      } else if (selectedSize === '40') {
        adjustedPrice *= 1.3;
      }
      card.querySelector('.selected-size').value = selectedSize;
      card.querySelector('.price').textContent = `€${adjustedPrice.toFixed(2)}`;
      const image = card.querySelector('.card-img-top');
      if (selectedSize === '35') {
        image.style.transform = 'scale(1)';
      } else if (selectedSize === '40') {
        image.style.transform = 'scale(1.02)';
      } else {
        image.style.transform = 'scale(0.98)';
      }
    });
  });