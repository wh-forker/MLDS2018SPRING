import os
import argparse
import numpy as np
import tensorflow as tf

from model.basic_model import small_model


def main(args):
    # parameters
    batch_size = 512
    epochs = 50
    learning_rate = 1e-4

    # Fix random seed for reproducibility.
    seed = 416
    np.random.seed(seed)
    print("Fixed random seed for reproducibility.")

    # target function sin(5x*pi) / 5x*pi
    X_train = np.linspace(0.0001, 1.0, num=10000)[:, np.newaxis]
    np.random.shuffle(X_train)
    y_train = np.sinc(5 * X_train)

    # # visulization target function
    # plt.scatter(x=X_train, y=y_train, c="r", s=5, marker="o", alpha=0.1, label=r"$\mathrm{sin}(5 \pi x)/5x$")
    # plt.legend()
    # plt.show()
    mes_loss_times = []
    min_ratio_times = []
    for idx in range(100):

        tf.reset_default_graph()
        with tf.name_scope("Inputs"):
            X_placeholder = tf.placeholder(tf.float32, [None, 1])
            Y_placeholder = tf.placeholder(tf.float32, [None, 1])

        predict = small_model(X_placeholder)

        with tf.name_scope("mean_square_error"):
            mse_loss = tf.reduce_mean(tf.square(predict - Y_placeholder))
            tf.summary.scalar("Loss", mse_loss) # In tensorboard event

        with tf.name_scope("train"):
            train_step = tf.train.AdamOptimizer(learning_rate).minimize(mse_loss)

        # min grads norm
        grads_norm = tf.constant(0, dtype=tf.float32)
        for v in tf.trainable_variables():
            [grads] = tf.gradients(ys=mse_loss, xs=v)
            grads_norm += tf.reduce_sum(grads**2)
        grads_norm = tf.sqrt(grads_norm)
        grads_train_step = tf.train.AdadeltaOptimizer(learning_rate=5e-3).minimize(grads_norm)

        # train
        with tf.Session() as sess:
            # Merge all the summaries and write them out to ./logs/Tensorboard/train/
            merged = tf.summary.merge_all()
            train_writer = tf.summary.FileWriter(os.path.join(args.LOG_DIR_PATH, "Grad_zeros{}".format(idx), "Tensorboard/train/"), sess.graph)

            sess.run(tf.global_variables_initializer())
            nbrof_batch = int(len(X_train)/batch_size)

            for e in range(epochs):
                for step in range(nbrof_batch):
                    batch_x, batch_y = X_train[step * batch_size: (step+1) * batch_size], y_train[step * batch_size: (step+1)* batch_size]

                    feed_dict = {X_placeholder: batch_x, Y_placeholder: batch_y}
                    _, summary, mse_loss_ = sess.run([train_step, merged, mse_loss], feed_dict=feed_dict)
                    train_writer.add_summary(summary, e)

                    if (e*nbrof_batch) + step %10 == 0:
                        print("epochs:{}, steps:{}, loss={}".format(e, (e*nbrof_batch) + step, mse_loss_))
            mes_loss_times.append(mse_loss_)

            while True:
                _, grads_norm_ = sess.run([grads_train_step, grads_norm], feed_dict=feed_dict)
                print("grads norm:{}".format(grads_norm_))

                if grads_norm_ <= 5e-3: #5e-3
                    break
            
            # calculate positive eigen value ratio
            eigen_values = np.asarray([])
            for v in tf.trainable_variables():
                # v_flat = tf.squeeze(v)
                [hess] = sess.run(tf.hessians(mse_loss, v), feed_dict=feed_dict) # FIXME: hess not sys matric
                hess_shape = [int(np.sqrt(np.prod(hess.shape))), int(np.sqrt(np.prod(hess.shape)))]
                eigen_values = np.append(eigen_values, (np.linalg.eigvals(hess.reshape(hess_shape))))
        
            minimal_ratio = np.sum(eigen_values > 0) / len(eigen_values)
            min_ratio_times.append(minimal_ratio)

            # save model
            saver = tf.train.Saver()
            save_model_dir_path = os.path.join(args.SAVE_MODLE_DIR_PATH, "Grad_zeros{}".format(idx), "model")
            if not os.path.exists(os.path.dirname(save_model_dir_path)):
                os.makedirs(os.path.dirname(save_model_dir_path))
            save_path = saver.save(sess, save_model_dir_path)
            print("Save model to path: {}".format(os.path.dirname(save_model_dir_path)))


        # save loss process
        mes_loss_list = np.asarray(mes_loss_times)
        loss_save_path = os.path.join(args.LOG_DIR_PATH, "Grad_zeros", "loss.npy")
        if not os.path.exists(os.path.dirname(loss_save_path)):
            os.makedirs(os.path.dirname(loss_save_path))
        np.save(loss_save_path, mes_loss_list)
        print("Loss process to path: ", loss_save_path)

        # save minimal ratio process
        min_ratio_list = np.asarray(min_ratio_times)
        min_ratio_save_path = os.path.join(args.LOG_DIR_PATH, "Grad_zeros", "min_ratio.npy")
        if not os.path.exists(os.path.dirname(min_ratio_save_path)):
            os.makedirs(os.path.dirname(min_ratio_save_path))
        np.save(min_ratio_save_path, min_ratio_list)
        print("Minimal ratio process to path: ", min_ratio_save_path)

if __name__ == "__main__":
    PROJECT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR_PATH = os.path.join(PROJECT_DIR_PATH, "logs")
    SAVE_MODLE_DIR_PATH = os.path.join(PROJECT_DIR_PATH, "save_models")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--LOG_DIR_PATH",
        type=str,
        default=LOG_DIR_PATH,
        help=""
    )
    parser.add_argument(
        "--SAVE_MODLE_DIR_PATH",
        type=str,
        default=SAVE_MODLE_DIR_PATH,
        help=""
    )
    main(parser.parse_args())