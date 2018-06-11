# import matplotlib.pyplot as plt
import itertools
import numpy as np
#from sklearn.metrics import confusion_matrix

"""
https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
Red     #e6194b	(230, 25, 75)	(0, 100, 66, 0)
Green	#3cb44b	(60, 180, 75)	(75, 0, 100, 0)
Yellow	#ffe119	(255, 225, 25)	(0, 25, 95, 0)
Blue	#0082c8	(0, 130, 200)	(100, 35, 0, 0)
Orange	#f58231	(245, 130, 48)	(0, 60, 92, 0)
Purple	#911eb4	(145, 30, 180)	(35, 70, 0, 0)
Cyan	#46f0f0	(70, 240, 240)	(70, 0, 0, 0)
Magenta	#f032e6	(240, 50, 230)	(0, 100, 0, 0)
Lime	#d2f53c	(210, 245, 60)	(35, 0, 100, 0)
Pink	#fabebe	(250, 190, 190)	(0, 30, 15, 0)
Teal	#008080	(0, 128, 128)	(100, 0, 0, 50)
Lavender	#e6beff	(230, 190, 255)	(10, 25, 0, 0)
Brown	#aa6e28	(170, 110, 40)	(0, 35, 75, 33)
Beige	#fffac8	(255, 250, 200)	(5, 10, 30, 0)
Maroon	#800000	(128, 0, 0)	(0, 100, 100, 50)
Mint	#aaffc3	(170, 255, 195)	(33, 0, 23, 0)
Olive	#808000	(128, 128, 0)	(0, 0, 100, 50)
Coral	#ffd8b1	(255, 215, 180)	(0, 15, 30, 0)
Navy	#000080	(0, 0, 128)	(100, 100, 0, 50)
Grey	#808080	(128, 128, 128)	(0, 0, 0, 50)
White	#FFFFFF	(255, 255, 255)	(0, 0, 0, 0)
Black	#000000	(0, 0, 0)	(0, 0, 0, 100)
"""
COLORS = [(230, 25, 75),
          (60, 180, 75),
          (255, 225, 25),
          (0, 130, 200),
          (245, 130, 48),
          (145, 30, 180),
          (70, 240, 240),
          (240, 50, 230),
          (210, 245, 60),
          (250, 190, 190),
          (0, 128, 128),
          (230, 190, 255),
          (170, 110, 40),
          (255, 250, 200),
          (128, 0, 0),
          (170, 255, 195),
          (128, 128, 0),
          (255, 215, 180),
          (0, 0, 128),
          (128, 128, 128),
          (255, 255, 255),
          (0, 0, 0)
          ]


def get_color(index, normalized=False):
    if 0 <= index < len(COLORS):
        if normalized:
            return tuple(COLORS[index][0] / 255.0, COLORS[index][1] / 255.0, COLORS[index][2] / 255.0)
        else:
            return tuple(COLORS[index])
    else:
        return tuple(0, 0, 0)


def plot_confusion_matrix(f, y_true, y_pred, classes,
                          normalize=False,
                          title='Confusion matrix'):
    """
    :param f: output file
    :param y_true: true labels
    :param y_pred: predicted labels
    :param classes: list of class labels
    :param normalize: true => normalize value, false => no normalization
    :param title: (optional) title for graphic
    :param cmap: (optional) color map
    :return: None
    """
    print('')


def plot_accuracy(f, history, from_list=False, accuraccy='categorical_accuracy'):
    """
    :param f: output file
    :param history: list of accuracy from keras model
    :param from_list: true => history gives as list, false => history given from model.fit_generator
    :return:
    """
    print('')


def plot_loss(f, history, from_list=False):
    """
    :param f: output file
    :param history: list of loss from keras model
    :param from_list: true => history gives as list, false => history given from model.fit_generator
    :return: None
    """
    print("loss file: " + f)


def visualize_progress(val, max_val, description="", bar_width=20):
    """
    :param val: current progress value
    :param max_val: maximum value
    :param description: (optional) text which is displayed next to the progress bar
    :param bar_width: length of bar in the command line (number of chars)
    :return: string containing progress which can be printed to console
    """
    progress = int(val / max_val * bar_width)
    progress_bar = ['='] * (progress - 1) + ['>'] + ['.'] * (bar_width - progress)
    progress_bar = ''.join(progress_bar)
    return str(val + 1) + "/" + str(max_val) + ' [' + progress_bar + '] ' + description
