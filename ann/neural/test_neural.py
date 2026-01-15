import torch
from torch.utils.data import Dataset
from torchvision import datasets
from torchvision.transforms import ToTensor
from build_pipeline.neural import MLPClassifier


training_data = datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor()
)

test_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=ToTensor()
)

# ----------------------------
# 1. Initialize and train the classifier
# ----------------------------
# FashionMNIST images are 28x28, flatten to 784
input_dim = 28 * 28
num_classes = 10  # 10 FashionMNIST labels

# Initialize model
model_wrapper = MLPClassifier(d_in=input_dim, n_out=num_classes, layers=3, nodes=64)

# Train the classifier
model_wrapper.train_classifier(
    dataset=training_data,
    output=num_classes,
    epochs=5,
    batch_size=128,
    lr=1e-3
)

# ----------------------------
# 2. Evaluate on test set
# ----------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MLPClassifier(d_in=input_dim, n_out=num_classes, layers=3, nodes=64).to(device)
model.eval()  # just evaluation mode

test_loader = torch.utils.data.DataLoader(test_data, batch_size=128, shuffle=False)
correct = 0
total = 0

with torch.no_grad():
    for x, y in test_loader:
        x, y = x.to(device), y.to(device)
        x = x.view(x.size(0), -1)  # flatten 28x28 -> 784
        logits = model(x)
        preds = torch.argmax(logits, dim=1)
        correct += (preds == y).sum().item()
        total += y.size(0)

print(f"Test Accuracy: {correct/total:.4f}")

# ----------------------------
# 3. Print model weights
# ----------------------------
print("\nModel weights after training:\n")
for name, param in model.named_parameters():
    if param.requires_grad:
        print(f"{name}:")
        print(param.data)
        print("-" * 40)
torch.save(model.state_dict(), "mlp_fashionmnist_weights.pth")
print("Model weights saved to 'mlp_fashionmnist_weights.pth'")

## Recreate the same model architecture
#input_dim = 28 * 28
#num_classes = 10
#model = MLPClassifier(d_in=input_dim, n_out=num_classes, layers=3, nodes=64)
#
## Load the saved weights
#model.load_state_dict(torch.load("mlp_fashionmnist_weights.pth"))
#model.eval()  # set to evaluation mode if needed