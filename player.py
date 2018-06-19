import numpy as np
import tensorflow as tf
from tensorflow.python.tools.inspect_checkpoint import print_tensors_in_checkpoint_file

print_tensors_in_checkpoint_file("./model/rnn.ckpt", None, True)

# W = tf.Variable(np.arange(512).reshape((4, 128)), dtype=tf.float32, name="weights")
# b = tf.Variable(np.arange(128).reshape((128, 1)), dtype=tf.float32, name="biases")


# print W, b

# Add ops to save and restore all the variables.
saver = tf.train.Saver()

# # Later, launch the model, use the saver to restore variables from disk, and
# # do some work with the model.
with tf.Session() as sess:
    # Restore variables from disk.
    saver.restore(sess, "./model/rnn.ckpt")
    # print("weights:", sess.run(W))
    # print("biases:", sess.run(b))
