document.addEventListener('DOMContentLoaded', function() {
	const updateTotalPrice = () => {
    const basePrice = parseFloat(document.querySelector('.price').getAttribute('data-base-price'));
    let totalPrice = basePrice;
    const selectedSize = document.querySelector('.selected-size').value;
    let multiplier = 1;
    if (selectedSize === '35') {
      multiplier = 1.1;
    } else if (selectedSize === '40') {
      multiplier = 1.3;
    }
    totalPrice *= multiplier;
    const selectedToppingsInput = document.querySelector('.selected-toppings');
    if (selectedToppingsInput.value === '') {
      document.querySelector('.price').textContent = `€${totalPrice.toFixed(2)}`;
      return;
    }
    const selectedToppings = selectedToppingsInput.value.split(',');
    const toppingCards = document.querySelectorAll('.topping-card');
    selectedToppings.forEach(toppingId => {
      toppingCards.forEach(toppingCard => {
        const toppingPriceElement = toppingCard.querySelector('.topping-price');
        const toppingIdValue = toppingCard.querySelector('.add-icon').getAttribute('data-topping-id');
        const toppingPrice = parseFloat(toppingPriceElement.getAttribute('data-base-price'));

        if (toppingId === toppingIdValue) {
          const newToppingPrice = toppingPrice * multiplier;
          totalPrice += newToppingPrice;
        }
      });
    });
    document.querySelector('.price').textContent = `€${totalPrice.toFixed(2)}`;
  };

	const additionalToppingsText = document.querySelector('.card-text-additional-toppings');
	const toppingIcons = document.querySelectorAll('.add-icon');
	const selectedToppingsInput = document.querySelector('.selected-toppings');

	toppingIcons.forEach(icon => {
		icon.addEventListener('click', function() {
			const toppingId = this.getAttribute('data-topping-id');
			const card = this.closest('.topping-card');
			if (selectedToppingsInput.value === '') {
				selectedToppingsInput.value = toppingId;
				this.classList.add('selected');
				this.classList.remove('fa-plus');
				this.classList.add('fa-minus');
				card.classList.add('selected');
				additionalToppingsText.textContent += (', ' + card.querySelector('.card-title').textContent);
			} else {
				let selectedToppings = selectedToppingsInput.value.split(',');
				const index = selectedToppings.indexOf(toppingId);
				if (index !== -1) {
					selectedToppings.splice(index, 1);
					this.classList.remove('selected');
					this.classList.add('fa-plus');
					this.classList.remove('fa-minus');
					card.classList.remove('selected');
					additionalToppingsText.textContent = additionalToppingsText.textContent.split(', ').filter(topping => {
						if (topping !== card.querySelector('.card-title').textContent) {
						return true;
						}
					}).join(', ');
				} else {
					if (selectedToppings.length === 7) {
						const toppingLimitModal = new bootstrap.Modal(document.getElementById('toppingLimitModal'));
						toppingLimitModal.show();
						return;
				}
					selectedToppings.push(toppingId);
					this.classList.add('selected');
					this.classList.remove('fa-plus');
					this.classList.add('fa-minus');
					card.classList.add('selected');
					additionalToppingsText.textContent += (', ' + card.querySelector('.card-title').textContent);
							}
							selectedToppingsInput.value = selectedToppings.join(',');
						}
						updateTotalPrice();
					});
	});

	let multiplier = 1;
	const toppingCards = document.querySelectorAll('.topping-card');
	const sizeInputs = document.querySelectorAll('.pizza-size-input');
	sizeInputs.forEach(input => {
		input.addEventListener('change', function() {
			const selectedSize = this.value;
			const card = this.closest('.card');

			multiplier = 1;
			if (selectedSize === '35') {
				multiplier = 1.1;
			} else if (selectedSize === '40') {
				multiplier = 1.3;
			}
			card.querySelector('.selected-size').value = selectedSize;
			const image = card.querySelector('.card-img-top');
			if (selectedSize === '35') {
				image.style.transform = 'scale(1)';
			} else if (selectedSize === '40') {
				image.style.transform = 'scale(1.02)';
			} else {
				image.style.transform = 'scale(0.98)';
			}

			toppingCards.forEach(toppingCard => {
				const toppingPriceElement = toppingCard.querySelector('.topping-price');
				const toppingPrice = parseFloat(toppingPriceElement.getAttribute('data-base-price'));
				const newToppingPrice = toppingPrice * multiplier;
				toppingPriceElement.textContent = `€${newToppingPrice.toFixed(2)}`;
			});
			updateTotalPrice();
		});
	});
});