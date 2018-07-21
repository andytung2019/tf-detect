# tf-detect
my own detection
1.  download tf-detect
2.  cd lib , make clean , make 
     python setup.py install

    cd lib/datasets/coco
    make install

3. train
cd tf-detect/tools/ 
python trainval_net.py --net res101 --imdb carcar_2018_train --imdbval carcar_2018_val --weight res101 --iters=40000

4. output:
    tf-detect/output/default/carcar_2018_train/default/
     checkpoint
     res101_faster_rcnn_iter_10000.pkl
     res101_faster_rcnn_iter_10000.ckpt.index
     res101_faster_rcnn_iter_10000.ckpt.meta
     res101_faster_rcnn_iter_10000.ckpt.data-00000-of-00001

5.test the new trained net
    saver = tf.train.Saver()
    saver.restore(sess, tfmodel) #tfmodel is the trained model file dir

 
