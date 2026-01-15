import torch, torch.nn as nn
from torch.utils.data import DataLoader


# Define a simple feedforward neural network (MLP)
class MLPClassifier(nn.Module):
  def __init__(self, d_in, n_out, layers:int=3, nodes:int=64):
    super().__init__() # Sequential block
    modules = [nn.Linear(d_in, nodes), nn.ReLU()]
    for _ in range(layers - 2):
        modules.append(nn.Linear(nodes, nodes))
        modules.append(nn.ReLU())
    modules.append(nn.Linear(nodes, n_out))
    self.net = nn.Sequential(*modules)
  def forward(self, x): # Forward pass through the network
    return self.net(x)

  def train_classifier(self, dataset, output, epochs:int=10, batch_size:int =128,
                       lr:float = 0.001):
    device = torch.device("cuda" if
         torch.cuda.is_available() else "cpu")
    self.to(device)

    opt = torch.optim.Adam(self.parameters(), lr= lr)
    loss_fn = nn.CrossEntropyLoss()

    # Hyperparameters
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    for epoch in range(epochs):
      self.train()
      total_loss=0
      for x, y in loader:
          x, y = x.to(device), y.to(device)   # Move to GPU/CPU
          x = x.view(x.size(0), -1)
          opt.zero_grad()                     # 1. Reset gradients
          logits = self(x)                    # 2. Forward pass
          loss = loss_fn(logits, y)           # 3. Compute loss
          loss.backward()                     # 4. Backward pass
          opt.step()                          # 5. Update weights
          total_loss+=loss.item()
      print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(loader):.4f}")