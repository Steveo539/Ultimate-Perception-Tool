import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from collections import OrderedDict

dummy_multiple_choice_data = {
    'title': 'Why do you hate your manager?',
    'type': 'multiple_choice',
    'optionList': OrderedDict({'He is ugly': 10, 'His breath smells bad': 20, 'He does not take showers': 30}),
}

dummy_rating_choice_data = {
    'question_title': 'What out of 10 do you rate your manager?',
    'question_type': 'rating',
    'rating_choice_range': (0, 10), # rating range from 0 to 10
    'results': [5]*10
}


def generate_multiple_choice(data, save=False):
    x_axis = data['optionList'].keys()
    y_pos = np.arange(len(x_axis))
    plt.bar(y_pos, list(data['optionList'].values()), align='center', alpha=0.5)
    plt.xticks(y_pos, x_axis)
    plt.ylabel('# (frequency)')
    plt.xlabel('(choice)')
    plt.title(data['title'])
    matplotlib.rc('xtick', labelsize=20)
    matplotlib.rc('ytick', labelsize=20)
    if (save):
        return plt.savefig('books_read.png')
    #plt.show()

#generate_multiple_choice(dummy_multiple_choice_data)