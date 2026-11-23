# contenido/: convenciones

> El dominio (producto, glosario, reglas globales) está en el CLAUDE.md raíz. **No lo repitas aquí**; este archivo solo contiene convenciones del temario.

El formato completo de los archivos (`camino.yaml` y lecciones) está en `README.md` de esta carpeta. Este archivo dice **cómo** escribir y revisar el contenido.

---

## 1. Estructura

```
contenido/
├── README.md                formato del temario
├── camino.yaml              ← crear  orden de etapas, secciones, unidades y nodos
└── unidades/
    └── u01-ley-de-ohm/      ← crear  una carpeta por unidad
        └── ohm-01.md        ← crear  una lección por archivo; nombre = id
```

## 2. Reglas

### 2.1 Una lección por archivo, `id` = nombre del archivo

- **Por qué:** el importador y el progreso de los usuarios se ligan al `id`; si cambia, se pierde el progreso.
- **Prohibido:** cambiar el `id` de una lección ya publicada en `main`; ids duplicados; mayúsculas, acentos o espacios en ids.
- **Correcto:** `unidades/u01-ley-de-ohm/ohm-01.md` con `id: ohm-01`.

### 2.2 El orden vive solo en `camino.yaml`

- **Por qué:** reordenar el camino no debe obligar a renombrar archivos.
- **Prohibido:** depender del nombre de carpeta o archivo para el orden; declarar en una lección en qué posición va.

### 2.3 Todo ejercicio lleva explicación y pistas

- **Por qué:** la explicación se muestra después de Comprobar, y el tutor solo puede usar las pistas y la teoría escritas aquí.
- Mínimo **2 pistas**, de la más general a la más concreta. **Ninguna pista contiene el resultado final.**
- **Prohibido:** ejercicios sin `explicacion`; pistas que digan la respuesta o la opción correcta.
- **Correcto:**
  ```yaml
  pistas:
    - "¿Qué ley relaciona voltaje, corriente y resistencia?"
    - "Despeja I de V = I · R."
  ```

### 2.4 Ejercicios numéricos: unidad, rangos y tolerancia siempre

- **Por qué:** el backend sortea los valores y valida con tolerancia; sin estos datos no puede generar ni validar.
- Los rangos deben producir resultados realistas (sin corrientes de 10⁶ A ni resistencias negativas).
- **Prohibido:** fórmulas sin `unidad`; `tolerancia` ausente o cero; variables en la fórmula que no estén en `parametros`; funciones fuera de la lista blanca de `README.md`.

### 2.5 Solo contenido propio y verificado

- **Por qué:** el tutor usa este texto como su única fuente; si hay un error aquí, el tutor lo repite.
- **Prohibido:** copiar texto de libros o sitios con derechos; usar contenido o ejercicios de las apps de referencia; publicar fórmulas sin revisarlas.
- Notación: SI, punto decimal, símbolos `Ω`, `µ`, `·`.

### 2.6 Teoría en el cuerpo de la lección

- **Por qué:** el cuerpo en Markdown (debajo del frontmatter) es la teoría que lee el tutor y que puede mostrarse como introducción.
- Breve: de 3 a 8 párrafos cortos, enfocados en los `conceptos` declarados.

---

## 3. Checklist: nueva lección de contenido

- [ ] Archivo en `unidades/<unidad>/<id>.md` con `id` igual al nombre.
- [ ] Frontmatter completo según `README.md`: `id`, `unidad`, `objetivos`, `conceptos`, `ejercicios`.
- [ ] Cada ejercicio con `tipo`, `enunciado`, `explicacion` y al menos 2 `pistas`.
- [ ] Numéricos: `parametros` con rangos, `solucion`, `unidad` y `tolerancia`.
- [ ] Resolví a mano al menos un caso con los valores mínimos y otro con los máximos.
- [ ] Ninguna pista revela el resultado.
- [ ] Teoría en el cuerpo que cubre todos los `conceptos`.
- [ ] Nodo agregado en `camino.yaml` en la posición correcta.
- [ ] El validador pasa: `cd backend && uv run python -m app.content_import.validate`.
- [ ] Commit `feat(contenido): ...` en una rama `feature/*` con PR.
