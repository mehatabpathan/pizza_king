let toasts = document.getElementsByClassName('custom-toast');
if(toasts) {
    toasts = Array.from(toasts);
    toasts.forEach(toast => {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
    });
}

const deleteModal = document.querySelector('#delete-modal');

function createModalHTML(url, txt) {
    return `
  <div class="modal-dialog modal-dialog-centered" style="z-index: 99999">
    <div class="modal-content">

      <div class="modal-header">
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>

      <div class="modal-body h3 text-center">
        Are you sure you want to delete ${txt}?
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-outline-custom" data-bs-dismiss="modal">Cancel</button>
        <a class="btn bg-red light-color" href="${url}">Confirm</a>
      </div>

    </div>
  </div>
`;
}

function confirmDelete(url, txt) {
  deleteModal.innerHTML = createModalHTML(url, txt);
  const myModal = new bootstrap.Modal(deleteModal);
  myModal.show();
}

document.body.addEventListener('click', (e) => {
    if(e.target.classList.contains('confirm-delete')) {
      confirmDelete(e.target.dataset.url, e.target.dataset.txt);
    }
});