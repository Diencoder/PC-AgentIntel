import sys
from typing import Optional

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from core.schemas import PSUEvaluation

class PSUCalculatorTool:
    """Tool tính toán công suất nguồn (PSU) và đánh giá độ an toàn điện năng."""

    SYSTEM_BASE_LOAD_WATT = 100  # Bo mạch chủ, RAM, NVMe SSD, Quạt tản nhiệt, RGB
    TRANSIENT_SPIKE_HEADROOM = 1.25  # Hệ số dự phòng xung nhịp và tải đỉnh đột ngột

    @classmethod
    def calculate_load(cls, cpu_tdp: int, gpu_tdp: int, user_psu_watt: Optional[int]) -> PSUEvaluation:
        """
        Tính toán công suất đỉnh:
        Peak_Load = (CPU_TDP + GPU_TDP + Base_Load) * Headroom
        """
        raw_draw = cpu_tdp + gpu_tdp + cls.SYSTEM_BASE_LOAD_WATT
        estimated_peak = int(raw_draw * cls.TRANSIENT_SPIKE_HEADROOM)

        if not user_psu_watt or user_psu_watt <= 0:
            return PSUEvaluation(
                psu_watt=0,
                estimated_peak_system_watt=estimated_peak,
                load_percentage=0.0,
                status="UNKNOWN",
                message=f"Chưa rõ công suất nguồn! Tổng tải đỉnh ước tính là {estimated_peak}W. Bạn cần mở nắp case kiểm tra tem nguồn tối thiểu {estimated_peak + 50}W."
            )

        load_percentage = round((estimated_peak / user_psu_watt) * 100, 1)

        if load_percentage <= 80.0:
            status = "SAFE"
            msg = f"Nguồn {user_psu_watt}W hoạt động an toàn tuyệt đối (Tải đỉnh {estimated_peak}W ~ {load_percentage}%). Nguồn nằm trong dải hiệu suất chuyển đổi điện năng tối ưu."
        elif 80.0 < load_percentage <= 95.0:
            status = "WARNING"
            msg = f"Cảnh báo: Nguồn {user_psu_watt}W chịu tải khá cao ({estimated_peak}W ~ {load_percentage}%). Quạt nguồn có thể hú to khi chơi game nặng, nên cân nhắc nâng cấp nếu có điều kiện."
        else:
            status = "DANGER"
            msg = f"NGUY HIỂM: Nguồn {user_psu_watt}W bị quá tải trầm trọng ({estimated_peak}W ~ {load_percentage}% > 95%)! Nguy cơ sập nguồn (shut down), sụt áp hoặc chập cháy linh kiện khi kích hoạt full load."

        return PSUEvaluation(
            psu_watt=user_psu_watt,
            estimated_peak_system_watt=estimated_peak,
            load_percentage=load_percentage,
            status=status,
            message=msg
        )

if __name__ == "__main__":
    tool = PSUCalculatorTool()
    print("=== TEST PSU CALCULATOR ===")
    res1 = tool.calculate_load(cpu_tdp=65, gpu_tdp=215, user_psu_watt=650)
    print("Test 1 (i5 14400F + RTX 2070S + 650W):", res1.status, res1.message)

    res2 = tool.calculate_load(cpu_tdp=65, gpu_tdp=220, user_psu_watt=450)
    print("Test 2 (i5 10400F + RTX 3070 + 450W):", res2.status, res2.message)
