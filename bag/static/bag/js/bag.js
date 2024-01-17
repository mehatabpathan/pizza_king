function handleEnableDisable(id) {
	const inputElement = document.getElementById('id_qty_' + id);
	if (inputElement) {
		const currentValue = parseInt(inputElement.value);
		const minusDisabled = currentValue < 2;
		const plusDisabled = currentValue > 14;
		const decrementButton = document.getElementById('decrement-qty_' + id);
		const incrementButton = document.getElementById('increment-qty_' + id);
		decrementButton.disabled = minusDisabled;
		incrementButton.disabled = plusDisabled;
	} 
}

function debounce(func, delay) {
	let timeoutId;
	return function (...args) {
	  clearTimeout(timeoutId);
	  timeoutId = setTimeout(() => {
		func(...args);
	  }, delay);
	};
  }

document.addEventListener('DOMContentLoaded', () => {
	document.querySelectorAll('.qty_input').forEach(input => {
		const id = input.dataset.id;
		handleEnableDisable(id);

		input.addEventListener('change', function() {
			const id = this.dataset.id;
			handleEnableDisable(id);
		});
	});

	const submitFormDebounced = debounce((form) => {
		form.submit();
	  }, 1000);

	document.querySelectorAll('.increment-qty').forEach(btn => {
		btn.addEventListener('click', function(e) {
			e.preventDefault();
			const id = this.dataset.id;
			const closestInput = this.closest('.input-group').querySelector('.qty_input');
			const form = closestInput.parentNode.parentNode;
			if (closestInput) {
				let currentValue = parseInt(closestInput.value);
				closestInput.value = currentValue + 1;
				handleEnableDisable(id);
				submitFormDebounced(form);
			}
		});
	});

	document.querySelectorAll('.decrement-qty').forEach(btn => {
		btn.addEventListener('click', function(e) {
			e.preventDefault();
			const id = this.dataset.id;
			const closestInput = this.closest('.input-group').querySelector('.qty_input');
			const form = closestInput.parentNode.parentNode;
			if (closestInput) {
				let currentValue = parseInt(closestInput.value);
				closestInput.value = currentValue - 1;
				handleEnableDisable(id);
				submitFormDebounced(form);
			}
		});
	});
});