import os
import torch
import torch.distributed as dist

def main():
    dist.init_process_group(backend="nccl")
    local_rank = int(os.environ["LOCAL_RANK"])
    world_size = int(os.environ["WORLD_SIZE"])
    torch.cuda.set_device(local_rank)
    t = torch.tensor([local_rank + 1.0], device=f"cuda:{local_rank}")
    dist.all_reduce(t)
    print(f"Rank {local_rank}/{world_size} successfully all-reduced: sum = {t.item()}")
    dist.destroy_process_group()

if __name__ == "__main__":
    main()
