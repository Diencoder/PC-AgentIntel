from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class HardwareSpecContract(BaseModel):
    """
    Data Contract produced by Agent 1 (Spec Analyst) and consumed by Agent 2 (Compatibility Auditor).
    """
    user_raw_query: str = Field(description="Original user request string")
    current_cpu: Optional[str] = Field(default=None, description="Identified current CPU model")
    current_psu_watt: Optional[int] = Field(default=None, description="Current power supply capacity in Watts")
    budget_vnd: Optional[int] = Field(default=None, description="Budget in Vietnamese Dong")
    target_component: str = Field(default="GPU", description="Component target: 'GPU' or 'FULL_PC'")
    condition: str = Field(default="used", description="Target condition: 'used', 'new', or 'any'")
    purpose: str = Field(default="Gaming", description="User's primary usage goal (Gaming, Render, Office, etc.)")
    missing_fields: List[str] = Field(default_factory=list, description="Fields that were not specified by user")
    warning_flag: Optional[str] = Field(default=None, description="Immediate warnings identified during intent analysis")
    already_owned_parts: Dict[str, str] = Field(default_factory=dict, description="Linh kiện người dùng đã có sẵn (ví dụ: cpu, gpu)")
    agent1_brief: str = Field(default="", description="Văn bản nhận định & phân tích bối cảnh từ Agent 1 gửi cho Agent 2")

class GPUCandidate(BaseModel):
    """Information for a candidate GPU evaluated by tools."""
    id: str
    model: str
    tdp_watt: int
    recommended_psu_watt: int
    vram_gb: int
    market_price_used_vnd: int
    performance_tier: str
    power_connectors: str

class PSUEvaluation(BaseModel):
    """Evaluation result from PSU calculation tool."""
    psu_watt: int
    estimated_peak_system_watt: int
    load_percentage: float
    status: str  # SAFE, WARNING, DANGER
    message: str

class BottleneckEvaluation(BaseModel):
    """Evaluation result from Bottleneck checking tool."""
    cpu_model: str
    gpu_model: str
    bottleneck_risk: str  # LOW, MODERATE, HIGH
    explanation: str

class GPURecommendation(BaseModel):
    """Final assessed recommendation item."""
    gpu: GPUCandidate
    psu_evaluation: PSUEvaluation
    bottleneck_evaluation: BottleneckEvaluation
    pros: List[str]
    cons: List[str]
    quick_review: str = ""

class FinalAuditReport(BaseModel):
    """Complete advisory and compatibility audit output."""
    contract: HardwareSpecContract
    recommendations: List[GPURecommendation]
    executive_summary: str
    safety_alerts: List[str]
    purchase_checklist: List[str]
    full_pc_build: Optional[Dict[str, Any]] = None
    agent1_brief: str = ""
    agent2_consultation: str = ""
