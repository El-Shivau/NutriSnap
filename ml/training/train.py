"""
Training Script -- EfficientNetB0 on Food-101 (PyTorch + timm)
==============================================================

This script trains a food recognition model using EfficientNetB0
from timm (pre-trained on ImageNet-21k) with a custom 101-class head.

Training Strategy (Two-Phase Transfer Learning)
-------------------------------------------------
Phase 1 -- HEAD ONLY:
    - The EfficientNetB0 backbone is frozen.
    - Only the final classification layer is trained.
    - Fast convergence (~5-10 epochs).

Phase 2 -- FINE-TUNING:
    - Backbone is gradually unfrozen.
    - Lower learning rate to preserve pretrained features.
    - Better accuracy on food-specific patterns.

Usage
-----
    # Run from project root:
    python ml/training/train.py --version v1

    # Custom settings:
    python ml/training/train.py \\
        --data-dir ml/dataset/food-101/images \\
        --version v1 \\
        --epochs-phase1 10 \\
        --epochs-phase2 10 \\
        --batch-size 32

Outputs
-------
    ml/models/food101_v1.pt           <- Best model weights (val_accuracy)
    ml/training/checkpoints/          <- Per-epoch checkpoints
    ml/evaluation/reports/            <- Training history CSV

IMPORTANT: Run from the project root directory.
IMPORTANT: This file must NEVER import Flask or backend modules.
"""

import argparse
import csv
import logging
import os
import sys

# Add project root to sys.path so we can import ml modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ml.training.config import (
    CHECKPOINT_DIR,
    EARLY_STOPPING_PATIENCE,
    EVALUATION_OUTPUT_DIR,
    FINE_TUNE_AT_LAYER,
    IMAGE_SIZE,
    MIN_LEARNING_RATE,
    NUM_CLASSES,
    PHASE1_EPOCHS,
    PHASE1_LEARNING_RATE,
    PHASE2_EPOCHS,
    PHASE2_LEARNING_RATE,
    REDUCE_LR_FACTOR,
    REDUCE_LR_PATIENCE,
    VALIDATION_SPLIT,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train EfficientNetB0 on Food-101 (PyTorch + timm).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--data-dir", type=str, default="ml/dataset/food-101/images")
    parser.add_argument("--version", type=str, default="v1")
    parser.add_argument("--epochs-phase1", type=int, default=PHASE1_EPOCHS)
    parser.add_argument("--epochs-phase2", type=int, default=PHASE2_EPOCHS)
    parser.add_argument("--batch-size", type=int, default=32)
    return parser.parse_args()


def build_dataloaders(data_dir: str, batch_size: int, val_split: float = VALIDATION_SPLIT):
    """
    Build PyTorch DataLoaders for training and validation.

    Uses torchvision's ImageFolder with augmentation for train,
    clean transforms for validation.
    """
    import torch
    from torchvision import datasets, transforms

    # Training augmentation (same augmentations as config.AUGMENTATION_CONFIG)
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(IMAGE_SIZE[0], scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Validation -- no augmentation, just resize + normalize
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMAGE_SIZE[0]),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    full_dataset = datasets.ImageFolder(data_dir)
    total = len(full_dataset)
    val_size = int(total * val_split)
    train_size = total - val_size

    train_subset, val_subset = torch.utils.data.random_split(
        full_dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )

    # Apply transforms after split (using Subset with transform override)
    from torch.utils.data import Dataset

    class TransformedSubset(Dataset):
        def __init__(self, subset, transform):
            self.subset = subset
            self.transform = transform

        def __getitem__(self, idx):
            x, y = self.subset[idx]
            if self.transform:
                x = self.transform(x)
            return x, y

        def __len__(self):
            return len(self.subset)

    # Re-load with transforms applied
    train_ds_raw = datasets.ImageFolder(data_dir, transform=train_transform)
    val_ds_raw = datasets.ImageFolder(data_dir, transform=val_transform)

    train_idx = train_subset.indices
    val_idx = val_subset.indices

    train_sampler = torch.utils.data.SubsetRandomSampler(train_idx)
    val_sampler = torch.utils.data.SubsetRandomSampler(val_idx)

    num_workers = min(4, os.cpu_count() or 1)
    train_loader = torch.utils.data.DataLoader(
        train_ds_raw, batch_size=batch_size, sampler=train_sampler,
        num_workers=num_workers, pin_memory=False
    )
    val_loader = torch.utils.data.DataLoader(
        val_ds_raw, batch_size=batch_size, sampler=val_sampler,
        num_workers=num_workers, pin_memory=False
    )

    logger.info("Train: %d images | Val: %d images | Classes: %d",
                len(train_idx), len(val_idx), len(full_dataset.classes))
    return train_loader, val_loader, full_dataset.classes


