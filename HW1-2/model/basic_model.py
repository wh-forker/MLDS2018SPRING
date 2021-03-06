import tensorflow as tf


def small_model(X_placeholder):

    dense = tf.layers.dense(inputs=X_placeholder, units=10
                            , kernel_initializer=tf.truncated_normal_initializer(stddev=0.01)
                            , activation=tf.nn.relu
                            , name="dense1")

    dense = tf.layers.dense(inputs=dense, units=4
                            , kernel_initializer=tf.truncated_normal_initializer(stddev=0.01)
                            , activation=tf.nn.relu
                            , name="dense2")

    output = tf.layers.dense(inputs=dense, units=1
                            , kernel_initializer=tf.truncated_normal_initializer(stddev=0.01)
                            , name="output")

    return output


def dnn_medium_model(X_placeholder):

    dense = tf.layers.dense(inputs=X_placeholder, units=64
                            , kernel_initializer=tf.truncated_normal_initializer(stddev=0.01)
                            , activation=tf.nn.relu
                            , name="dense1")

    dense = tf.layers.dense(inputs=dense, units=64
                            , kernel_initializer=tf.truncated_normal_initializer(stddev=0.01)
                            , activation=tf.nn.relu
                            , name="dense2")

    dense = tf.layers.dense(inputs=dense, units=64
                            , kernel_initializer=tf.truncated_normal_initializer(stddev=0.01)
                            , activation=tf.nn.relu
                            , name="dense3")

    output = tf.layers.dense(inputs=dense, units=10
                            , kernel_initializer=tf.truncated_normal_initializer(stddev=0.01)
                            , activation=tf.nn.softmax
                            , name="output")
    
    return output

