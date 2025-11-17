from gurobipy import Model, GRB, quicksum
import random

# ----------------------------
# ① Job 생성 (TF/RDD 방식)
# ----------------------------
def generate_jobs_TF_RDD(n, p_low=1, p_high=20, seed=42, scenario="medium"):
    rng = random.Random(seed)
    p = [rng.randint(p_low, p_high) for _ in range(n)]
    Ptot = sum(p)

    if scenario == "loose":   TF, RDD = 0.2, 0.6   # 납기 여유롭고 다양
    elif scenario == "medium": TF, RDD = 0.5, 0.5   # 중간 수준
    elif scenario == "tight":  TF, RDD = 0.8, 0.4   # 빡빡하고 유사한 납기
    else: raise ValueError("scenario must be 'loose','medium','tight'")

    low, high = int((1 - TF - RDD/2) * Ptot), int((1 - TF + RDD/2) * Ptot)
    d = [rng.randint(max(0, low), high) for _ in range(n)]
    return p, d

# ----------------------------
# ② Time-Indexed ILP 모델
# ----------------------------
def solve_time_indexed_total_tardiness(p, d, time_limit=300, mip_gap=0.0, verbose=False):
    n, H = len(p), sum(p)
    m = Model("TT")
    m.Params.OutputFlag = 1 if verbose else 0
    m.Params.TimeLimit, m.Params.MIPGap = time_limit, mip_gap

    # y[j,t] = 1 ⇔ job j가 시간 t에 시작
    y = {(j, t): m.addVar(vtype=GRB.BINARY) for j in range(n) for t in range(H - p[j] + 1)}

    # 각 job은 한 번만 시작
    for j in range(n):
        m.addConstr(quicksum(y[j, t] for t in range(H - p[j] + 1)) == 1)

    # 한 시각에는 하나의 job만 수행
    for θ in range(H):
        m.addConstr(quicksum(
            y[j, t]
            for j in range(n)
            for t in range(max(0, θ - p[j] + 1), min(θ, H - p[j]) + 1)
        ) <= 1)

    # 목적함수: 총 지연시간 최소화
    m.setObjective(quicksum(
        max(0, t + p[j] - d[j]) * y[j, t]
        for j in range(n) for t in range(H - p[j] + 1)
    ), GRB.MINIMIZE)

    m.optimize()

    # 결과 요약
    if m.SolCount == 0:
        return {"status": m.Status, "obj": None}

    starts = [next(t for t in range(H - p[j] + 1) if y[j, t].X > 0.5) for j in range(n)]
    tard = [max(0, starts[j] + p[j] - d[j]) for j in range(n)]
    return {
        "status": m.Status,
        "obj": m.ObjVal,
        "late_cnt": sum(t > 0 for t in tard),
        "avg_T": sum(tard) / n
    }

# ----------------------------
# ③ 세 시나리오 실행
# ----------------------------
def run_all(n=100, seed=42, time_limit=300, verbose=False):
    for sc in ["loose", "medium", "tight"]:
        p, d = generate_jobs_TF_RDD(n=n, seed=seed, scenario=sc)
        res = solve_time_indexed_total_tardiness(p, d, time_limit, 0.0, verbose)
        print(f"[{sc.upper()}] ∑p={sum(p)}  avg(d)={sum(d)/n:.1f}  "
              f"obj(∑T)={res['obj']:.1f}  late={res['late_cnt']}/{n}  avgT={res['avg_T']:.1f}")

if __name__ == "__main__":
    run_all(n=100, seed=42, time_limit=600, verbose=True)

    

