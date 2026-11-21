# Lotería Histórica · Multijugador (versión 0.2)

## Iniciar en el computador

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

Abrir `http://localhost:8000` para crear la sala. Para conectarse desde celulares en la misma red Wi-Fi, usar `http://IP-DEL-COMPUTADOR:8000` (el firewall debe permitir el puerto 8000).

## Publicación en internet

Subir la carpeta a un servicio que ejecute procesos Python ASGI y soporte WebSockets (por ejemplo, Render). Comando de instalación: `pip install -r requirements.txt`; comando de inicio: `uvicorn server:app --host 0.0.0.0 --port $PORT`. No es una página estática: **no funciona en GitHub Pages o en un alojamiento estático sin backend**.

## Características

- 8 equipos y un celular por equipo, cada uno con un tablero diferente de 12 conceptos.
- 48 conceptos, dos pistas por concepto.
- Profesor inicia manualmente las rondas; cierre automático tras 30 segundos o primer acierto.
- Error: bloqueo de 5 segundos; el servidor decide el ganador bajo bloqueo de exclusión mutua.
- 35 rondas como máximo, clasificación y empate explícito.
- Reconexión con credencial almacenada en el navegador.

## Limitaciones importantes de esta versión

- Las salas y puntuaciones se guardan **solo en memoria**. Reiniciar o suspender el servidor elimina las partidas.
- Para mantener el estado compartido, desplegar **una sola instancia/proceso** del servidor; no escalar a múltiples réplicas sin introducir almacenamiento compartido.
- No se incluye aún un sistema de cuentas, panel de edición de preguntas, exportación de resultados ni QR visual (sí enlace y código).
- La latencia de red puede afectar el orden de llegada: la adjudicación usa el orden de procesamiento en el servidor.
- El sistema permite empates al finalizar las 35 rondas; el desempate queda a cargo del docente.
- Se recomienda probar con ocho celulares antes de utilizarlo con estudiantes.
