from ortools.sat.python import cp_model


def main() -> None:
    # Datos.
    num_nurses = 6
    num_shifts = 3
    num_shifts_per_nurse_per_day = 1
    num_nurses_per_shift = 2
    num_days = 30
    vacation_days_per_nurse = 3
    min_shifts_per_nurse_per_three_days = 2
    affinity_lists = [[7, 2, 8, 9, 6, 4, 5, 3, 1], [8, 5, 0, 3, 2, 4, 6, 9, 7], [1, 3, 9, 5, 7, 6, 8, 0, 4],
                      [2, 5, 4, 1, 0, 8, 6, 7, 9], [5, 0, 7, 3, 1, 8, 9, 6, 2], [4, 6, 3, 8, 7, 0, 1, 2, 9]]

    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    all_vacation_days = range(vacation_days_per_nurse)
    all_shifts_per_three_days = range(num_shifts * 3)

    # Crea el modelo.
    model = cp_model.CpModel()

    # Crea las variables de turno.
    # shifts[(n, d, s)]: la enfermera 'n' trabaja en el turno 's' el día 'd'.
    shifts = {}
    for n in all_nurses:
        for d in all_days:
            for s in all_shifts:
                shifts[(n, d, s)] = model.new_bool_var(f"turno_n{n}_d{d}_s{s}")

    # Crea las variables de vacaciones.
    # vacations[(n, v)]: la enfermera 'n' está de vacaciones el día 'v'.
    vacations = {}
    for n in all_nurses:
        for v in all_vacation_days:
            vacations[(n, v)] = model.new_bool_var(f"vacaciones_n{n}_v{v}")

    # Crea las variables de afinidad.
    # affinities[(n1, n2)]: la afinidad entre la enfermera 'n1' y la enfermera 'n2'.
    affinities = {}
    for n1 in all_nurses:
        for n2 in all_nurses:
            if n1 != n2:  # Una enfermera no puede tener afinidad consigo misma.
                # Calcula la afinidad total como la suma de las posiciones en las que
                # cada enfermera ha colocado a la otra en su lista de afinidad.
                total_affinity = affinity_lists[n1].index(n2) + affinity_lists[n2].index(n1)
                affinities[(n1, n2)] = model.new_int_var(0, total_affinity, f"afinidad_n{n1}_n{n2}")

    # Cada enfermera tiene 30 días de vacaciones.
    for n in all_nurses:
        model.add(sum(vacations[(n, v)] for v in all_vacation_days) == vacation_days_per_nurse)

    # Cada enfermera trabaja como mínimo 2 turnos cada 3 días.
    for n in all_nurses:
        for d in range(num_days - 2):  # Restamos 2 para evitar salirnos del rango de días.
            model.add(
                sum(shifts[(n, d + i, s)] for i in range(3) for s in all_shifts) >= min_shifts_per_nurse_per_three_days)

    # No puede trabajar más de un turno por día.
    for n in all_nurses:
        for d in all_days:
            model.add(sum(shifts[(n, d, s)] for s in all_shifts) <= num_shifts_per_nurse_per_day)

    # En cada turno trabajarán 2 enfermeras.
    for d in all_days:
        for s in all_shifts:
            model.add(sum(shifts[(n, d, s)] for n in all_nurses) == num_nurses_per_shift)

    # Cada enfermera tendrá una lista de preferencias de acompañamiento donde ordenará el nombre de sus compañeras de
    # mayor afinidad a menor afinidad. Para esta restricción, necesitamos definir una función objetivo que maximice
    # la afinidad total entre las enfermeras que trabajan juntas en el mismo turno. Primero, calculamos la afinidad
    # total para cada turno.
    total_affinity = {}
    for d in all_days:
        for s in all_shifts:
            for n1 in all_nurses:
                for n2 in all_nurses:
                    if n1 != n2:  # Una enfermera no puede tener afinidad consigo misma.
                        # Crea una nueva variable para el producto de las variables de turno y de afinidad.
                        total_affinity[(n1, n2, d, s)] = model.new_int_var(0, num_nurses * num_days * num_shifts,
                                                                           f"total_affinity_n{n1}_n{n2}_d{d}_s{s}")
                        # Define la nueva variable como el producto de las variables de turno y de afinidad.
                        model.AddMultiplicationEquality(total_affinity[(n1, n2, d, s)],
                                                        [shifts[(n1, d, s)], shifts[(n2, d, s)], affinities[(n1, n2)]])

    # Maximiza la afinidad total.
    model.maximize(sum(total_affinity.values()))

    # Crea el solucionador y resuelve.
    solver = cp_model.CpSolver()
    solver.parameters.linearization_level = 0
    # Enumera todas las soluciones.
    solver.parameters.enumerate_all_solutions = True

    class ImpresoraDeSolucionesParcialesDeEnfermeras(cp_model.CpSolverSolutionCallback):
        """Imprime soluciones intermedias."""

        def __init__(self, shifts, affinities, num_nurses, num_days, num_shifts, limit):

            cp_model.CpSolverSolutionCallback.__init__(self)
            self._shifts = shifts
            self._affinities = affinities
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
                        if self.Value(self._shifts[(n, d, s)]):
                            is_working = True
                            print(f"  Enfermera {n} trabaja en el turno {s}")
                            for n2 in range(self._num_nurses):
                                if n != n2 and self.Value(self._shifts[(n2, d, s)]):
                                    print(f"  Afinidad con enfermera {n2}: {self.Value(self._affinities[(n, n2)])}")
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
        shifts, affinities, num_nurses, num_days, num_shifts, solution_limit
    )

    solver.solve(model, solution_printer)

    # Estadísticas.
    print("\nEstadísticas")
    print(f"  - conflictos      : {solver.num_conflicts}")
    print(f"  - ramificaciones  : {solver.num_branches}")
    print(f"  - tiempo de pared : {solver.wall_time} s")
    print(f"  - soluciones encontradas: {solution_printer.solutionCount()}")


if __name__ == "__main__":
    main()
