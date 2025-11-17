import gurobipy as gp
from gurobipy import GRB

def knapsack_unbounded_gurobi(N, W, items):
    # 모델 생성
    model = gp.Model("unbounded_knapsack")
    
    # 결정변수: 보석 i를 몇 개 선택할지 (정수, 0 이상)
    x = model.addVars(N, vtype=GRB.binary, name="x")
    
    # 목적함수: 총 값어치 최대화z
    model.setObjective(gp.quicksum(items[i][1] * x[i] for i in range(N)), GRB.MAXIMIZE)
    
    # 제약조건: 총 무게 ≤ W
    model.addConstr(gp.quicksum(items[i][0] * x[i] for i in range(N)) <= W, "capacity")
    
    # 최적화 실행
    model.optimize()
    
    # 결과 출력
    if model.status == GRB.OPTIMAL:
        print(f"최대 값어치: {model.ObjVal}")
        for i in range(N):
            if x[i].X > 0.5:  # 선택된 보석만 표시
                print(f"보석 {i+1}: {int(x[i].X)}개 선택 (무게={items[i][0]}, 값어치={items[i][1]})")
    else:
        print("최적해를 찾지 못했습니다.")

# 입력 처리
if __name__ == "__main__":
    N, W = map(int, input().split())
    items = [tuple(map(int, input().split())) for _ in range(N)]
    
    knapsack_unbounded_gurobi(N, W, items)
