from ortools.sat.python import cp_model


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
        self.print_shifts()

        if self._solution_count >= self._solution_limit:
            print(f"Detener la búsqueda después de {self._solution_limit} soluciones")
            self.stop_search()


    def solutionCount(self):
        return self._solution_count


    def print_shifts(self):
        for n in range(self._num_nurses):
            for d in range(self._num_days):
                for s in range(self._num_shifts):
                    if self.Value(self._shifts[(n, d, s)]):
                      print(f"La enfermera {n} trabaja en el turno {s} el día {d}")


def main() -> None:
    # Datos.
    num_nurses = 6
    num_shifts = 3
    num_shifts_per_nurse_per_day = 1
    num_nurses_per_shift = 2
    num_days = 30

    all_nurses = range(num_nurses)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    # Almacenar el turno trabajado en el último día del mes anterior.
    previous_last_day_shifts = {n: None for n in all_nurses}

    for month in range(5):
        print(f"Mes: {month}")
        # Crea el modelo.
        model = cp_model.CpModel()

        # Crea las variables de turno.
        # shifts[(n, d, s)]: la enfermera 'n' trabaja en el turno 's' el día 'd'.
        shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    shifts[(n, d, s)] = model.new_bool_var(f"turno_n{n}_d{d}_s{s}")

        # No puede trabajar más de un turno por día.
        for n in all_nurses:
            for d in all_days:
                model.add(sum(shifts[(n, d, s)] for s in all_shifts) <= num_shifts_per_nurse_per_day)

        # En cada turno trabajarán 2 enfermeras.
        for d in all_days:
            for s in all_shifts:
                model.add(sum(shifts[(n, d, s)] for n in all_nurses) == num_nurses_per_shift)

        # Si una enfermera trabaja el último día del mes en un turno, no puede trabajar en el mismo turno el primer día del mes siguiente.
        if month > 0:  # No aplicamos esta restricción en el primer mes.
            for n in all_nurses:
                if previous_last_day_shifts[n] is not None:
                    model.add(shifts[(n, 0, previous_last_day_shifts[n])] == 0)

        # Maximiza la rotación.
        model.Maximize(sum(shifts.values()))

        # Resuelve el modelo.
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Si se encontró una solución, almacena el turno trabajado en el último día del mes para la próxima iteración.
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for n in all_nurses:
                for s in all_shifts:
                    if solver.Value(shifts[(n, num_days - 1, s)]):
                        previous_last_day_shifts[n] = s

        # Imprime las soluciones.
        solution_printer = ImpresoraDeSolucionesParcialesDeEnfermeras(shifts, num_nurses, num_days, num_shifts, 1)
        solver.Solve(model, solution_printer)

        # Estadísticas.
        print(f"\nEstadísticas del mes: {month}")
        print(f"  - conflictos      : {solver.num_conflicts}")
        print(f"  - ramificaciones  : {solver.num_branches}")
        print(f"  - tiempo de pared : {solver.wall_time} s")
        print(f"  - soluciones encontradas: {solution_printer.solutionCount()}")


if __name__ == "__main__":
    main()
