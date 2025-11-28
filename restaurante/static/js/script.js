// Confirmación simple y global para acciones de eliminación
// Busca elementos (botones/enlaces/forms) con el atributo `data-confirm`.
// Uso: añadir `data-confirm="¿Seguro que quieres eliminar ...?"` al <form> o al <button> o al <a>.

(function () {
	function getCookie(name) {
		const value = `; ${document.cookie}`;
		const parts = value.split(`; ${name}=`);
		if (parts.length === 2) return parts.pop().split(';').shift();
	}
	const csrftoken = getCookie('csrftoken');

	function findClosestForm(el) { return el.closest('form'); }

	// Maneja clicks en elementos con data-confirm
	document.addEventListener('click', function (ev) {
		const el = ev.target.closest('[data-confirm]');
		if (!el) return;
		ev.preventDefault();

		const msg = el.getAttribute('data-confirm') || '¿Estás seguro que quieres eliminar este elemento?';

		// Usar el confirm() nativo
		if (!window.confirm(msg)) return; // si cancela, no hacer nada

		// Si el elemento está dentro de un form y es un botón de submit -> enviar
		const form = findClosestForm(el);
		if (form && (el.tagName === 'BUTTON' || el.getAttribute('type') === 'submit')) {
			form.submit();
			return;
		}

		// Si el elemento indica data-ajax="true" -> hacer fetch
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

		// Si es un enlace normal, navegar
		const href = el.getAttribute('href');
		if (href) { window.location.href = href; return; }

		// Fallback: si está dentro de un form, enviarlo
		if (form) { form.submit(); return; }
	}, false);

	// Maneja envío de formulario por Enter o submit directo si el form tiene data-confirm
	document.addEventListener('submit', function (ev) {
		const form = ev.target;
		if (!form || !form.hasAttribute('data-confirm')) return;
		const msg = form.getAttribute('data-confirm') || '¿Estás seguro que quieres eliminar este elemento?';
		if (!window.confirm(msg)) {
			ev.preventDefault();
		}
		// si confirma, dejamos que el formulario se envíe normalmente
	}, true);

})();

// Función global mínima para confirmación (estilo: confirmarBorrado())
// Uso en HTML: <button type="submit" onclick="return confirmarBorrado(this)">Borrar</button>
function confirmarBorrado(el, mensaje) {
	mensaje = mensaje || '¿Estás seguro de que quieres borrar este elemento?';
	const respuesta = confirm(mensaje);
	if (respuesta) {
		// comportamiento por defecto: si se llama desde un botón dentro de un formulario
		// y el botón es de tipo submit, devolver true permite que el formulario se envíe.
		return true;
	} else {
		// si cancela, devolver false evita el submit cuando se usa "return confirmarBorrado(this)"
		return false;
	}
}
