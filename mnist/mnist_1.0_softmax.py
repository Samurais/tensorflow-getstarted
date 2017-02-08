# encoding: UTF-8
# Copyright 2016 Google.com
# https://github.com/martin-gorner/tensorflow-mnist-tutorial
#
# Modifications copyright (C) 2017 Hai Liang Wang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import tensorflow as tf
from utils import gen_model_save_dir
from tensorflow.contrib.learn.python.learn.datasets.mnist import read_data_sets
tf.set_random_seed(0)

# neural network with 1 layer of 10 softmax neurons
#
# · · · · · · · · · ·       (input data, flattened pixels)       X [batch, 784]        # 784 = 28 * 28
# \x/x\x/x\x/x\x/x\x/    -- fully connected layer (softmax)      W [784, 10]     b[10]
#   · · · · · · · ·                                              Y [batch, 10]

# The model is:
#
# Y = softmax( X * W + b)
#              X: matrix for 100 grayscale images of 28x28 pixels, flattened (there are 100 images in a mini-batch)
#              W: weight matrix with 784 lines and 10 columns
#              b: bias vector with 10 dimensions
#              +: add with broadcasting: adds the vector to each line of the matrix (numpy)
#              softmax(matrix) applies softmax on each line
#              softmax(line) applies an exp to each value then divides by the norm of the resulting line
#              Y: output matrix with 100 lines and 10 columns

# Download images and labels into mnist.test (10K images+labels) and
# mnist.train (60K images+labels)
mnist = read_data_sets("MNIST_data", one_hot=True,
                       reshape=False, validation_size=0)

# input X: 28x28 grayscale images, the first dimension (None) will index
# the images in the mini-batch
X = tf.placeholder(tf.float32, [None, 28, 28, 1])
# correct answers will go here
Y_ = tf.placeholder(tf.float32, [None, 10])
# weights W[784, 10]   784=28*28
W = tf.Variable(tf.zeros([784, 10]))
# biases b[10]
b = tf.Variable(tf.zeros([10]))

# flatten the images into a single line of pixels
# -1 in the shape definition means "the only possible dimension that will preserve the number of elements"
XX = tf.reshape(X, [-1, 784])

# The model
Y = tf.nn.softmax(tf.matmul(XX, W) + b)

# loss function: cross-entropy = - sum( Y_i * log(Yi) )
#                           Y: the computed output vector
#                           Y_: the desired output vector

# cross-entropy
# log takes the log of each element, * multiplies the tensors element by element
# reduce_mean will add all the components in the tensor
# so here we end up with the total cross-entropy for all images in the batch
# normalized for batches of 100 images,
cross_entropy = -tf.reduce_mean(Y_ * tf.log(Y)) * 1000.0
tf.scalar_summary('loss', cross_entropy)  # Keep track of the cost
# *10 because  "mean" included an unwanted division by 10

# accuracy of the trained model, between 0 (worst) and 1 (best)
correct_prediction = tf.equal(tf.argmax(Y, 1), tf.argmax(Y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
tf.scalar_summary('accuracy', accuracy)  # Keep track of the accuracy

# training, learning rate = 0.005
train_step = tf.train.GradientDescentOptimizer(0.005).minimize(cross_entropy)

# init
model_save_dir = gen_model_save_dir(prefix='1_softmax')
tf_writer = tf.train.SummaryWriter(model_save_dir)
tf_saver = tf.train.Saver(max_to_keep=200)  # Arbitrary limit
init = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init)

merged_summaries = tf.merge_all_summaries()
tf_writer.add_graph(sess.graph)


def run(i, update_test_data, update_train_data):
    '''
    You can call this function in a loop to train the model, 100 images at a time
    '''
    # training on batches of 100 images with 100 labels
    batch_X, batch_Y = mnist.train.next_batch(100)

    # compute training values
    if update_train_data:
        a, c, s = sess.run([accuracy, cross_entropy, merged_summaries], feed_dict={
                           X: batch_X, Y_: batch_Y})
        tf_writer.add_summary(s, i)
        print(str(i) + ": accuracy:" + str(a) + " loss: " + str(c))

    # compute test value
    if update_test_data:
        a, c = sess.run([accuracy, cross_entropy], feed_dict={
                        X: mnist.test.images, Y_: mnist.test.labels})
        print(str(i) +
              ": ********* epoch " +
              str(i *
                  100 //
                  mnist.train.images.shape[0] +
                  1) +
              " ********* test accuracy:" +
              str(a) +
              " test loss: " +
              str(c))

    # the backpropagation training step
    sess.run(train_step, feed_dict={X: batch_X, Y_: batch_Y})


def main():
    for k in range(2000):
        run(k + 1, True, True)
    tf_saver.save(sess, '%s/model.ckpt' % model_save_dir)

if __name__ == '__main__':
    main()
