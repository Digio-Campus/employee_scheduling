from typing import Union

from ortools.sat.python import cp_model


def main() -> None:
    # Este programa intenta encontrar una asignación óptima de enfermeras a turnos
    # (3 turnos por día, durante 7 días), sujeto a algunas restricciones (ver abajo).
    # Cada enfermera puede solicitar ser asignada a turnos específicos.
    # La asignación óptima maximiza el número de solicitudes de turnos cumplidas.
    num_enfermeras = 5
    num_turnos = 3
    num_dias = 7
    todas_enfermeras = range(num_enfermeras)
    todos_turnos = range(num_turnos)
    todos_dias = range(num_dias)
    solicitudes_turnos = [
        [[0, 0, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 1]],
        [[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1]],
        [[0, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0], [0, 1, 0], [0, 0, 0]],
        [[0, 0, 1], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0]],
        [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0]],
    ]

    # Crea el modelo.
    model = cp_model.CpModel()

    # Crea las variables de turno.
    # turnos[(n, d, s)]: la enfermera 'n' trabaja el turno 's' el día 'd'.
    turnos = {}
    for n in todas_enfermeras:
        for d in todos_dias:
            for s in todos_turnos:
                turnos[(n, d, s)] = model.new_bool_var(f"turno_n{n}_d{d}_s{s}")

    # Cada turno se asigna exactamente a una enfermera.
    for d in todos_dias:
        for s in todos_turnos:
            model.add_exactly_one(turnos[(n, d, s)] for n in todas_enfermeras)

    # Cada enfermera trabaja como máximo un turno por día.
    for n in todas_enfermeras:
        for d in todos_dias:
            model.add_at_most_one(turnos[(n, d, s)] for s in todos_turnos)

    # Intenta distribuir los turnos de manera uniforme, de modo que cada enfermera trabaje
    # min_turnos_por_enfermera turnos. Si esto no es posible, porque el total
    # número de turnos no es divisible por el número de enfermeras, algunas enfermeras serán
    # asignadas un turno más.
    min_turnos_por_enfermera = (num_turnos * num_dias) // num_enfermeras
    if num_turnos * num_dias % num_enfermeras == 0:
        max_turnos_por_enfermera = min_turnos_por_enfermera
    else:
        max_turnos_por_enfermera = min_turnos_por_enfermera + 1
    for n in todas_enfermeras:
        turnos_trabajados: Union[cp_model.LinearExpr, int] = 0
        for d in todos_dias:
            for s in todos_turnos:
                turnos_trabajados += turnos[(n, d, s)]
        model.add(min_turnos_por_enfermera <= turnos_trabajados)
        model.add(turnos_trabajados <= max_turnos_por_enfermera)

    model.maximize(
        sum(
            solicitudes_turnos[n][d][s] * turnos[(n, d, s)]
            for n in todas_enfermeras
            for d in todos_dias
            for s in todos_turnos
        )
    )

    # Crea el solucionador y resuelve.
    solver = cp_model.CpSolver()
    estado = solver.solve(model)

    if estado == cp_model.OPTIMAL:
        print("Solución:")
        for d in todos_dias:
            print("Día", d)
            for n in todas_enfermeras:
                for s in todos_turnos:
                    if solver.value(turnos[(n, d, s)]) == 1:
                        if solicitudes_turnos[n][d][s] == 1:
                            print("Enfermera", n, "trabaja en el turno", s, "(solicitado).")
                        else:
                            print("Enfermera", n, "trabaja en el turno", s, "(no solicitado).")
            print()
        print(
            f"Número de solicitudes de turnos cumplidas = {solver.objective_value}",
            f"(de {num_enfermeras * min_turnos_por_enfermera})",
        )
    else:
        print("¡No se encontró una solución óptima!")

    # Estadísticas.
    print("\nEstadísticas")
    print(f"  - conflictos: {solver.num_conflicts}")
    print(f"  - ramificaciones : {solver.num_branches}")
    print(f"  - tiempo de operación: {solver.wall_time}s")


if __name__ == "__main__":
    main()
