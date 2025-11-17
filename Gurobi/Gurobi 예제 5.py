import gurobipy as gp
from gurobipy import GRB

n = int(input())
time = [tuple(map(int, input().split())) for _ in range(n)]

def work(n, time):
    model = gp.Model("Work")
    x = model.addVars(n, vtype=GRB.BINARY, name="x")
    y = model.addVars(n, vtype=GRB.BINARY, name="y")
    
    # 각 작업에 대해 x[i]와 y[i] 중 하나만 선택
    for i in range(n):
        model.addConstr(x[i] + y[i] == 1, name=f"c0_{i}")
    
    # 목적함수: 총 시간 최소화
    model.setObjective(
        gp.quicksum(time[i][0] * x[i] + time[i][1] * y[i] for i in range(n)),
        GRB.MINIMIZE
    )

    # 최적화 실행
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print(f"최소 시간: {model.ObjVal}시간")
    else:
        print("최적해를 찾지 못했습니다.")

work(n, time)
