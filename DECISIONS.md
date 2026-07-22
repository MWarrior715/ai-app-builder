# AI App Builder — Decisiones

## ¿Por qué Python puro y no LangGraph/LangChain?

LangGraph acelera en producción, pero aquí el objetivo es demostrar **comprensión de orquestación**, no uso de framework de caja. Python puro + Protocol hace visible cada paso: qué agente corre, qué recibe, qué devuelve. Además, mantiene el stack coherente con PoC 01 y PoC 03.

## ¿Por qué agentes secuenciales?

Porque la narrativa del demo es: "una idea atraviesa una cadena de especialistas". La secuencia (Arquitecto → Backend → Frontend → QA → DevOps) es intuitiva para un CTO y permite mostrar logs claros. Paralelismo queda para el PoC 05 (AI Operations Center).

## ¿Por qué no se ejecuta el código generado?

El producto es el **orquestador**, no el compilador. Hacer que el código generado siempre compile implicaría un scope mucho mayor (sandboxing, reintentos, test runner). Se deja explícito en README y ROADMAP.

## ¿Por qué `LLMProvider` con `OpenAICompatibleLLM`?

Mago-compliance y flexibilidad. El mismo repo corre con cualquier motor que exponga `/v1/chat/completions`: local, cloud, on-prem. No hay `import ollama` ni nombres de modelo específicos en el código fuente.

## ¿Por qué el delimitador `---FILE: path---`?

Para que un agente genere múltiples archivos en una sola llamada al LLM. Es parseable sin regex compleja y robusto frente a fences markdown.

## Stack default y alternativas

Por defecto el Arquitecto elige stack automáticamente. Para demos controladas se ofrecen presets:
- `fastapi-react`
- `flask-vanilla`
- `auto`

En el futuro se pueden extender a Next.js, Express, etc.
