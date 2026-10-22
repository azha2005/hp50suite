# Borradores para difusión

Pendientes de publicación en las comunidades. Descarga:
https://github.com/azha2005/hp50suite/releases/latest/download/hp50suite.zip
No hay testimonios ni adopción externa verificada
documentados en este archivo.

## Para compañeros

Estoy desarrollando hp50suite: programas gratuitos y de código abierto para
HP 50g con ejercicios de Laboratorio de Datos, Micro I y Matemática I de
Economía en la UNLP. Muestran pasos y resultados intermedios. Busco gente con
una 50g que quiera probar un ejercicio y contar si funcionó, cómo lo cargó y
qué problema encontró. No hace falta programar. Hay una guía de primera prueba
y ejemplos: https://github.com/azha2005/hp50suite

## For HP calculator communities / archive submission

Title: hp50suite — open source UserRPL statistics, economics and calculus for HP 50g

I maintain hp50suite, an MIT-licensed collection of UserRPL programs for HP 50g,
written around undergraduate economics coursework at FCE-UNLP, Argentina.
It shows intermediate results through forms and message boxes. Calculation
cores are separated from the interfaces and have test tables for Emu48 with
an HP 50g ROM. Real hardware coverage varies by program and is documented;
emulator results are not presented as hardware validation.

The repository includes compact Conn4x packages, a Spanish/English first-run
guide, Spanish worked examples and the test harness. No ROM or emulator is
included in the distribution. I would appreciate tests from HP 50g owners:
model, package version, inputs, expected/actual result and any transfer issues.
Successful tests are useful too. Source and documentation:
https://github.com/azha2005/hp50suite

## Demo de un minuto, pendiente de grabar en hardware

1. Mostrar la 50g y el directorio LAB en VAR.
2. Abrir DSTATS e ingresar `{ 2 4 6 8 10 }`.
3. Mostrar las tres cajas: media 6; varianza muestral 10 y desvío
   3.16227766; CV 52.70462767 %. No ocultar errores si aparecen.
4. Terminar con el enlace al proyecto y la invitación a reportar una prueba.

No presentar una captura de emulador como si fuera la calculadora física.

## Evidencia a reunir

- Una release identificable, su ZIP y hashes, y la ejecución pública de CI.
- Video o fotos del ejemplo, indicando versión y hardware.
- Issues de usuarios externos con pruebas reproducibles, si llegan.
- Correcciones enlazadas a esos reportes y resultados de las baterías con ROM.

La CI comprueba formato y empaquetado. Las baterías con ROM se corren
por separado siguiendo `harness/README.md`; no se afirma que corran en Actions.
Con evidencia nueva se puede redactar una actualización factual de la solicitud
si existe un canal habilitado para ello. No se puede inferir una probabilidad
de aprobación a partir de estas mejoras.
