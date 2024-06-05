Esto es un pequeño proyecto para probar Google OR Tools.

OR Tools es una librería de Google para resolver problemas de optimización.
En este caso vamos a centrarnos en un problema de optimización de recursos con restricciones.

En este tipo de problemas el programador es responsable de:

- Crear las variables de decisión
- Agregar restricciones
- Definir la función objetivo
- Configurar y ejecutar el solucionador

Queremos conseguir una asignación de turnos para enfermeras de un hospital.
Las variables que utilizaremos son:

- Turnos de trabajo
- Enfermeras
- Días de la semana

Las restricciones que tendremos en cuenta son:

- Cada día se divide en 3 turnos: Mañana, Tarde y Noche.
- Cada día, cada turno se asigna a una enfermera distinta.
- Cada enfermera trabaja como mínimo 2 turnos cada 3 días.

El objetivo será:

- Repartir los turnos de trabajo de forma equitativa entre las enfermeras. En caso de que no sea posible algunas
  enfermeras trabajarán un turno más.

En el código de nurses_scheduling_1.py se puede ver la implementación de este problema teniendo 4 enfermeras, 3 turnos y
3 días.

Es crucial el rol que juegan las restricciones en este tipo de problemas. En el código de nurses_sheduling_2.py se suma
a las restricciones anteriores una nueva:

- Tenemos un total de 20 peticiones de turnos de trabajo y queremos que se cumpla el mayor número posible de ellas. En
  este caso el objetivo deja de ser el reparto equitativo y pasa a ser el cumplimiento del máximo de peticiones posible.

Debemos tener en cuenta que en este tipo de problemas se suele atacar a una única función objetivo, que es la que
trataremos de maximizar o minimizar.
Por lo general será bueno poner un límite a las soluciones que queremos que nos devuelva, ya que el número total de
soluciones podría ser muy grande.
Es importante también calcular el tiempo que tarda en ejecutarse la operación, porque en operaciones más costosas nos
ayudará a buscar la solución más óptima.

En el script nurses_scheduling_3.py vamos a complicar un poco más la operación y le vamos a pedir que tenga en cuenta
las preferencias personales de las enfermeras a la hora de asignar compañeras en los turnos. Las restricciones serán:

- Tenemos un total de 6 enfermeras.
- Calcularemos el horario de un mes(30 días).~~~~
- Cada enfermera tendrá 3 días de vacaciones.
- Cada día tendrá 3 turnos: Mañana, Tarde y Noche.
- Cada enfermera trabajará como mínimo 2 turnos cada 3 días y no podrá trabajar más de un turno por día.
- En cada turno trabajarán 2 enfermeras.
- Cada enfermera tendrá una lista de preferencias de acompañamiento donde ordenará el nombre de sus compañeras de mayor
  afinidad a menor afinidad.

El objetivo será maximizar la afinidad entre las compañeras asignadas a cada turno. 



