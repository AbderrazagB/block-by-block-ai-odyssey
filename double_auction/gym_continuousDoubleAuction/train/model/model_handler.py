from ray.rllib.models.torch.torch_modelv2 import TorchModelV2
from ray.rllib.models.torch.fcnet import FullyConnectedNetwork as TorchFCNet
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.utils.annotations import override

torch, nn = try_import_torch()

class CustomModel_1(TorchModelV2, nn.Module):
    """
    Custom PyTorch model - Updated to use TorchModelV2.
    
    This model uses fully connected layers for processing.
    Updated for modern Ray RLlib API with PyTorch backend.
    """

    def __init__(self, obs_space, action_space, num_outputs, model_config, name):
        TorchModelV2.__init__(self, obs_space, action_space, num_outputs, model_config, name)
        nn.Module.__init__(self)
        
        self.hidden_size = 512
        
        # Build the base fully connected network
        self.base_model = TorchFCNet(
            obs_space,
            action_space,
            num_outputs,
            model_config,
            name=name + "_fc"
        )
    
    @override(TorchModelV2)
    def forward(self, input_dict, state, seq_lens):
        """
        Forward pass through the model.
        
        Args:
            input_dict: Dictionary of input tensors, including "obs"
            state: List of state tensors (for recurrent models)
            seq_lens: Tensor of sequence lengths
            
        Returns:
            (outputs, state): The model output and new state
        """
        # Use the base model
        model_out, _ = self.base_model(input_dict, state, seq_lens)
        return model_out, []
    
    @override(TorchModelV2)
    def value_function(self):
        """Returns the value function output for the most recent forward pass."""
        return self.base_model.value_function()
