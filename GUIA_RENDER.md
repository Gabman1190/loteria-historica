# Publicar Lotería Histórica en Render

1. Crea un repositorio nuevo en GitHub (puede ser privado).
2. Sube **los archivos del interior** de esta carpeta a la raíz del repositorio: `server.py`, `multijugador.html`, `concepts.json`, `requirements.txt`, `render.yaml` y `.python-version`.
3. En https://dashboard.render.com/ selecciona **New > Blueprint** y conecta tu repositorio de GitHub.
4. Render leerá `render.yaml`. Revisa la configuración y confirma la creación del servicio. Si el plan gratuito no está disponible en tu cuenta, revisa el costo antes de aceptar.
5. Espera a que el despliegue termine y visita la URL `https://...onrender.com` asignada por Render. Verifica `/health`.
6. En el computador del profesor, pulsa **Crear sala**. En los celulares, abre el enlace de sala y escribe un nombre de equipo.

## Advertencias

- Las salas viven **solo en memoria**: un reinicio, suspensión o nuevo despliegue borra la partida.
- La instancia gratuita puede suspenderse por inactividad, lo que provoca una espera al volver a entrar. Abre la página antes de la clase.
- Usa **un solo proceso y una sola instancia**. No actives escalado horizontal.
- No se ha probado con ocho teléfonos reales; haz una partida de ensayo antes de usarla en clase.
- Si el docente o alumnos se desconectan, recarga la página para recuperar la sesión mientras el servidor no haya reiniciado.
- El servidor adjudica por orden de procesamiento de mensajes, no compensa diferencias de latencia entre redes.
- Evita compartir el enlace de profesor o su navegador con los alumnos; la sesión docente se guarda localmente.
