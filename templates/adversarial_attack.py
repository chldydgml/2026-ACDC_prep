"""화이트박스 적대적 공격 템플릿 (CPU 자동).

가중치(.pth/.onnx)가 제공될 때 FGSM/PGD로 섭동을 만든다.
torchattacks가 있으면 그걸 쓰고, 없으면 수동 구현으로 폴백한다.
블랙박스(가중치 없음)면 이 파일 대신 adversarial-attacks 스킬의 API 스윕을 쓸 것.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"  # 로컬은 보통 cpu


def fgsm(model, x, y, eps=0.03):
    """x: (N,C,H,W) in [0,1], y: 정답 라벨. 한 스텝 섭동."""
    x = x.clone().detach().to(DEVICE).requires_grad_(True)
    loss = F.cross_entropy(model(x), y.to(DEVICE))
    loss.backward()
    x_adv = x + eps * x.grad.sign()
    return x_adv.clamp(0, 1).detach()


def pgd(model, x, y, eps=0.03, alpha=0.007, steps=20, targeted=False):
    """반복 PGD. targeted=True면 y를 '목표' 라벨로 삼아 손실을 낮춘다."""
    x = x.to(DEVICE)
    y = y.to(DEVICE)
    x_adv = (x + torch.empty_like(x).uniform_(-eps, eps)).clamp(0, 1).detach()
    for _ in range(steps):
        x_adv.requires_grad_(True)
        loss = F.cross_entropy(model(x_adv), y)
        grad = torch.autograd.grad(loss, x_adv)[0]
        sign = -1 if targeted else 1
        x_adv = x_adv.detach() + sign * alpha * grad.sign()
        x_adv = (x + (x_adv - x).clamp(-eps, eps)).clamp(0, 1).detach()
    return x_adv


def attack(model, x, y, eps=0.03, steps=20, targeted=False):
    """torchattacks 우선, 없으면 위 수동 구현."""
    model = model.to(DEVICE).eval()
    try:
        import torchattacks
        atk = torchattacks.PGD(model, eps=eps, alpha=eps / 4, steps=steps)
        if targeted:
            atk.set_mode_targeted_by_label()
        return atk(x.to(DEVICE), y.to(DEVICE)).detach()
    except ImportError:
        return pgd(model, x, y, eps=eps, steps=steps, targeted=targeted)


def save_lossless(tensor_img, path):
    """(C,H,W) [0,1] 텐서를 PNG(무손실)로 저장 — JPEG 압축으로 섭동이 사라지는 것 방지."""
    from PIL import Image
    arr = (tensor_img.detach().cpu().clamp(0, 1) * 255).byte()
    arr = arr.permute(1, 2, 0).numpy() if arr.ndim == 3 else arr.numpy()
    Image.fromarray(arr).save(path, format="PNG")
    return path


if __name__ == "__main__":
    print(f"device = {DEVICE}")
