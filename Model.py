from itertools import count
from keras.layers import Input, Conv2D, Add, LeakyReLU, Lambda, Multiply, Reshape
from keras.models import Model
from CustomLayers import ClippingLayer, RoundingLayer, MeanLayer, StdLayer, MirrorPaddingLayer, MultiplyLayer, NormalizeLayer
from ModelConfig import *
from utils import subpixel


def encoder(e_input):

    # Counters
    conv_index = count(start=1)
    leaky_index = count(start=1)
    add_index = count(start=1)

    e_mean = MeanLayer()(e_input)
    e_std = StdLayer()(e_input)

    e = NormalizeLayer()([e_input,e_mean,e_std])
    e = MirrorPaddingLayer()(e_input)

    e = Conv2D(filters=64, kernel_size=(5, 5), padding='valid', strides=(2, 2), name=f"e_conv_{next(conv_index)}")(e)
    e = LeakyReLU(alpha=a, name=f"e_leaky_{next(leaky_index)}")(e)
    e = Conv2D(filters=128, kernel_size=(5, 5), padding='valid', strides=(2, 2), name=f"e_conv_{next(conv_index)}")(e)
    e = LeakyReLU(alpha=a, name=f"e_leaky_{next(leaky_index)}")(e)

    e_skip_connection = e

    # Create three residual blocks
    for i in range(3):
        e = Conv2D(name=f"e_conv_{next(conv_index)}", **e_res_block_conv_params)(e)
        e = LeakyReLU(alpha=a, name=f"e_leaky_{next(leaky_index)}")(e)
        e = Conv2D(name=f"e_conv_{next(conv_index)}", **e_res_block_conv_params)(e)
        e = Add(name=f"e_add_{next(add_index)}")([e, e_skip_connection])
        e_skip_connection = e

    e = Conv2D(filters=96, kernel_size=(5, 5), padding='valid', strides=(2, 2), name=f"e_conv_{next(conv_index)}")(e)
    #e = RoundingLayer()(e)

    return [e,e_mean,e_std]

def decoder(encoded_list, mask):
    # Counters
    conv_index = count(start=1)
    lambda_index = count(start=1)
    leaky_index = count(start=1)
    add_index = count(start=1)

    #d = Multiply()([encoded,mask])
    d = Conv2D(filters=512, kernel_size=(3, 3), padding='same', strides=(1, 1), name=f"d_conv_{next(conv_index)}")(encoded_list[0])
    d = Lambda(function=subpixel, name=f"d_lambda_{next(lambda_index)}")(d)

    d_skip_connection = d

    # Add three residual blocks
    for j in range(3):
        d = Conv2D(name=f"d_conv_{next(conv_index)}", **d_res_block_conv_params)(d)
        d = LeakyReLU(alpha=a, name=f"d_leaky_{next(leaky_index)}")(d)
        d = Conv2D(name=f"d_conv_{next(conv_index)}", **d_res_block_conv_params)(d)
        d = Add(name=f"d_add_{next(add_index)}")([d, d_skip_connection])
        d_skip_connection = d

    d = Conv2D(filters=256, kernel_size=(3, 3), padding='same', strides=(1, 1), name=f"d_conv_{next(conv_index)}")(d)
    d = Lambda(function=subpixel, name=f"d_lambda_{next(lambda_index)}")(d)

    d = Conv2D(filters=12, kernel_size=(3, 3), padding='same', strides=(1, 1), name=f"d_conv_{next(conv_index)}")(d)
    d = Lambda(function=subpixel, name=f"d_lambda_{next(lambda_index)}")(d)


    # Denormalize
    d = MultiplyLayer()([encoded_list[1],d])

    d = Add()([d,encoded_list[2]])

    #d = ClippingLayer()(d)

    return d

def build_model():
    e_input = Input(shape=img_input_shape, name="e_input_1")
    mask = Input(shape=(img_input_shape[0]//8,img_input_shape[1]//8,96,), name="d_input_mask")
    return Model([e_input,mask],decoder(encoder(e_input), mask))