from ortools.sat.python import cp_model

def main() -> None:
    # Datos.
    num_nurses = 4
    num_shifts = 3
    num_days = 3
    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    # Crea el modelo.
    model = cp_model.CpModel()

    # Crea las variables de turno.
    # shifts[(n, d, s)]: la enfermera 'n' trabaja en el turno 's' el día 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.new_bool_var(f"turno_n{n}_d{d}_s{s}")

    # Cada turno se asigna exactamente a una enfermera en el período de programación.
    for d in all_days:
        for s in all_shifts:
            model.add_exactly_one(shifts[(n, d, s)] for n in all_nurses)

    # Cada enfermera trabaja como máximo un turno por día.
    for n in all_nurses:
        for d in all_days:
            model.add_at_most_one(shifts[(n, d, s)] for s in all_shifts)

    # Intenta distribuir los turnos de manera uniforme, de modo que cada enfermera trabaje
    # min_turnos_por_enfermera turnos. Si esto no es posible, porque el total
    # número de turnos no es divisible por el número de enfermeras, algunas enfermeras serán
    # asignado un turno más.
    min_turnos_por_enfermera = (num_shifts * num_days) // num_nurses
    if num_shifts * num_days % num_nurses == 0:
        max_turnos_por_enfermera = min_turnos_por_enfermera
    else:
        max_turnos_por_enfermera = min_turnos_por_enfermera + 1
    for n in all_nurses:
        turnos_trabajados = []
        for d in all_days:
            for s in all_shifts:
                turnos_trabajados.append(shifts[(n, d, s)])
        model.add(min_turnos_por_enfermera <= sum(turnos_trabajados))
        model.add(sum(turnos_trabajados) <= max_turnos_por_enfermera)

    # Crea el solucionador y resuelve.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    # Enumera todas las soluciones.
    solver.parameters.enumerate_all_solutions = True

    class ImpresoraDeSolucionesParcialesDeEnfermeras(cp_model.CpSolverSolutionCallback):
        """Imprime soluciones intermedias."""

        def __init__(self, shifts, num_nurses, num_days, num_shifts, limit):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._num_nurses = num_nurses
            self._num_days = num_days
            self._num_shifts = num_shifts
            self._solution_count = 0
            self._solution_limit = limit

        def on_solution_callback(self):
            self._solution_count += 1
            print(f"Solución {self._solution_count}")
            for d in range(self._num_days):
                print(f"Día {d}")
                for n in range(self._num_nurses):
                    is_working = False
                    for s in range(self._num_shifts):
                        if self.value(self._shifts[(n, d, s)]):
                            is_working = True
                            print(f"  Enfermera {n} trabaja en el turno {s}")
                    if not is_working:
                        print(f"  Enfermera {n} no trabaja")
            if self._solution_count >= self._solution_limit:
                print(f"Detener la búsqueda después de {self._solution_limit} soluciones")
                self.stop_search()

        def solutionCount(self):
            return self._solution_count

    # Muestra las primeras cinco soluciones.
    solution_limit = 5
    solution_printer = ImpresoraDeSolucionesParcialesDeEnfermeras(
        shifts, num_nurses, num_days, num_shifts, solution_limit
    )

    solver.solve(model, solution_printer)

    # Estadísticas.
    print("\nEstadísticas")
    print(f"  - conflictos      : {solver.num_conflicts}")
    print(f"  - ramificaciones  : {solver.num_branches}")
    print(f"  - tiempo de operación : {solver.wall_time} s")
    print(f"  - soluciones encontradas: {solution_printer.solutionCount()}")


if __name__ == "__main__":
    main()
