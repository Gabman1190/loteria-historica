# Lotería Histórica v0.4 — actualización de Render

Esta actualización conserva la sala multijugador y agrega QR, sala de espera visual, ingreso tardío, pausa/reanudación y modo proyección.

## Cómo actualizar el repositorio GitHub existente

1. En GitHub, abre tu repositorio `loteria-historica`.
2. Usa **Add file → Upload files**.
3. Descomprime el ZIP v0.4 y sube el **contenido** de la carpeta `loteria_historica` (no el ZIP). Debes reemplazar los archivos existentes cuando GitHub lo permita; para archivos existentes, es más seguro editar directamente o usar GitHub Desktop. En GitHub web, Upload files suele permitir sobrescribir archivos con el mismo nombre al confirmar el commit.
4. Verifica que `server.py`, `requirements.txt`, `multijugador.html`, `render.yaml` y `concepts.json` queden en la raíz del repositorio.
5. Confirma los cambios mediante **Commit changes**.
6. Render normalmente despliega automáticamente el nuevo commit; abre el panel **Events** para comprobar el resultado.
7. Una vez que indique **Live**, actualiza la página con Ctrl+F5 y crea una **sala nueva**. No intentes conservar una partida anterior durante el despliegue.

## Pruebas sugeridas

- Crea sala, escanea el QR desde un celular, verifica que se rellene el código.
- Entra con dos equipos y empieza una ronda.
- Añade un tercer equipo cuando la ronda ya haya comenzado; debe entrar y esperar a la siguiente ronda para responder.
- Pausa la ronda y comprueba que el tiempo se detenga; reanuda.
- Activa modo proyección.

## Limitaciones

- La partida reside en memoria. Si Render reinicia el servidor, se pierde.
- Usa una sola instancia del servidor (`--workers 1`).
- No se ha validado todavía con ocho celulares físicos en una clase.
