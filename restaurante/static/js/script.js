(function () {
	function getCookie(name) {
		const value = `; ${document.cookie}`;
		const parts = value.split(`; ${name}=`);
		if (parts.length === 2) return parts.pop().split(';').shift();
	}
	const csrftoken = getCookie('csrftoken');

	function findClosestForm(el) { return el.closest('form'); }

	document.addEventListener('click', function (ev) {
		const el = ev.target.closest('[data-confirm]');
		if (!el) return;
		ev.preventDefault();

		const msg = el.getAttribute('data-confirm') || '¿Estás seguro que quieres eliminar este elemento?';

		if (!window.confirm(msg)) return;

		const form = findClosestForm(el);
		if (form && (el.tagName === 'BUTTON' || el.getAttribute('type') === 'submit')) {
			form.submit();
			return;
		}

		if (el.getAttribute('data-ajax') === 'true') {
			const url = el.getAttribute('href') || el.getAttribute('data-url');
			const method = (el.getAttribute('data-method') || 'DELETE').toUpperCase();
			(async function () {
				try {
					const headers = {};
					if (csrftoken) headers['X-CSRFToken'] = csrftoken;
					const resp = await fetch(url, { method: method, headers: headers, credentials: 'same-origin' });
					if (resp.ok) {
						window.location.reload();
					} else {
						alert('No se pudo completar la eliminación. Código: ' + resp.status);
					}
				} catch (err) {
					console.error(err);
					alert('Ocurrió un error al eliminar. Revisa la consola.');
				}
			})();
			return;
		}

		const href = el.getAttribute('href');
		if (href) { window.location.href = href; return; }

		if (form) { form.submit(); return; }
	}, false);

	document.addEventListener('submit', function (ev) {
		const form = ev.target;
		if (!form || !form.hasAttribute('data-confirm')) return;
		const msg = form.getAttribute('data-confirm') || '¿Estás seguro que quieres eliminar este elemento?';
		if (!window.confirm(msg)) {
			ev.preventDefault();
		}
	}, true);

})();

function confirmarBorrado(el, mensaje) {
	mensaje = mensaje || '¿Estás seguro de que quieres borrar este elemento?';
	return confirm(mensaje);
}
