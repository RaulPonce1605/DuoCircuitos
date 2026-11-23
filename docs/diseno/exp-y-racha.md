# Diseño: EXP, precisión y racha

Decisiones de la fase 1. El backend es la fuente de verdad (CLAUDE.md 5.4) y **todas las cifras** viven en la configuración del backend (`app/core/config.py`), no en el código de los servicios ni en la app.

## 1. Cómo avanza una lección

1. Al iniciar la lección, el backend crea una **sesión** con una instancia de cada ejercicio, en el orden del temario.
2. Si el alumno responde mal, ve la explicación y la respuesta correcta, y el ejercicio **vuelve al final de la cola**. Los numéricos vuelven con valores nuevos.
3. La lección termina cuando todos los ejercicios se respondieron bien al menos una vez.
4. Si el alumno abandona, la sesión queda incompleta y **no da EXP ni cuenta para la racha**.

## 2. EXP

Se calcula **una sola vez**, al terminar la lección:

| Concepto | Valor por defecto | Variable |
|---|---|---|
| Ejercicio correcto al primer intento | 10 EXP | `XP_PER_EXERCISE_FIRST_TRY` |
| Ejercicio correcto después de fallarlo | 5 EXP | `XP_PER_EXERCISE_RETRY` |
| Bono por lección perfecta (100 % de precisión) | 5 EXP | `XP_PERFECT_LESSON_BONUS` |

- Cada ejercicio cuenta una vez, aunque se haya fallado varias veces antes de acertarlo.
- Ejemplo: una lección de 5 ejercicios con 4 aciertos al primer intento da 4 · 10 + 1 · 5 = **45 EXP**. Con los 5 al primer intento: 5 · 10 + 5 = **55 EXP**.
- Repetir una lección ya completada da EXP con las mismas reglas. Si en la fase 3 (ligas) se vuelve un problema de "granjear" EXP, se agrega un factor de repetición.
- Cada vez que se gana EXP se guarda un **evento** (usuario, cantidad, origen, fecha). Las ligas y los desafíos de las fases 2 y 3 suman esos eventos por periodo.

## 3. Precisión

`precisión = ejercicios correctos al primer intento / ejercicios de la lección`, en porcentaje entero redondeado. Una lección de 5 ejercicios con 4 al primer intento tiene 80 %.

## 4. Racha

- **Día = día calendario en la zona horaria del alumno.** La app manda su zona horaria IANA (`America/Mexico_City`) al registrarse y el backend la guarda. Sin zona válida se usa `UTC`.
- Al **terminar** una lección en el día local `D`:
  - si la última racha registrada es de `D`, no cambia;
  - si es de `D − 1`, la racha sube 1;
  - en cualquier otro caso (o si no había racha), la racha vuelve a 1.
- La **racha más larga** se actualiza cuando la actual la supera.
- **La racha se rompe sola**: no hay tareas programadas. Al leer el perfil, si el último día con lección es anterior a ayer (día local), la racha mostrada es 0.
- Cambiar de zona horaria se permite. En el día del cambio, la racha se evalúa con la zona nueva. Puede ganar o perder un día en casos raros, y se acepta.
- Protector de racha: fase 3 (tienda).

## 5. Fuera de la fase 1

Energía, desafíos, ligas, cofres y logros (fases 2 y 3). Este documento se actualiza cuando lleguen.
