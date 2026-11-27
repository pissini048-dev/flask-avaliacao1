from flask import Blueprint, flash, render_template, request

bp = Blueprint("calculos", __name__)


def calcular_irpf_estimado(salario_bruto: float) -> dict:
    if salario_bruto <= 2259.20:
        aliquota = 0.0
        deducao = 0.0
    elif salario_bruto <= 2826.65:
        aliquota = 0.075
        deducao = 169.44
    elif salario_bruto <= 3751.05:
        aliquota = 0.15
        deducao = 381.44
    elif salario_bruto <= 4664.68:
        aliquota = 0.225
        deducao = 662.77
    else:
        aliquota = 0.275
        deducao = 896.00

    imposto_bruto = salario_bruto * aliquota
    desconto_estimado = max(0.0, round(imposto_bruto - deducao, 2))
    salario_apos_irpf = round(salario_bruto - desconto_estimado, 2)

    return {
        "salario_bruto": round(salario_bruto, 2),
        "aliquota_percentual": round(aliquota * 100, 1),
        "desconto_estimado": desconto_estimado,
        "salario_apos_irpf": salario_apos_irpf,
    }


def calcular_decimo_terceiro_proporcional(
    salario_base: float, meses_trabalhados: int
) -> dict:
    if meses_trabalhados < 1 or meses_trabalhados > 12:
        raise ValueError("Informe uma quantidade de meses entre 1 e 12.")

    valor_proporcional = round((salario_base / 12) * meses_trabalhados, 2)
    return {
        "salario_base": round(salario_base, 2),
        "meses_trabalhados": meses_trabalhados,
        "valor_proporcional": valor_proporcional,
    }


@bp.route("/painel", methods=("GET", "POST"))
def painel():
    resultado_irpf = None
    resultado_13 = None

    if request.method == "POST":
        tipo_calculo = request.form.get("tipo_calculo")

        if tipo_calculo == "irpf":
            try:
                salario_bruto = float(
                    request.form.get("salario_bruto", "").replace(",", ".")
                )
                if salario_bruto < 0:
                    raise ValueError("O salário bruto não pode ser negativo.")
                resultado_irpf = calcular_irpf_estimado(salario_bruto)
            except ValueError as exc:
                flash(str(exc) or "Valor de salário bruto inválido.")

        elif tipo_calculo == "decimo_terceiro":
            try:
                salario_base = float(
                    request.form.get("salario_base", "").replace(",", ".")
                )
                meses_trabalhados = int(request.form.get("meses_trabalhados", "0"))
                if salario_base < 0:
                    raise ValueError("O salário base não pode ser negativo.")
                resultado_13 = calcular_decimo_terceiro_proporcional(
                    salario_base, meses_trabalhados
                )
            except ValueError as exc:
                flash(
                    str(exc)
                    or "Preencha salário base e meses trabalhados (1 a 12) corretamente."
                )

    return render_template(
        "calculos/index.html",
        resultado_irpf=resultado_irpf,
        resultado_13=resultado_13,
    )