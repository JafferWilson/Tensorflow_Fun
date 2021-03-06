import numpy as np
from tensorflow.examples.tutorials.mnist import input_data
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

batch_size = 50
noise_size = 100
num_iter = 1000000

class generator:
    def __init__(self):
        #random projection
        self.w1 = tf.Variable(tf.truncated_normal(shape=[noise_size, 1024 * 4 * 4], stddev=np.sqrt(2.0 / noise_size)))
        self.b1 = tf.Variable(tf.zeros(1024 * 4 * 4, tf.float32))
        self.filter1 = tf.Variable(tf.truncated_normal(shape=[5, 5, 512, 1024], stddev=np.sqrt(2.0 / 1)))
        self.filterb1 = tf.Variable(tf.zeros(512, tf.float32))
        self.filter2 = tf.Variable(tf.truncated_normal(shape=[5, 5, 256, 512], stddev=np.sqrt(2.0 / 1)))
        self.filterb2 = tf.Variable(tf.zeros(256, tf.float32))
        self.filter3 = tf.Variable(tf.truncated_normal(shape=[5, 5, 1, 256], stddev=np.sqrt(2.0 / 1)))
        self.filterb3 = tf.Variable(tf.zeros(1, tf.float32))

    def outputs(self, z_holder):
        rand = tf.matmul(z_holder, self.w1) + self.b1
        conv0 = tf.reshape(rand, [-1, 4, 4, 1024])
        conv1 = tf.nn.conv2d_transpose(conv0, self.filter1, [batch_size, 8, 8, 512], [1, 2, 2, 1]) + self.filterb1
        o_conv1 = tf.nn.relu(conv1)

        conv2 = tf.nn.conv2d_transpose(o_conv1, self.filter2, [batch_size, 16, 16, 256], [1, 2, 2, 1]) + self.filterb2
        o_conv2 = tf.nn.relu(conv2)

        conv3 = tf.nn.conv2d_transpose(o_conv2, self.filter3, [batch_size, 28, 28, 1], [1, 2, 2, 1]) + self.filterb3
        o_conv3 = tf.sigmoid(conv3)
        return o_conv3

class discriminator:
    def __init__(self):
        self.l1_size = 200
        self.w1 = tf.Variable(tf.truncated_normal(shape=[784, self.l1_size], stddev=np.sqrt(2.0 / (784))))
        self.b1 = tf.Variable(tf.zeros([self.l1_size], tf.float32))
        self.w2 = tf.Variable(tf.truncated_normal(shape=[self.l1_size, 1], stddev=np.sqrt(2.0 / self.l1_size)))
        self.b2 = tf.Variable(tf.zeros([1], tf.float32))

    def outputs(self, x_holder):
        l1 = tf.nn.relu(tf.matmul(x_holder, self.w1) + self.b1)
        l2 = tf.nn.sigmoid(tf.matmul(l1, self.w2) + self.b2)
        return l2

def setup():
    z_holder = tf.placeholder(tf.float32, shape=[None, noise_size])
    x_holder = tf.placeholder(tf.float32, shape=[None, 784])

    gen, dis = generator(), discriminator()
    gen_out, dis_out = gen.outputs(z_holder), dis.outputs(x_holder)
    dis_gen_out = dis.outputs(gen_out)
    dis_loss = -tf.reduce_mean(tf.log(dis_out) + tf.log(1.0 - dis_gen_out))
    gen_loss = -tf.reduce_mean(tf.log(dis_gen_out))

    dis_opt = tf.train.AdamOptimizer(1e-4).minimize(dis_loss, var_list=[dis.w1, dis.b1, dis.w2, dis.b2])
    gen_opt = tf.train.AdamOptimizer(1e-4).minimize(gen_loss, var_list=[gen.w1, gen.b1, gen.w2, gen.b2])
    return (dis_opt, dis_loss, gen_opt, gen_loss, gen_out), z_holder, x_holder

def disp(img):
    plt.imshow(img.reshape(28, 28), cmap='Greys_r')
    plt.show()

def train_loop():
    mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
    runs, z_holder, x_holder = setup()
    print('model done')
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range(num_iter):
            x_batch, _ = mnist.train.next_batch(batch_size)
            z_rand = np.random.uniform(-1.0, 1.0, size=[batch_size, noise_size])
            _, dis_loss = sess.run(runs[:2], feed_dict={z_holder: z_rand, x_holder: x_batch})

            z_rand = np.random.uniform(-1.0, 1.0, size=[batch_size, noise_size])
            _, gen_loss, gen_out = sess.run(runs[2:], feed_dict={z_holder: z_rand})

            if i % 2500 == 0:
                print("Iter: {}".format(i))
                print("disloss: {}".format(dis_loss))
                print("genloss: {}".format(gen_loss))
                disp(gen_out[np.random.randint(0, batch_size)])

train_loop()