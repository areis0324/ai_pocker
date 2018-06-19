import tensorflow as tf
import numpy as np
from irc_data import Provider
#pylint: disable=all

# set random seed
tf.set_random_seed(1)

# model path
MODEL_PATH = "./model/rnn.ckpt"

# hyperparameters
lr = 0.001                  # learning rate
training_iters = 100000     # train step
batch_size = 128

############################################
# roundName, raiseCount, betCount, winProbility(10)
#   0      ,    1/players , 2/players , 0.51
#   1      ,    2/players , 2/players , 0.58
#   0      ,    0        , 0      , 0.53
##############
n_inputs = 11                # holdem data input
                             # raiseCount, betCount, roundName, winProbility(10)

n_steps = 4                 # time steps: "Deal", "Flop", "Turn", "River"

n_hidden_units = 128        # neurons in hidden layer


n_gain = 2                  # [1,0]:win, [0,1]:lose

# x y placeholder
x = tf.placeholder(tf.float32, [None, n_steps, n_inputs])
y = tf.placeholder(tf.float32, [None, n_gain])

# weights biases definition
weights = {
    # shape (4, 128)
    'in': tf.Variable(tf.random_normal([n_inputs, n_hidden_units])),
    # shape (128, 1)
    'out': tf.Variable(tf.random_normal([n_hidden_units, n_gain]))
}
biases = {
    # shape (4, )
    'in': tf.Variable(tf.constant(0.1, shape=[n_hidden_units, ])),
    # shape (2, )
    'out': tf.Variable(tf.constant(0.1, shape=[n_gain, ]))
}

def RNN(X, weights, biases):
    ## Translate X from 3-d to 2-d ##
    # X ==> (128 batches * 4 steps, 4 inputs)
    # auto encode to 2 dimension
    X = tf.reshape(X, [-1, n_inputs])

    # X_in = W*X + b
    X_in = tf.matmul(X, weights['in']) + biases['in']
    # X_in ==> (128 batches, 4 steps, 128 hidden),
    # auto decode to 3 dimension
    X_in = tf.reshape(X_in, [-1, n_steps, n_hidden_units])

    # use basic LSTM Cell.
    lstm_cell = tf.contrib.rnn.BasicLSTMCell(n_hidden_units, forget_bias=1.0, state_is_tuple=True)
    # init state to zero
    init_state = lstm_cell.zero_state(batch_size, dtype=tf.float32)

    outputs, final_state = tf.nn.dynamic_rnn(lstm_cell, X_in, initial_state=init_state, time_major=False)

    results = tf.matmul(final_state[1], weights['out']) + biases['out']

    return results

pred = RNN(x, weights, biases)
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
train_op = tf.train.AdamOptimizer(lr).minimize(cost)

correct_pred = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

init = tf.global_variables_initializer()


# Add ops to save and restore all the variables.
saver = tf.train.Saver()

def train_model(sess):
    sess.run(init)
    step = 0
    for batch_xs, batch_ys in Provider.next_batch(batch_size):

        if step * batch_size > training_iters:
            save_path = saver.save(sess, MODEL_PATH)
            print("Model saved in path: %s" % save_path)
            return

        batch_xs = batch_xs.reshape([batch_size, n_steps, n_inputs])
        sess.run([train_op], feed_dict={
            x: batch_xs,
            y: batch_ys,
        })
        if step % 20 == 0:
            print(sess.run(accuracy, feed_dict={
            x: batch_xs,
            y: batch_ys,
        }))
        step += 1


def load_model(sess):
    sess.run(init)
    saver.restore(sess, MODEL_PATH)
    print("Model restored from file: %s" % MODEL_PATH)
    # train_model(sess)


def predict():
    with tf.Session() as sess:
        load_model(sess)
        #train_model(sess)

        for batch_xs, batch_ys in Provider.next_batch(1):
            extend_xs = np.zeros((batch_size, n_steps, n_inputs), dtype=batch_xs.dtype)
            extend_xs[0] = batch_xs
            batch_xs = extend_xs.reshape([batch_size, n_steps, n_inputs])

            print sess.run(pred, feed_dict={
                x: batch_xs
            })
            break


if __name__ == '__main__':
    try:
        with tf.Session() as sess:
            train_model(sess)
            #load_model(sess)
            # predict()
    except BaseException as err:
        print err
        raise
