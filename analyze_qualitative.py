import json
import os

def load_results():
    possible_paths = [
        #"results/experiment_results_20261020_234423.json",
        "results/experiment_results_20261021_004131.json",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f), path
    raise FileNotFoundError("No se encontró 'evaluation_results.json' ni en './' ni en './data/'")

def analyze_qualitative():
    results, file_path = load_results()
    total_cases = len(results)

    if total_cases == 0:
        print("❌ El archivo de resultados está vacío.")
        return

    # -------------------------------------------------------------------------
    # 1. ACUMULADORES PARA 5.2.1 (MATCH RATE UNIFICADO)
    # -------------------------------------------------------------------------
    c1_hits = 0
    c2_hits = 0

    # -------------------------------------------------------------------------
    # 2. ACUMULADORES PARA 5.2.4 (DESEMPEÑO COMPUTACIONAL)
    # -------------------------------------------------------------------------
    c1_p_tok_sum, c1_c_tok_sum, c1_tot_tok_sum, c1_lat_sum = 0, 0, 0, 0.0
    c2_p_tok_sum, c2_c_tok_sum, c2_tot_tok_sum, c2_lat_sum = 0, 0, 0, 0.0

    for case in results:
        # Aciertos
        if case.get("exact_sql_match", False):
            c1_hits += 1
        if case.get("exact_orm_match", False) or case.get("ast_match", False):
            c2_hits += 1

        # Tokens C1 (SQL)
        c1_p = case.get("sql_prompt_tokens", 0)
        c1_c = case.get("sql_completion_tokens", 0)
        c1_p_tok_sum += c1_p
        c1_c_tok_sum += c1_c
        c1_tot_tok_sum += case.get("sql_total_tokens", c1_p + c1_c)
        c1_lat_sum += case.get("sql_latency_seconds", 0.0)

        # Tokens C2 (ORM)
        c2_p = case.get("orm_prompt_tokens", 0)
        c2_c = case.get("orm_completion_tokens", 0)
        c2_p_tok_sum += c2_p
        c2_c_tok_sum += c2_c
        c2_tot_tok_sum += case.get("orm_total_tokens", c2_p + c2_c)
        c2_lat_sum += case.get("orm_latency_seconds", 0.0)

    # -------------------------------------------------------------------------
    # CÁLCULOS 5.2.1
    # -------------------------------------------------------------------------
    c1_pct = (c1_hits / total_cases * 100) if total_cases else 0
    c2_pct = (c2_hits / total_cases * 100) if total_cases else 0
    diff_pct = c2_pct - c1_pct

    # -------------------------------------------------------------------------
    # CÁLCULOS 5.2.4
    # -------------------------------------------------------------------------
    c1_avg_p_tok = c1_p_tok_sum / total_cases
    c1_avg_c_tok = c1_c_tok_sum / total_cases
    c1_avg_tot_tok = c1_tot_tok_sum / total_cases
    c1_avg_lat = c1_lat_sum / total_cases

    c2_avg_p_tok = c2_p_tok_sum / total_cases
    c2_avg_c_tok = c2_c_tok_sum / total_cases
    c2_avg_tot_tok = c2_tot_tok_sum / total_cases
    c2_avg_lat = c2_lat_sum / total_cases

    diff_p_tok = ((c2_avg_p_tok - c1_avg_p_tok) / c1_avg_p_tok * 100) if c1_avg_p_tok else 0
    diff_c_tok = ((c2_avg_c_tok - c1_avg_c_tok) / c1_avg_c_tok * 100) if c1_avg_c_tok else 0
    diff_tot_tok = ((c2_avg_tot_tok - c1_avg_tot_tok) / c1_avg_tot_tok * 100) if c1_avg_tot_tok else 0
    diff_lat = c2_avg_lat - c1_avg_lat

    # -------------------------------------------------------------------------
    # IMPRESIÓN
    # -------------------------------------------------------------------------
    print("\n======================================================================")
    print("5.2.1 VALIDEZ Y COINCIDENCIA SINTÁCTICA (MATCH RATE)")
    print("======================================================================\n")
    print(f"{'PROYECTO EVALUADO':<22} | {'#CASOS':<7} | {'C1 TEXT-TO-SQL (ACIERTOS / %)':<30} | {'C2 TEXT-TO-ORM (ACIERTOS / %)':<30} | {'DIFERENCIA':<10}")
    print("-" * 108)
    print(f"{'Dataset Único (Benchmark)':<22} | {total_cases:<7} | {c1_hits} ({c1_pct:.1f}%) {'':<18} | {c2_hits} ({c2_pct:.1f}%) {'':<18} | {diff_pct:+.1f}%")
    print("-" * 108)
    print(f"{'PROMEDIO GLOBAL':<22} | {total_cases:<7} | {c1_hits} ({c1_pct:.1f}%) {'':<18} | {c2_hits} ({c2_pct:.1f}%) {'':<18} | {diff_pct:+.1f}%\n")

    print("\n======================================================================")
    print("5.2.4 DESEMPEÑO COMPUTACIONAL")
    print("======================================================================\n")
    print(f"{'VARIABLE DE DESEMPEÑO':<38} | {'C1 TEXT-TO-SQL':<18} | {'C2 TEXT-TO-ORM':<18} | {'COSTO ADICIONAL':<15}")
    print("-" * 98)
    print(f"{'Tokens de Entrada Promedio (Prompt)':<38} | {c1_avg_p_tok:<18.1f} | {c2_avg_p_tok:<18.1f} | {diff_p_tok:+.1f}%")
    print(f"{'Tokens de Salida Promedio (Respuesta)':<38} | {c1_avg_c_tok:<18.1f} | {c2_avg_c_tok:<18.1f} | {diff_c_tok:+.1f}%")
    print(f"{'Consumo Total de Tokens / Consulta':<38} | {c1_avg_tot_tok:<18.1f} | {c2_avg_tot_tok:<18.1f} | {diff_tot_tok:+.1f}%")
    print(f"{'LATENCIA PROMEDIO DE GENERACIÓN':<38} | {c1_avg_lat:<18.3f}s | {c2_avg_lat:<18.3f}s | {diff_lat:+.3f}s\n")

if __name__ == "__main__":
    analyze_qualitative()