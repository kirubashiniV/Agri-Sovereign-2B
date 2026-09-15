"""
GPU & CUDA Acceleration Smoke Test
Agri-Sovereign / Uzhavan-Sahayak Platform
"""

import sys
import os

print("=" * 80)
print("                   GPU & CUDA HARDWARE ACCELERATION SMOKE TEST")
print("=" * 80)
print(f"Python Executable: {sys.executable}")
print(f"Python Version:    {sys.version.split()[0]}")

try:
    import torch
    print(f"PyTorch Version:   {torch.__version__}")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available:    {cuda_available}")
    
    if cuda_available:
        print(f"Device Name:       {torch.cuda.get_device_name(0)}")
        print(f"Device Count:      {torch.cuda.device_count()}")
        vram_bytes = torch.cuda.get_device_properties(0).total_memory
        print(f"Total VRAM:        {vram_bytes / (1024**3):.2f} GB")
        print(f"CUDA Capability:   {torch.cuda.get_device_capability(0)}")
        
        # Test basic tensor computation on GPU
        x = torch.randn(1024, 1024, device="cuda")
        y = torch.matmul(x, x)
        print("✔ GPU Tensor MatMul Test: PASSED (Hardware acceleration active)")
    else:
        print("⚠ Running in CPU mode (CUDA not detected in torch build).")
except ImportError:
    print("❌ PyTorch is not yet installed in this environment.")

print("=" * 80)
