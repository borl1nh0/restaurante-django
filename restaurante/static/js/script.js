// Global JS: intercepta clicks en enlaces de eliminación y muestra confirm() antes de hacer POST.
console.log("JS Cargado!");

function getCookie(name) {
	const value = `; ${document.cookie}`;
	const parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop().split(';').shift();
}

document.addEventListener('click', function (e) {
	// buscar el enlace más cercano
	const a = e.target.closest && e.target.closest('a');
	if (!a) return;

	const href = a.getAttribute('href') || '';

	// condición para considerar que es un enlace de eliminar
	// aquí usamos '/eliminar/' porque las plantillas usan esa ruta; si usas otra, ajusta
	if (href.includes('/eliminar/') || a.dataset.confirm !== undefined || a.classList.contains('js-confirm-delete')) {
		e.preventDefault();
		e.stopPropagation();

		// mensaje personalizado si existe data-confirm, si no uno por defecto
		const mensaje = a.dataset.confirm || `¿Seguro que deseas eliminar este elemento?`;
		if (!confirm(mensaje)) return;

		// Enviar POST a la URL usando fetch con CSRF
		const csrftoken = getCookie('csrftoken');

		fetch(href, {
			method: 'POST',
			credentials: 'same-origin',
			headers: {
				'X-CSRFToken': csrftoken,
				'X-Requested-With': 'XMLHttpRequest'
			}
		}).then(function (resp) {
			if (resp.ok) {
				// recargar la página para reflejar el cambio
				location.reload();
			} else if (resp.status === 302) {
				// si hubo redirección, recargar también
				location.reload();
			} else {
				resp.text().then(function (t) { alert('Error al eliminar: ' + resp.status + '\n' + t); });
			}
		}).catch(function (err) {
			alert('Error en la petición de eliminación: ' + err);
		});
	}
});
