import pytest
from core.schemas import HardwareSpecContract
from tools.db_lookup_tool import DBLookupTool
from tools.psu_calculator_tool import PSUCalculatorTool
from tools.bottleneck_tool import BottleneckTool
from agents.spec_analyst_agent import SpecAnalystAgent
from agents.compatibility_agent import CompatibilityAgent

def test_db_lookup_finds_gpus():
    db = DBLookupTool()
    gpus = db.find_gpus_by_budget(5_000_000)
    assert len(gpus) > 0
    # Every candidate should be reasonably within budget (with tolerance)
    for g in gpus:
        assert g.market_price_used_vnd <= 5_000_000 * 1.15

def test_psu_calculator_danger():
    # 450W with 65W CPU and 220W GPU -> Peak is 481W > 450W -> DANGER
    eval_res = PSUCalculatorTool.calculate_load(cpu_tdp=65, gpu_tdp=220, user_psu_watt=450)
    assert eval_res.status == "DANGER"
    assert eval_res.load_percentage > 95.0

def test_psu_calculator_safe():
    # 650W with 65W CPU and 170W GPU -> SAFE
    eval_res = PSUCalculatorTool.calculate_load(cpu_tdp=65, gpu_tdp=170, user_psu_watt=650)
    assert eval_res.status == "SAFE"
    assert eval_res.load_percentage < 80.0

def test_bottleneck_legacy_cpu():
    eval_res = BottleneckTool.check_bottleneck(
        cpu_name="Intel Core i3-4160",
        gpu_model="NVIDIA GeForce RTX 2060 Super"
    )
    assert eval_res.bottleneck_risk == "HIGH"

def test_end_to_end_agent_flow():
    agent1 = SpecAnalystAgent()
    agent2 = CompatibilityAgent()

    query = "Tôi đang có chip i5 14400F và nguồn 650W, ngân sách 5 triệu muốn kiếm con card cũ để chơi game"
    contract = agent1.analyze(query)
    
    assert contract.current_psu_watt == 650
    assert contract.budget_vnd == 5_000_000
    assert "14400" in contract.current_cpu

    report = agent2.audit(contract, verbose=False)
    assert len(report.recommendations) > 0
    assert report.recommendations[0].psu_evaluation.status == "SAFE"
