# AI App Builder — ROADMAP

## V0.1.0 (actual)
- [x] Orquestador secuencial con 5 agentes.
- [x] CLI + FastAPI.
- [x] Motor LLM enchufable (OpenAI-compatible).
- [x] Tests con LLM falso.
- [x] README, ARCHITECTURE, DECISIONS, CHANGELOG, LICENSE.

## V0.2.0 — Refinamiento interactivo
- [ ] Agente de refinamiento: permite preguntar al usuario por requisitos faltantes.
- [ ] Loop de corrección QA → Backend/Frontend cuando el score es bajo.
- [ ] Validación de JSON de spec con retry automático.

## V0.3.0 — Ejecución y verificación
- [ ] Ejecutar `pytest` sobre los tests generados.
- [ ] Intentar levantar backend generado y capturar errores.
- [ ] Reintentos automáticos limitados ante errores de sintaxis.

## V0.4.0 — UI web
- [ ] Streamlit o React para mostrar el flujo de agentes en tiempo real.
- [ ] Drag-and-drop de especificaciones y descarga del proyecto generado.

## Futuro
- [ ] Integración con PoC 05 (AI Operations Center) para monitorear el orquestador en vivo.
