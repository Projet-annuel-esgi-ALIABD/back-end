import torch
import torch.nn as nn

class AirQualityLSTM(nn.Module):
    def __init__(self, input_size: int, output_size: int, lstm_size: int, n_lstm_layers: int, dense_layers: list,
                 dropout_rate: float = 0.3):
        super(AirQualityLSTM, self).__init__()

        self.n_lstm_layers = n_lstm_layers
        self.lstm_size = lstm_size

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=lstm_size,
            num_layers=n_lstm_layers,
            batch_first=True,
            dropout=dropout_rate if n_lstm_layers > 1 else 0
        )

        self.clf = nn.Sequential()
        input_dim = lstm_size
        for layer_size in dense_layers:
            self.clf.append(nn.ReLU())
            self.clf.append(nn.Dropout(dropout_rate))
            self.clf.append(nn.Linear(input_dim, layer_size))
            input_dim = layer_size

        self.clf.append(nn.ReLU())
        self.clf.append(nn.Dropout(dropout_rate))
        self.clf.append(nn.Linear(input_dim, output_size))

    def forward(self, x):
        h_0 = torch.zeros(self.n_lstm_layers, x.size(0), self.lstm_size).to(x.device)
        c_0 = torch.zeros(self.n_lstm_layers, x.size(0), self.lstm_size).to(x.device)
        out, _ = self.lstm(x, (h_0.detach(), c_0.detach()))
        out = out[:, -1, :]
        out = self.clf(out)
        return out