def build_model(num_classes: int = NUM_CLASSES):
    """Build EfficientNetB0 with ImageNet-21k pretrained weights via timm."""
    import timm
    model = timm.create_model(
        "efficientnet_b0",
        pretrained=True,
        num_classes=num_classes,
    )
    logger.info("Model built. Parameters: %s", f"{sum(p.numel() for p in model.parameters()):,}")
    return model


def freeze_backbone(model) -> None:
    """Freeze all layers except the final classification head."""
    for name, param in model.named_parameters():
        if "classifier" not in name:
            param.requires_grad = False
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info("Backbone frozen. Trainable params: %s", f"{trainable:,}")


def unfreeze_top_layers(model, unfreeze_from: int = FINE_TUNE_AT_LAYER) -> None:
    """Unfreeze all parameters (Phase 2 fine-tuning)."""
    for param in model.parameters():
        param.requires_grad = True
    total = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info("All layers unfrozen. Trainable params: %s", f"{total:,}")


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    import torch
    total_loss, correct, total = 0.0, 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(1) == labels).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


def validate(model, loader, criterion, device):
    model.eval()
    import torch
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * images.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += images.size(0)
    return total_loss / total, correct / total


def main() -> None:
    args = parse_args()
    model_output_path = f"ml/models/food101_{args.version}.pt"

    logger.info("=" * 60)
    logger.info("NutriSnap -- EfficientNetB0 Training (PyTorch + timm)")
    logger.info("=" * 60)
    logger.info("Data dir       : %s", args.data_dir)
    logger.info("Output         : %s", model_output_path)
    logger.info("Phase 1 epochs : %d", args.epochs_phase1)
    logger.info("Phase 2 epochs : %d", args.epochs_phase2)
    logger.info("=" * 60)

    if not os.path.isdir(args.data_dir):
        logger.error("Dataset not found: %s\nRun: bash scripts/download_dataset.sh", args.data_dir)
        sys.exit(1)

    import torch

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Device: %s", device)

    os.makedirs("ml/models", exist_ok=True)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(EVALUATION_OUTPUT_DIR, exist_ok=True)

    train_loader, val_loader, classes = build_dataloaders(args.data_dir, args.batch_size)
    model = build_model(num_classes=len(classes)).to(device)
    criterion = torch.nn.CrossEntropyLoss()

    history = []
    best_val_acc = 0.0

    # ====================================================================
    # Phase 1: Train head only
    # ====================================================================
    logger.info("\n--- Phase 1: Head-only training ---")
    freeze_backbone(model)
    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=PHASE1_LEARNING_RATE,
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, factor=REDUCE_LR_FACTOR, patience=REDUCE_LR_PATIENCE, min_lr=MIN_LEARNING_RATE
    )

    no_improve = 0
    for epoch in range(1, args.epochs_phase1 + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        scheduler.step(val_loss)
        logger.info("P1 Ep %2d/%d | train_loss=%.4f acc=%.3f | val_loss=%.4f acc=%.3f",
                    epoch, args.epochs_phase1, train_loss, train_acc, val_loss, val_acc)
        history.append({"phase": 1, "epoch": epoch, "train_loss": train_loss,
                        "train_acc": train_acc, "val_loss": val_loss, "val_acc": val_acc})

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_output_path)
            logger.info("  -> Best model saved (val_acc=%.4f)", best_val_acc)
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= EARLY_STOPPING_PATIENCE:
                logger.info("Early stopping at epoch %d", epoch)
                break

    # ====================================================================
    # Phase 2: Fine-tune all layers
    # ====================================================================
    logger.info("\n--- Phase 2: Fine-tuning all layers ---")
    unfreeze_top_layers(model)
    optimizer = torch.optim.Adam(model.parameters(), lr=PHASE2_LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, factor=REDUCE_LR_FACTOR, patience=REDUCE_LR_PATIENCE, min_lr=MIN_LEARNING_RATE
    )

    no_improve = 0
    for epoch in range(1, args.epochs_phase2 + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        scheduler.step(val_loss)
        logger.info("P2 Ep %2d/%d | train_loss=%.4f acc=%.3f | val_loss=%.4f acc=%.3f",
                    epoch, args.epochs_phase2, train_loss, train_acc, val_loss, val_acc)
        history.append({"phase": 2, "epoch": epoch, "train_loss": train_loss,
                        "train_acc": train_acc, "val_loss": val_loss, "val_acc": val_acc})

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_output_path)
            logger.info("  -> Best model saved (val_acc=%.4f)", best_val_acc)
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= EARLY_STOPPING_PATIENCE:
                logger.info("Early stopping at epoch %d", epoch)
                break

    # Save training history CSV
    history_path = os.path.join(EVALUATION_OUTPUT_DIR, "training_history.csv")
    with open(history_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=history[0].keys())
        writer.writeheader()
        writer.writerows(history)

    logger.info("=" * 60)
    logger.info("Training complete! Best val_accuracy: %.4f", best_val_acc)
    logger.info("Model saved to: %s", model_output_path)
    logger.info("History saved to: %s", history_path)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
