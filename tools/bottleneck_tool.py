import sys
from typing import Optional, Dict, Any

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from core.schemas import BottleneckEvaluation

class BottleneckTool:
    """Tool đánh giá mức độ tương thích và nghẽn cổ chai (Bottleneck) giữa CPU và GPU."""

    LEGACY_CPUS = ["celeron", "pentium", "i3 4160", "i3 4170", "i3 3220", "i3 2100", "core 2 quad", "core 2 duo", "core 2", "q9650", "q6600", "g2030", "g3250"]

    @classmethod
    def check_bottleneck(cls, cpu_name: Optional[str], gpu_model: str, cpu_info: Optional[Dict[str, Any]] = None) -> BottleneckEvaluation:
        if not cpu_name:
            return BottleneckEvaluation(
                cpu_model="Chưa rõ",
                gpu_model=gpu_model,
                bottleneck_risk="MODERATE",
                explanation="Do chưa rõ thông tin CPU hiện tại, không thể đo lường chính xác tỷ lệ nghẽn. Cần kiểm tra thông số CPU trước khi mua."
            )

        cpu_clean = cpu_name.lower().replace("-", " ")
        gpu_clean = gpu_model.lower().replace("-", " ")

        # Kiểm tra CPU đời rất cũ (Haswell/Ivy Bridge/Core 2) đi với Card mạnh
        is_legacy = any(leg in cpu_clean for leg in cls.LEGACY_CPUS)
        is_heavy_gpu = any(g in gpu_clean for g in ["rtx", "rx 6600", "rx 6700", "gtx 1660"])

        if is_legacy and is_heavy_gpu:
            return BottleneckEvaluation(
                cpu_model=cpu_name,
                gpu_model=gpu_model,
                bottleneck_risk="HIGH",
                explanation=f"CẢNH BÁO NGHẼN NẶNG (>40%): CPU {cpu_name} đã quá cũ (chỉ 2 nhân/4 luồng đời cũ) sẽ không thể theo kịp tốc độ render của {gpu_model}. Card đồ họa sẽ bị bóp nghẹt hiệu năng, gây hiện tượng khựng khung hình (stuttering/drop FPS). Khuyến nghị: Giảm ngân sách mua card cũ nhẹ hơn (như GTX 1050Ti/GTX 750Ti) hoặc nâng combo Main + CPU trước!"
            )

        # Kiểm tra CPU tầm trung thế hệ 10 (i5-10400F) với GPU tầm cao (RTX 3070, 3080)
        if "10400" in cpu_clean and any(g in gpu_clean for g in ["3070", "3080", "4070"]):
            return BottleneckEvaluation(
                cpu_model=cpu_name,
                gpu_model=gpu_model,
                bottleneck_risk="MODERATE",
                explanation=f"Nghẽn nhẹ ở độ phân giải 1080p (~15-20%): CPU {cpu_name} có thể đuối nhẹ khi kéo {gpu_model} ở các tựa game esport FPS cao. Nếu chơi game 2K/1440p hoặc bật max đồ họa thì hoàn toàn cân tốt."
            )

        # Cấu hình hiện đại cân đối (i5 12th/14th, Ryzen 5 5600 với RTX 2060S/2070S/3060)
        return BottleneckEvaluation(
            cpu_model=cpu_name,
            gpu_model=gpu_model,
            bottleneck_risk="LOW",
            explanation=f"ĐỘ TƯƠNG THÍCH LÝ TƯỞNG (<8% nghẽn): CPU {cpu_name} và {gpu_model} là combo cân đối hoàn hảo. Cả hai đều khai thác được 98-100% công suất trong hầu hết các tựa game và tác vụ đồ họa hiện nay."
        )

if __name__ == "__main__":
    tool = BottleneckTool()
    print("=== TEST BOTTLENECK ===")
    res1 = tool.check_bottleneck("Intel Core i5-14400F", "NVIDIA GeForce RTX 2070 Super")
    print("Test 1:", res1.bottleneck_risk, "-", res1.explanation)

    res2 = tool.check_bottleneck("Intel Core i3-4160", "NVIDIA GeForce RTX 2060 Super")
    print("Test 2:", res2.bottleneck_risk, "-", res2.explanation)
