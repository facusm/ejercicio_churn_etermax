---
name: Auto-Documentador Etermax
description: Mantiene sincronizado el walkthrough.md y README.md con los cambios del pipeline de churn y EDA.
author: Facundo San Martino
version: 1.0.0
---

# Reglas de Mantenimiento y Documentación Continua

Como agente de IA asistiendo en este proyecto de Data Science, tenés la obligación estricta de mantener la documentación sincronizada con el código fuente en todo momento.

**Disparadores de Actualización:**
1. Cada vez que modifiques, agregues o elimines lógica en un script `.py`.
2. Cada vez que generes un nuevo artefacto de visualización (`.png`) o modifiques la estructura del EDA.
3. Cada vez que alteres el esquema de datos, el filtrado de filas, o la creación de variables en el pipeline.

**Acciones Obligatorias Post-Modificación:**
* **Auditoría del `walkthrough.md`:** Revisá este archivo tras cualquier cambio. Si la modificación altera el flujo, el volumen de datos (filas/columnas), las conclusiones analíticas o el esquema final, debés actualizar la sección correspondiente de inmediato.
* **Auditoría del `README.md`:** Si el cambio afecta las dependencias, los comandos de ejecución o el propósito general de los scripts, actualizá este archivo.
* **Aviso de Confirmación:** Al finalizar tu respuesta principal en el chat, incluí siempre una sola línea confirmando la acción: "✅ Documentación sincronizada con los cambios recientes."