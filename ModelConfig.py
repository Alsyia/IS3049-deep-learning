# Encoder
a = 0.3 # Leaky ReLu alpha value
img_input_shape = (32, 32, 3)  # Encoder input shape (32, 32, 3) for CIFAR
e_input_shape = (32+24, 32+24, 3)  # Encoder input shape (32, 32, 3) for CIFAR
e_res_block_conv_params = {  # Parameters of residual blocks
    "filters": 128,
    "kernel_size": (3, 3),
    "padding": "same",
}

# Decoder
# d_input_shape = (178, 178, 3)  # will be round output_shape
d_res_block_conv_params = {  # Parameters of residual blocks
    "filters": 128,
    "kernel_size": (3, 3),
    "padding": "same",
}

# Loss
loss_params = {
    "beta": 1
}