import os
import PIL.Image
import numpy as np

from keras.callbacks import TensorBoard, ModelCheckpoint, EarlyStopping
from keras.optimizers import Adam
from keras.utils import plot_model
from CustomCallbacks import TensorBoardImage, EncoderCheckpoint, HuffmanCallback

from CustomLoss import loss, code
from Generator import DataGenerator
from Model import build_model
from ModelConfig import img_input_shape, dataset_path, train_dir, validation_dir, test_dir,load_model


train_list = os.listdir(dataset_path+"/"+train_dir)
val_list = os.listdir(dataset_path+"/"+validation_dir)
test_list = os.listdir(dataset_path+"/"+test_dir)

train_ratio = 0.7
val_ratio = 0.2


train_generator = DataGenerator(dataset_path+"/"+train_dir,train_list,32,img_input_shape)
test_generator = DataGenerator(dataset_path+"/"+validation_dir,val_list,32,img_input_shape)

autoencoder = build_model()

# Plot model graph
plot_model(autoencoder, to_file='autoencoder.png')


if load_model:
    weight_path = "weights.hdf5"
    print("loading weights from {}".format(weight_path))
    autoencoder.load_weights(weight_path)

# TODO: Code loss !

# Compile model with adam optimizer
optimizer = Adam(lr=1e-4, clipnorm=1)
autoencoder.compile(optimizer=optimizer, loss={'clipping_layer_1':loss,'model_1':code})

# Get last log
log_index = None
run_list = os.listdir("./logs")
if len(run_list) == 0:
    log_index = 0
else:
    indexes = [run[-1] for run in run_list]
    log_index = str(int(max(indexes)) + 1)

tensorboard = TensorBoard(log_dir='./logs/run' + str(log_index), histogram_freq=0, batch_size=32)
early_stopping = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=20, verbose=0, mode='auto')
checkpoint = ModelCheckpoint("weights.hdf5", save_best_only=True)
encodercheckpoint = EncoderCheckpoint("encoder.hdf5", save_best_only=True)
tensorboard_image = TensorBoardImage("Reconstruction", test_list=test_list, logs_path='./logs/run' + str(log_index))
huffmancallback = HuffmanCallback(train_generator)


# Train model !
autoencoder.fit_generator(train_generator,
                          epochs=100,
                          validation_data=test_generator,
                          callbacks=[tensorboard_image, tensorboard, early_stopping, checkpoint,encodercheckpoint,huffmancallback])


