import os
import numpy as np
import pandas as pd
import dtlpy as dl
import matplotlib.pyplot as plt
from dtlpymetrics.tools.Evaluator import Evaluator
from dtlpymetrics.tools.utils import MethodAveragePrecision


def calc_precision_recall(dataset_id: str,
                          model_id: str,
                          metric: str,
                          metric_threshold=0.5,
                          method_type='every_point'):
    """
    Plot precision recall curve for a given metric threshold

    :param dataset_id: dataset ID
    :param model_id: model ID
    :param metric: name of the column in the scores dataframe to use as the metric
    :param metric_threshold: threshold for which to calculate TP/FP
    :param method_type: 'every_point' or 'eleven_point'
    :return:
    """
    if metric.lower() == 'iou':
        metric = 'geometry_score'
    elif metric.lower() == 'accuracy':
        metric = 'label_score'

    model_filename = f'{model_id}.csv'
    filters = dl.Filters(field='hidden', values=True)
    filters.add(field='name', values=model_filename)
    dataset = dl.datasets.get(dataset_id=dataset_id)
    items = list(dataset.items.list(filters=filters).all())
    if len(items) == 0:
        raise ValueError(f'No scores found for model ID {model_id}.')
    elif len(items) > 1:
        raise ValueError(f'Found {len(items)} items with name {model_id}.')
    else:
        scores_file = items[0].download()

    scores = pd.read_csv(scores_file)
    labels = dataset.labels
    label_names = [label.tag for label in labels]

    if metric not in scores.columns:
        raise ValueError(f'{metric} metric not included in scores.')

    #########################
    # plot precision/recall #
    #########################
    # calc
    if labels is None:
        labels = pd.concat([scores.first_label, scores.second_label]).dropna()

    plot_points = {'metric': metric,
                   'metric_threshold': metric_threshold,
                   'method_type': method_type,
                   'labels': {}}

    for label in list(set(label_names)):
        label_confidence_df = scores[scores.first_label == label].copy()

        label_confidence_df.sort_values('second_confidence', inplace=True, ascending=True)
        true_positives = label_confidence_df[metric] >= metric_threshold
        false_positives = label_confidence_df[metric] < metric_threshold
        #
        num_gts = sum(scores.first_id.notna())

        #
        acc_fps = np.cumsum(false_positives)
        acc_tps = np.cumsum(true_positives)
        recall = acc_tps / num_gts
        precision = np.divide(acc_tps, (acc_fps + acc_tps))

        # # Depending on the method, call the right implementation
        if method_type == 'every_point':
            [avg_precis, mpre, mrec, ii] = Evaluator.CalculateAveragePrecision(recall, precision)
        else:
            [avg_precis, mpre, mrec, _] = Evaluator.ElevenPointInterpolatedAP(recall, precision)

        plot_points['labels'].update({label: {
            'precision': mpre,
            'recall': mrec}})

    return plot_points


def calc_confusion_matrix(dataset_id,
                          model_id,
                          metric,
                          show_unmatched=False):
    """
    Calculate confusion matrix for a given model and metric
    :param dataset_id:
    :param model_id:
    :param metric:
    :param show_unmatched: display extra column showing which GT annotations were not matched
    :return:
    """
    if metric.lower() == 'iou':
        metric = 'geometry_score'
    elif metric.lower() == 'accuracy':
        metric = 'label_score'

    model_filename = f'{model_id}.csv'
    filters = dl.Filters(field='hidden', values=True)
    filters.add(field='name', values=model_filename)
    dataset = dl.datasets.get(dataset_id=dataset_id)
    items = list(dataset.items.list(filters=filters).all())
    if len(items) == 0:
        raise ValueError(f'No scores found for model ID {model_id}.')
    elif len(items) > 1:
        raise ValueError(f'Found {len(items)} items with name {model_id}.')
    else:
        scores_file = items[0].download()

    scores = pd.read_csv(scores_file)
    labels = dataset.labels
    label_names = [label.tag for label in labels]

    if metric not in scores.columns:
        raise ValueError(f'{metric} metric not included in scores.')

    #########################
    # plot precision/recall #
    #########################
    # calc
    if labels is None:
        labels = pd.concat([scores.first_label, scores.second_label]).dropna()

    scores_cleaned = scores.dropna().reset_index(drop=True)
    scores_labels = scores_cleaned[['first_label', 'second_label']]
    grouped_labels = scores_labels.groupby(['first_label', 'second_label']).size()

    conf_matrix = pd.DataFrame(index=label_names, columns=label_names, data=0)
    for label1, label2 in grouped_labels.index:
        # index/rows are the ground truth, cols are the predictions
        conf_matrix.loc[label1, label2] = grouped_labels.get((label1, label2), 0)

    return conf_matrix


def plot_precision_recall(plot_points, local_path=None):
    labels = list(plot_points['labels'].keys())

    plt.figure()
    plt.xlim(0, 1.1)
    plt.ylim(0, 1.1)

    for label in labels:
        plt.plot(plot_points['labels'][label]['recall'],
                 plot_points['labels'][label]['precision'],
                 label=[label])
    plt.legend()

    # plot_filename = f'precision_recall_{dataset_id}_{model_id}_{plot_points[metric]}_{metric_threshold}.png'
    plot_filename = f'precision_recall.png'
    if local_path is None:
        save_path = os.path.join(os.getcwd(), '.dataloop', plot_filename)
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        plt.savefig(save_path)
    else:
        save_path = os.path.join(local_path, plot_filename)
        plt.savefig(save_path)

    plt.close()

    return save_path


if __name__ == '__main__':
    dl.setenv('rc')

    dataset_id = '64731b043e2dd675c25cce88'  # big cats TEST evaluate
    model_id = '6473185c93bd97c6a30a47b9'  # resnet
    metric = 'accuracy'

    # plot_points = calc_precision_recall(dataset_id=dataset_id,
    #                                     model_id=model_id,
    #                                     metric=metric,
    #                                     metric_threshold=0.5,
    #                                     method_type='every_point')
    # plot_precision_recall(plot_points)
    conf_table = calc_confusion_matrix(dataset_id=dataset_id,
                                       model_id=model_id,
                                       metric=metric)
    print("columns are model predictions, rows are ground truth labels")
    print(conf_table)
    print()
