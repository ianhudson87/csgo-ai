import torch.nn as nn
from model.ConvLSTMCell import ConvLSTMCell
from efficientnet_pytorch import EfficientNet
eff_net = EfficientNet.from_pretrained('efficientnet-b0')
import torch

def get_options():
    opt = {
    "batch_size": 1,
    "width": 80,
    "length":180,
    "num_features": 21 + 21 + 6, # using one hot encoding for output of model for mouse_x and mouse_y
    "model_name": "aimtrain-normalLR-classification",
    "model_save_path": "./trained_models",
    "model_load_path": "./trained_models", # for starting a epoch!=0
    "epochs": 20, # includes pretrained epochs if load_pretrained_model is true
    }

    return opt

opt = get_options()

class SomethingModel(nn.Module):
    # only involution blocks and residual connection between first and last layer
    def __init__(self, hidden_layer_size = 256):
        super(SomethingModel, self).__init__()

        global opt
        hidden_size = hidden_layer_size
        num_filter = 3

        # get the first 2 layers of the pretrained efficient net
        head = nn.ModuleList(list(eff_net.children())[0:2])
        # get the first 4 blocks from the body of pretrained efficient net (why do they make it so difficult)
        blocks = nn.ModuleList(list(list(eff_net.children())[2].children())[0:4])
        # get stuff after blocks from pretrained efficient net
        tail = list(list(eff_net.children())[3:7])


        ######################################
        head = [nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3)]
        # body
        tail = [ConvLSTMCell(input_size=40, hidden_size=hidden_size)] # input = torch.Size([4, 40, 19, 44])
        tail2 = [nn.Linear(in_features = 836*hidden_size, out_features=opt["num_features"])]

        self.head = nn.Sequential(*head)
        self.body = nn.Sequential(*blocks)
        self.tail = nn.Sequential(*tail)
        self.tail2 = nn.Sequential(*tail2)

        
    def forward(self, x_prev_state):
        x = x_prev_state[0]
        prev_state = x_prev_state[1]
        out = self.head(x)
        out = self.body(out)
        lstm_out = self.tail((out, prev_state))
        out = lstm_out[1]
        out = torch.flatten(out, 1)
        out = self.tail2(out)

        # apply different activation functions to different outputs: https://discuss.pytorch.org/t/how-to-apply-different-activation-fuctions-to-different-neurons/13475
        movement_slice = out[:,0:6]
        mousex_slice = out[:,6:27]
        mousey_slice = out[:,27:48]
        Sigmoid = torch.nn.Sigmoid()
        Softmax = torch.nn.Softmax()
        tuple_of_activated_parts = (
            Sigmoid(movement_slice),
            Softmax(mousex_slice),
            Softmax(mousey_slice)
        )
        out = torch.cat(tuple_of_activated_parts, dim=1) # concatenate over feature dimension
        return lstm_out, out